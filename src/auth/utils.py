# Contenido: Define funciones de utilidad que no forman parte de la lógica de negocio principal.
# Lógica:
#   Incluye funciones que se usan en el módulo pero no encajan directamente en la lógica de negocio.

from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt
from src.config import Config
import uuid
import logging

password_context = CryptContext(
    schemes=['bcrypt']
)

def generate_password_hash(password: str) -> str:
    hash = password_context.hash(password)
    return hash

def verify_password(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)

def create_access_tocken(user_data: dict, expiry: timedelta = None, refresh:bool=False):
    payload={}

    payload["user"]=user_data
    payload["exp"]= datetime.now() + (expiry if expiry is not None else timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(
        payload= payload,
        key= Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM
    )

    return token

def decode_token(token: str) -> dict:
    try:
            
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWKError as e:
        logging.exception(e)
        return None