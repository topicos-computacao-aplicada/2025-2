from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    filepath = Column(String)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    chroma_collection_name = Column(String, unique=True, index=True)

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

from .database import engine
create_db_and_tables()