from fastapi_mail import MessageSchema, MessageType
from pydantic import EmailStr

with open("app/api/v1/templates/verification_email_template.txt", "r", encoding="utf-8") as file:
    _verification_email_template: str = file.read()


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


class EmailCreator:
    @staticmethod
    def create_verification_message(
            *recipients: EmailStr | str,
            verification_url: str
    ) -> MessageSchema:
        return _create_message(
            *recipients,
            subject="Verify your Monopoly3D account",
            content=_verification_email_template.format(verification_url=verification_url)
        )
