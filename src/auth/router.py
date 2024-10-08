# Contenido: Define los endpoints de tu módulo de autenticación y las rutas asociadas a ellos.
# Lógica:
#   Importa las dependencias necesarias.
#   Define y configura el enrutador (APIRouter).
#   Registra los endpoints y las funciones que manejan las solicitudes HTTP.

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse

from .schemas import UserCreateModel, UserModel, UserLogginModel
from .service import UserService
from src.db.database import get_session
from .utils import create_access_tocken, decode_token, verify_password

auth_router = APIRouter()
user_service = UserService()


"""
# Without OAUTH
from src.auth.dependencies import TokenBearer
access_token_bearer = AccessTokenBearer()
user_detail=Depends(access_token_bearer)
print(user_detail)
"""
"""
#With OAUTH https://www.youtube.com/watch?v=_y9qQZXE24A&list=PLNdFk2_brsRdgQXLIlKBXQDeRf3qvXVU_&index=3&t=26986s
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
token: Annotated[str, Depends(oauth2_scheme)]
print(token)
"""




@auth_router.post(
        '/signup',
        response_model=UserModel,
        status_code= status.HTTP_201_CREATED
        )
async def create_user_Account(
    user_data: UserCreateModel,
    session: AsyncSession = Depends(get_session)
    ):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with email already exist")
    new_user = await user_service.create_user(user_data, session)

    return new_user

@auth_router.post(
        "/login"
        )
async def login_users(
    login_data: UserLogginModel,
    session: AsyncSession = Depends(get_session)
    ):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)
    if user is not None:
        password_valid = verify_password(password, user.password_hash)
        if password_valid:
            access_token = create_access_tocken(
                user_data={
                    "email":user.email,
                    "user_uid":str(user.uid),
                    "role": user.role
                }
            )

            refresh_token = create_access_tocken(
                user_data={
                    "email":user.email,
                    "user_uid":str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=1)
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    
                    "user":{
                        "email": user.email,
                        "uid": str(user.uid)
                    }
                }
            )
        else:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid password")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid Email"
    )

# ----------------------------------------------

from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer, get_current_user, RoleCheck
from src.db.redis import add_jti_to_blocklist
access_token_bearer = AccessTokenBearer()
role_checker = RoleCheck(["admin","user"])

@auth_router.get("/get_user")
async def get_current_user(
    user = Depends(get_current_user), 
    _:bool=Depends(role_checker)
    ):
    return user



@auth_router.get("/refresh_token")
async def get_new_access_token(token_details:dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_tocken(
            user_data=token_details["user"]
        )
        return JSONResponse(content={
            "access_token": new_access_token
            }
        )
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")


@auth_router.get("/logout")
async def revooke_token(token_details: dict = Depends(access_token_bearer)):
    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={
            "message":"Logged out Successfully"
        },
        status_code=status.HTTP_200_OK
    )