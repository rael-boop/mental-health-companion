from enum import Enum
import string
import secrets
import base64
from datetime import timedelta, datetime
from sqlalchemy.exc import NoResultFound

from src.models.token import (
    TokenBlacklist,
    Token
)
from src.schemas.token import (
    TokenBlacklistSchema,
    TokenSchema,
    TokenTypeEnum
)
from src.models import DatabaseSession


class TokenBlacklistService:
    @staticmethod
    def is_blacklisted(token: str) -> bool:
        is_blacklisted = False
        with DatabaseSession().withSession() as session:
            blacklisted_token = session.query(TokenBlacklist).where(
                TokenBlacklist.token == token).first()
            if blacklisted_token:
                is_blacklisted = True
        return is_blacklisted

    @staticmethod
    def blacklist_token(token: str) -> TokenBlacklistSchema:
        with DatabaseSession().withSession() as session:
            blacklist_token_orm = TokenBlacklist(
                token=token,
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            session.add(blacklist_token_orm)
            session.commit()
            blacklist_token = TokenBlacklistSchema.from_orm(
                blacklist_token_orm)
            return blacklist_token


class TokenCharacterType(Enum):
    alphanumeric = "alphanumeric"
    number = "number"


class TokenService:
    @staticmethod
    def generate_token(
        token_character_type: TokenCharacterType = TokenCharacterType.alphanumeric,
        length: int = 10
    ) -> str:
        """Generates a token of the specified type and length."""

        allowed_chars = string.ascii_letters + string.digits
        # Alphanumeric characters

        if token_character_type == TokenCharacterType.number:
            allowed_chars = string.digits  # Only digits for "number" type

        token = ''.join(secrets.choice(allowed_chars) for _ in range(length))
        return token

    @staticmethod
    def create_token_model(
        user_id,
        type: TokenTypeEnum,
        token_character_type: TokenCharacterType = TokenCharacterType.alphanumeric,
        length: int = 10,
        expiration_hours: int = 48,
        encode_token=True
    ):
        expires_at = datetime.utcnow() + timedelta(hours=expiration_hours)
        with DatabaseSession().withSession() as session:
            # delete all existing tokens of type
            session.query(Token).where(
                Token.user_id == user_id,
                Token.type == type
            ).delete()
            session.commit()

            # generate new token
            token_str = TokenService.generate_token(
                token_character_type,
                length
            )
            token_orm = Token(
                type=type,
                token=token_str,
                expires_at=expires_at,
                user_id=user_id
            )

            session.add(token_orm)
            session.commit()

            token = TokenSchema.from_orm(token_orm)

            if encode_token:
                encoded_token_id = TokenService.encode_number(token_orm.id)

                token_str = f"{token_str}_{encoded_token_id}"
            return (token_str, token)

    @staticmethod
    def delete_token(token_id: int):
        with DatabaseSession().withSession() as session:
            session.query(Token).where(Token.id == token_id).delete()
            session.commit()

    @staticmethod
    def get_by_encoded_token(
        token: str,
        type: TokenTypeEnum,
        is_encoded=True,
        user_id=None
    ) -> (bool, TokenSchema):
        """Retrieves a token by its encoded value.

        Args:
            token: Combination of the actual token and its token_id (if encoded)
            type: Token type
            is_encoded: Whether the token is encoded
            user_id: User ID (only used for non-encoded tokens)

        Returns:
            A tuple, (token_exists, token|None)
        """

        def get_query(session):
            # Build query based on encoded or non-encoded token
            if is_encoded:
                (token_str, encoded_id) = token.split("_")
                id = TokenService.decode_number(encoded_id)
                return session.query(Token).where(
                    Token.id == id,
                    Token.type == type,
                    Token.token == token_str,
                    Token.expires_at > datetime.utcnow()
                )
            else:
                return session.query(Token).where(
                    Token.user_id == user_id,
                    Token.type == type,
                    Token.token == token,
                    Token.expires_at > datetime.utcnow()
                )

        # Use with_session and handle exceptions
        with DatabaseSession().withSession() as session:
            try:
                token_orm = get_query(session).one()
                token = TokenSchema.from_orm(token_orm)
                return (True, token)
            except NoResultFound:
                return (False, None)

    @staticmethod
    def encode_number(num):
        """Encodes a number to a base64 string.

        Args:
            num: The number to encode.

        Returns:
            A base64 encoded string representation of the number.
        """
        # Convert the number to a byte string using big-endian encoding.
        byte_string = num.to_bytes(
            (num.bit_length() + 7) // 8, byteorder='big')
        # Encode the byte string to base64.
        encoded_data = base64.urlsafe_b64encode(byte_string).decode('utf-8')
        return encoded_data

    @staticmethod
    def decode_number(encoded_data):
        """Decodes a base64 encoded string back to a number.

        Args:
            encoded_data: The base64 encoded string to decode.

        Returns:
            The original number represented by the encoded string.
        """
        # Decode the base64 string back to a byte string.
        byte_string = base64.urlsafe_b64decode(encoded_data.encode('utf-8'))
        # Convert the byte string back to an integer using big-endian decoding.
        return int.from_bytes(byte_string, byteorder='big')
