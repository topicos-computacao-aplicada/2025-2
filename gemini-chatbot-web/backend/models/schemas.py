# backend/models/schemas.py
"""
Schemas Pydantic para validação de dados
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    session_id: str

class MessageResponse(MessageBase):
    id: int
    session_id: str
    message_type: str
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    session_id: str

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionResponse(ChatSessionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    session_id: str
    user_message: MessageResponse
    assistant_message: MessageResponse

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageResponse]
