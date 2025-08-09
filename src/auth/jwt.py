import os
from datetime import timedelta, datetime

from jose import jwt

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')

class JWTManager:
    @staticmethod
    def create_access_token(
            data: dict
    ) -> str:
        """
        Create a JWT access token with the given data and expiration time.
        """
        to_encode = data.copy()
        expire = datetime.now() + timedelta(minutes=600)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> int:
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM]
            )
            return payload.get("sub")
        except Exception as e:
            print(f"JWT Error: {e}")
            raise ValueError("Invalid token")
