# Contenido: Define los modelos de datos que se utilizan para la validación y serialización/deserialización de datos en las solicitudes y respuestas.
# Lógica:
#   Define modelos Pydantic para las solicitudes y respuestas.
#   Puedes incluir validaciones específicas en estos modelos.


from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class UserCreateModel(BaseModel):
    full_name: str = Field(min_length=4)
    username: str = Field(max_length=30)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)

class UserModel(BaseModel):
    uid: uuid.UUID 
    username: str
    email: str
    full_name: str
    created_at: datetime
    update_at: datetime
    is_verified: bool 
    is_disabled: bool 
    password_hash: str = Field(exclude=True)

class UserLogginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)