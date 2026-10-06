from typing import Any, List

from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select

from src.db.main import get_session
from src.db.model import User
from src.db.redis import token_in_blocklist
from src.auth.utils import decode_token
from src.core.exceptions import UnAuthorizedException
from src.auth.service import UserService


user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request:Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        if creds is None:
            raise UnAuthorizedException(
                message="Authentication required."
            )

        token = creds.credentials
        
        token_data = decode_token(token)

        if not self.token_valid(token):
            raise UnAuthorizedException(
                message="Invalid or expired token."
            )

        if await token_in_blocklist(token_data["jti"]):
            raise UnAuthorizedException(
                message="Invalid or expired token."
            )

        self.verify_token_data(token_data)
        return token_data

    def token_valid(self, token:str) -> bool:
        token_data = decode_token(token)
        return token_data is not None

    def verify_token_data(self, token_data:dict):        
        raise NotImplementedError("Please override this method in child classes.")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if not token_data and token_data["refresh"]:
            raise UnAuthorizedException(
                message="Access token required."
            )


async def get_current_user(
        token_details: dict = Depends(AccessTokenBearer()),
        session: AsyncSession = Depends(get_session),
):
    user_email = token_details["user"]["email"]
    user = await user_service.get_user_by_email(user_email, session)    

    if not user:
        raise UnAuthorizedException(
            message="Invalid email or password"
        )
    
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if not current_user.is_verified:
            raise UnAuthorizedException(
                message="Account is not verified yet.",
                details="Check your email and verify your account."
            )
        if current_user.role in self.allowed_roles:
            return True
        raise UnAuthorizedException(
            message="You do not have enough permission to do this perform."
        )