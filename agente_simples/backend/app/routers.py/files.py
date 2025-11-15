from typing import List
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas
from .auth import SESSION_USER_MAP

router = APIRouter(prefix="/files", tags=["files"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_id(x_session_id: str | None = Header(default=None)) -> int:
    if not x_session_id or x_session_id not in SESSION_USER_MAP:
        raise HTTPException(status_code=401, detail="Sessão inválida ou não fornecida")
    return SESSION_USER_MAP[x_session_id]

@router.post("/", response_model=schemas.UserFileRead)
def create_file(
    file_data: schemas.UserFileCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    db_file = models.UserFile(
        user_id=user_id,
        filename=file_data.filename,
        content=file_data.content
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

@router.get("/", response_model=List[schemas.UserFileRead])
def list_files(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    files = db.query(models.UserFile).filter(models.UserFile.user_id == user_id).all()
    return files