from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas
from ..ai_agent import chat_with_agent, get_session_history
from .auth import SESSION_USER_MAP

router = APIRouter(prefix="/chat", tags=["chat"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_id_and_session(x_session_id: str | None = Header(default=None)) -> tuple[int, str]:
    if not x_session_id or x_session_id not in SESSION_USER_MAP:
        raise HTTPException(status_code=401, detail="Sessão inválida ou não fornecida")
    return SESSION_USER_MAP[x_session_id], x_session_id

@router.post("/", response_model=schemas.ChatResponse)
def chat(
    chat_req: schemas.ChatRequest,
    db: Session = Depends(get_db),
    user_and_session=Depends(get_current_user_id_and_session),
):
    user_id, session_id = user_and_session

    # Carrega arquivos do usuário e gera um texto curto
    files = db.query(models.UserFile).filter(models.UserFile.user_id == user_id).all()
    user_files_text = ""
    for f in files:
        # podemos truncar o conteúdo se quiser
        snippet = f.content[:500]
        user_files_text += f"\n[ARQUIVO: {f.filename}]\n{snippet}\n"

    reply = chat_with_agent(session_id, chat_req.message, user_files_text)
    history = get_session_history(session_id)

    return schemas.ChatResponse(
        reply=reply,
        memory_size=len(history),
        session_id=session_id
    )