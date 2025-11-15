from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # simples (demo)

    files = relationship("UserFile", back_populates="owner")


class UserFile(Base):
    __tablename__ = "user_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # aqui guardamos o conteúdo do arquivo (texto)

    owner = relationship("User", back_populates="files")