from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class DocumentBase(BaseModel):
    filename: str
    chroma_collection_name: str

class DocumentCreate(DocumentBase):
    filepath: str

class Document(DocumentBase):
    id: int
    filepath: str
    uploaded_at: datetime

    class Config:
        orm_mode = True

class ChatRequest(BaseModel):
    document_id: int
    question: str

class ChatResponse(BaseModel):
    answer: str
    source_chunks: Optional[List[str]] = None
