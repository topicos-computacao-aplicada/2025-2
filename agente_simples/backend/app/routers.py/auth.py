# backend/app/routers/auth.py
import hashlib
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import SessionLocal
from ..ai_agent import create_session_id

router = APIRouter(prefix="/auth", tags=["auth"])

# Mapa de sessões em memória
SESSION_USER_MAP: Dict[str, int] = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    # hash simples só para demo (não use em produção)
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

@router.post("/register", response_model=schemas.UserRead)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    db_user = models.User(
        username=user.username,
        password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

class LoginResponse(schemas.BaseModel):
    user: schemas.UserRead
    session_id: str

@router.post("/login", response_model=LoginResponse)
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or db_user.password != hash_password(user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    session_id = create_session_id()
    SESSION_USER_MAP[session_id] = db_user.id

    return LoginResponse(
        user=db_user,
        session_id=session_id
    )