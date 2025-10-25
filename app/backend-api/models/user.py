"""
Database models

Define las estructuras de datos que se almacenarán en MongoDB.
Estos son los modelos de dominio de la aplicación.
"""
from typing import Optional
from bson import ObjectId


class UserModel:
    """
    Modelo de dominio para Usuario
    
    Estructura en MongoDB:
    {
        "_id": ObjectId,
        "name": str,
        "email": str,
        "pwd": str
    }
    """
    
    collection_name = "users"
    
    def __init__(
        self,
        name: str,
        email: str,
        pwd: str,
        _id: Optional[ObjectId] = None
    ):
        self._id = _id
        self.name = name
        self.email = email
        self.pwd = pwd
    
    def to_dict(self) -> dict:
        """Convertir modelo a diccionario para MongoDB"""
        data = {
            "name": self.name,
            "email": self.email,
            "pwd": self.pwd
        }
        if self._id:
            data["_id"] = self._id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserModel":
        """Crear modelo desde diccionario de MongoDB"""
        return cls(
            _id=data.get("_id"),
            name=data["name"],
            email=data["email"],
            pwd=data["pwd"]
        )
