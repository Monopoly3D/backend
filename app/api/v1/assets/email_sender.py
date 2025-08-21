from fastapi import BackgroundTasks
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from pydantic import EmailStr

from app.api.v1.enums.email_name import EmailName


class EmailSender:
    with open("app/api/v1/templates/verification_email_template.txt", "r", encoding="utf-8") as file:
        _verification_email_template: str = file.read()

    def __init__(
            self,
            email_name: str,
            email_password: str,
            smtp_server: str,
            smtp_port: int
    ) -> None:
        self._email_name = email_name
        self._email_password = email_password
        self._smtp_server = smtp_server
        self._smtp_port = smtp_port

    async def send_verification_email(
            self,
            *recipients: EmailStr | str,
            verification_url: str,
            background_tasks: BackgroundTasks | None = None
    ) -> None:
        await self._send_email(
            EmailName.NO_REPLY,
            self._create_verification_message(
                *recipients,
                verification_url=verification_url
            ),
            background_tasks=background_tasks
        )

    async def _send_email(
            self,
            email_name: str,
            message: MessageSchema,
            *,
            background_tasks: BackgroundTasks | None = None
    ) -> None:
        email_name: str = self._email_name.format(email_name=email_name)

        mail = FastMail(
            ConnectionConfig(
                MAIL_USERNAME=email_name,
                MAIL_PASSWORD=self._email_password,
                MAIL_FROM=email_name,
                MAIL_SERVER=self._smtp_server,
                MAIL_PORT=self._smtp_port,
                MAIL_SSL_TLS=True,
                MAIL_STARTTLS=False,
                USE_CREDENTIALS=True,
                VALIDATE_CERTS=True
            )
        )

        if background_tasks is None:
            await mail.send_message(message)
        else:
            background_tasks.add_task(
                mail.send_message,
                message=message,
                template_name=None,
                html_template=None,
                plain_template=None
            )

    @classmethod
    def _create_verification_message(
            cls,
            *recipients: EmailStr | str,
            verification_url: str
    ) -> MessageSchema:
        return cls._create_message(
            *recipients,
            subject="Verify your Monopoly3D account",
            content=cls._verification_email_template.format(verification_url=verification_url)
        )

    @staticmethod
    def _create_message(
            *recipients: EmailStr | str,
            subject: str,
            content: str
    ) -> MessageSchema:
        return MessageSchema(
            subject=subject,
            recipients=list(recipients),
            body=content,
            subtype=MessageType.html
        )
