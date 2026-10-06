import uuid
import jwt
from datetime import datetime, timedelta, timezone
from typing import Any
from pwdlib import PasswordHash
from src.core.config import Config
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from src.core.exceptions import UnAuthorizedException


pwd_context = PasswordHash.recommended()

ACCESS_TOKEN_EXPIRY = 3600

def hash_password(password:str) -> str:
    hash = pwd_context.hash(password)
    return hash

def verify_password(password: str, hash: str) -> bool:
    return pwd_context.verify(password, hash)


def create_access_token(user_data: dict, expiry: timedelta=None, refresh: bool = False) -> str:
    payload = {}

    payload["user"] = user_data
    payload["exp"] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
    payload["jti"] = str(uuid.uuid4)
    payload["refresh"] = refresh

    token = jwt.encode(payload, key=Config.JWT_SECRETE_KEY, algorithm=Config.JWT_ALGORITHM)

    return token


def decode_token(token:str) -> dict:
    try:
        token_data = jwt.decode(jwt=token, key=Config.JWT_SECRETE_KEY, algorithms=Config.JWT_ALGORITHM)

    except jwt.ExpiredSignatureError:
        raise UnAuthorizedException(
             message="Invalid or expired token."
        )
    
    except jwt.InvalidTokenError:
        raise UnAuthorizedException(
             message="Invalid or expired token."
        )

    except jwt.PyJWTError:
        raise UnAuthorizedException(
            message="Invalid or expired token."
        )
    
    # if not token_data.get('sub'):
    #     raise UnAuthorizedException(
    #         message="Invalid authentication token or token required."
    #     )
    
    return token_data

serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRETE_KEY, salt="email-configuration"
)


def create_url_safe_token(data: dict):
    token = serializer.dumps(data)
    return token


def decode_url_safe_token(token: str) -> dict[str, Any]:
    try:
        token_data = serializer.loads(token, max_age= 60 * 60 * 24)

        if not token_data:
            raise UnAuthorizedException(
                message="Invalid verification token."
            )
        return token_data

    except SignatureExpired:
        raise UnAuthorizedException(
            message="Verification link has expired."
        )

    except BadSignature:
        raise UnAuthorizedException(
            message="Invalid verification token"
        )