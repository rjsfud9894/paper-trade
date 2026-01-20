import bcrypt
import jwt
import os
from datetime import datetime
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")


class AuthService:
    
    @staticmethod
    def hash_password(password: str) -> str:
        """비밀번호를 암호화해서 반환"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """비밀번호가 맞는지 확인"""
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed.encode("utf-8")
        )
    
    @staticmethod
    def create_token(user_id: int) -> str:
        """JWT 토큰 생성"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
