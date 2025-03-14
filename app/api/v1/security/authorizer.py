from typing import Dict, List, Annotated

from fastapi import Depends
from yaml import load, Loader

from app.api.v1.enums.permission import Permission
from app.api.v1.exceptions.http.no_permission import NoPermissionError
from app.api.v1.security.authenticator import Authenticator
from app.database.models import Role


class Authorizer:
    with open("app/api/v1/security/permissions.yaml", "r", encoding="utf-8") as file:
        permissions_file: Dict[str, List[str]] = load(file.read(), Loader=Loader)

    roles_permissions: Dict[Role, List[Permission]] = {
        Role(role): [Permission(permission) for permission in permissions]
        for role, permissions in permissions_file.items()
    }

    @staticmethod
    def has_permission(permission: Permission) -> Depends:
        async def __has_permission(roles: Annotated[List[Role], Authenticator.get_roles()]) -> None:
            if Role.ADMIN in roles:
                return

            for role in roles:
                if permission in Authorizer.roles_permissions.get(role):
                    return

            raise NoPermissionError("You don't have permission to perform this action")

        return Depends(__has_permission)

    @staticmethod
    def has_any_permission(*permissions: Permission) -> Depends:
        async def __has_any_permission(roles: Annotated[List[Role], Authenticator.get_roles()]) -> None:
            if Role.ADMIN in roles:
                return

            for role in roles:
                for permission in permissions:
                    if permission in Authorizer.roles_permissions.get(role):
                        return

            raise NoPermissionError("You don't have permission to perform this action")

        return Depends(__has_any_permission)
