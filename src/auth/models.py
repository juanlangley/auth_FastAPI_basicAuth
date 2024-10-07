# Contenido: Define los modelos de base de datos que representan las entidades del módulo de autenticación.
# Lógica:
#   Define clases de modelos de base de datos usando SQLAlchemy, Tortoise ORM, o cualquier otro ORM que estés utilizando.
#   Incluye las relaciones entre modelos si es necesario.

from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
import uuid
from typing import Optional, List

class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column= Column(
            pg.UUID,
            nullable = False,
            primary_key = True,
            default= uuid.uuid4
        )
    )
    username: str
    email: str
    full_name: str | None = None

    role: str = Field(
        sa_column=Column(
            pg.VARCHAR, nullable= False, server_default="user" 
        )
    )

    group_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="auth_group.uid")
    group: Optional["Group"] = Relationship(back_populates="users")

    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now, onupdate=datetime.now))

    is_verified: bool = Field(default=False)
    is_disabled: bool = Field(default=False)  
    password_hash: str = Field(exclude=True)


    def __repr__(self) -> str:
        return f'<User {self.username}>'



class Group(SQLModel, table = True):
    __tablename__ = "auth_group"

    uid: uuid.UUID = Field(
        sa_column= Column(
            pg.UUID,
            nullable = False,
            primary_key = True,
            default= uuid.uuid4
        )
    )
    groupname: str
    users: List["User"]= Relationship(back_populates="group", sa_relationship_kwargs={'lazy':'selectin'})
