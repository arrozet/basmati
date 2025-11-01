from pydantic import BaseModel
from typing import Optional

class ResponseMessage(BaseModel):
    message: str
    detail: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    detail: str
