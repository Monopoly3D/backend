from typing import Any, Dict
from uuid import UUID

from app.api.v1.controllers.redis import RedisController
from app.assets.objects.redis import RedisObject


class User(RedisObject):
    def __init__(
            self,
            user_id: UUID,
            *,
            username: str,
            controller: RedisController
    ) -> None:
        self.user_id = user_id
        self.username = username

        super().__init__(controller.REDIS_KEY.format(user_id=user_id), controller)

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": str(self.user_id),
            "username": self.username
        }
