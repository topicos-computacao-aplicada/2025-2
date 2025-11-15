from pydantic import BaseModel
from typing import List, Optional

# ---------- Usuário ----------
class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True


# ---------- Arquivos ----------
class UserFileCreate(BaseModel):
    filename: str
    content: str

class UserFileRead(BaseModel):
    id: int
    filename: str
    content: str
    class Config:
        from_attributes = True


# ---------- Chat ----------
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    memory_size: int
    session_id: str