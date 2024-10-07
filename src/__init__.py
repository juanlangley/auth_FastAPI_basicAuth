# https://codigoencasa.com/como-estructurar-tus-proyectos-fastapi/

from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.db.database import init_db

#from src.users.router import users_router
from src.auth.router import auth_router

import colorama
colorama.init()

version = "v1"

@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"Server is starting ...")
    await init_db()

    yield
    print(f"Server has been stopped")

app = FastAPI(
    title="Innova_API",
    description="A REST API for innova systems",
    #lifespan=life_span,
    version=version
    )

#app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])