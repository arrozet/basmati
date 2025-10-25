"""
Pydantic schemas para validación y serialización de datos de usuario.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    """Schema base para Usuario"""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del usuario")
    email: EmailStr = Field(..., description="Email del usuario")


class UserCreate(UserBase):
    """Schema para crear un usuario"""
    pwd: str = Field(..., min_length=1, description="Contraseña del usuario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "david",
                "email": "davidmunvalle@uma.es",
                "pwd": "1234"
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema para actualizar un usuario (todos los campos opcionales)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    pwd: Optional[str] = Field(None, min_length=1)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "David Muñoz",
                "email": "nuevo@email.com"
            }
        }
    )


class UserInDB(UserBase):
    """Schema para usuario en la base de datos"""
    id: str = Field(..., alias="_id", description="ID del usuario en MongoDB")
    pwd: str
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "68fa377af47c0bcded1182e2",
                "name": "david",
                "email": "davidmunvalle@uma.es",
                "pwd": "1234"
            }
        }
    )


class UserResponse(UserBase):
    """Schema para respuesta de usuario (sin contraseña)"""
    id: str = Field(..., alias="_id", description="ID del usuario")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "68fa377af47c0bcded1182e2",
                "name": "david",
                "email": "davidmunvalle@uma.es"
            }
        }
    )


class UserList(BaseModel):
    """Schema para lista paginada de usuarios"""
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "users": [
                    {
                        "_id": "68fa377af47c0bcded1182e2",
                        "name": "david",
                        "email": "davidmunvalle@uma.es"
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10
            }
        }
    )
