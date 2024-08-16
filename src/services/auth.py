from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import NoResultFound
from jose import jwt, JWTError

import bcrypt
from src.models import DatabaseSession
from src.config import Config
from src.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class AuthService:
    @staticmethod
    def make_hashed_password(password: str):
        pwhash = bcrypt.hashpw(
            password=password.encode("utf-8"),
            salt=bcrypt.gensalt()
        )

        return pwhash.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str):
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        except Exception as E:
            print(E)
            return False

    @staticmethod
    def get_user_by_email(email: str) -> User.__pydantic_model__ or None:
        user = None
        with DatabaseSession().withSession() as session:
            try:
                user_model = session.query(User).where(
                    User.email == email).one()
                user = User.__pydantic_model__.from_orm(user_model)
            except NoResultFound:
                pass
        return user

    @staticmethod
    def get_user_by_id(id: int) -> User.__pydantic_model__ or None:
        user = None
        with DatabaseSession().withSession() as session:
            try:
                user_model = session.query(User).where(
                    User.id == id).one()
                user = User.__pydantic_model__.from_orm(user_model)
            except NoResultFound:
                pass
        return user

    @staticmethod
    def authenticate_user(email: str, password: str):
        user = AuthService.get_user_by_email(email)

        if not user:
            return False

        if not AuthService.verify_password(password, user.password):
            return False
        return user

    @staticmethod
    def create_access_token(user):
        data = {
            "id": user.id,
            "email": user.email,
            "type": "access"
        }
        to_encode = data.copy()
        expire = datetime.now(
            timezone.utc) + timedelta(
                minutes=Config.ACCESS_TOKEN_EXPIRATION_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(user):
        data = {
            "id": user.id,
            "email": user.email,
            "type": "refresh"
        }
        to_encode = data.copy()
        expire = datetime.now(
            timezone.utc) + timedelta(
                days=Config.REFRESH_TOKEN_EXPIRATION_DAYS
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_auth_tokens(user):
        access_token = AuthService.create_access_token(user)
        refresh_token = AuthService.create_refresh_token(user)

        return {
            "access": access_token,
            "refresh": refresh_token
        }

    @staticmethod
    def verify_jwt_token(token: str, token_type: str):
        try:
            payload = jwt.decode(
                token,
                Config.SECRET_KEY,
                algorithms=[Config.ALGORITHM]
            )
            type = payload.get("type")

            # Verify token type is valid
            if type != token_type:
                return (False, None)

            return (True, payload)
        except JWTError:
            return (False, None)
