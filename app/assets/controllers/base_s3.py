from abc import abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiobotocore.client import AioBaseClient
from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class S3:
    dsn: str
    region: str
    username: str
    password: str


@dataclass
class S3Controller:
    s3: S3

    @abstractmethod
    def bucket(self) -> str: pass

    async def add(
            self,
            name: str,
            content: bytes
    ) -> None:
        async with self._get_client() as client:
            await client.put_object(Bucket=self.bucket(), Key=name, Body=content)

    async def get(
            self,
            name: str
    ) -> bytes | None:
        async with self._get_client() as client:
            try:
                result: bytes = await client.get_object(Bucket=self.bucket(), Key=name)
            except ClientError:
                return

        return result

    async def delete(
            self,
            name: str
    ) -> None:
        async with self._get_client() as client:
            await client.delete_object(Bucket=self.bucket(), Key=name)

    @asynccontextmanager
    async def _get_client(self) -> AsyncGenerator[AioBaseClient, None]:
        session = get_session()
        async with session.create_client(
                "s3",
                endpoint_url=self.s3.dsn,
                region_name=self.s3.region,
                aws_access_key_id=self.s3.username,
                aws_secret_access_key=self.s3.password,
        ) as client:
            yield client
