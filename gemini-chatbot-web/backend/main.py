# backend/main.py
"""
Aplicação FastAPI principal do backend
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv

from models.database import engine, get_db
from models.chat_models import Base
from models.schemas import (
    MessageCreate, MessageResponse, ChatResponse, 
    ChatSessionCreate, ChatSessionResponse, ChatHistoryResponse
)
from services.gemini_service import GeminiService
from services.chat_service import ChatService

# Carregar variáveis de ambiente
load_dotenv()

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inicializar aplicação FastAPI
app = FastAPI(
    title="Gemini ChatBot API",
    description="API para chatbot usando Google Gemini e LangChain",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],  # Frontend Flask
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar serviços
gemini_service = GeminiService()
chat_service_dep = lambda db: ChatService(db)

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Gemini ChatBot API",
        "version": "1.0.0",
        "status": "online"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check da aplicação"""
    chat_service = chat_service_dep(db)
    
    # Verificar saúde do banco
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    # Verificar saúde do Gemini
    gemini_status = "healthy" if gemini_service.health_check() else "unhealthy"
    
    return {
        "api": "healthy",
        "database": db_status,
        "gemini": gemini_status
    }

@app.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """Cria uma nova sessão de chat"""
    chat_service = chat_service_dep(db)
    
    # Verificar se sessão já existe
    existing_session = chat_service.get_session(session_data.session_id)
    if existing_session:
        return existing_session
    
    # Criar nova sessão
    session = chat_service.create_session(session_data)
    return session

@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    message_data: MessageCreate,
    db: Session = Depends(get_db)
):
    """Envia uma mensagem para o AI e retorna a resposta"""
    chat_service = chat_service_dep(db)
    
    # Verificar/Criar sessão
    session = chat_service.get_session(message_data.session_id)
    if not session:
        session_data = ChatSessionCreate(session_id=message_data.session_id)
        session = chat_service.create_session(session_data)
    
    # Salvar mensagem do usuário
    user_message = chat_service.create_message(message_data, "user")
    
    # Obter resposta do Gemini
    ai_response_content = gemini_service.get_response(message_data.content)
    
    # Salvar resposta do assistente
    assistant_message_data = MessageCreate(
        session_id=message_data.session_id,
        content=ai_response_content
    )
    assistant_message = chat_service.create_message(assistant_message_data, "assistant")
    
    return ChatResponse(
        session_id=message_data.session_id,
        user_message=user_message,
        assistant_message=assistant_message
    )

@app.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Obtém o histórico de uma sessão de chat"""
    chat_service = chat_service_dep(db)
    
    # Verificar se sessão existe
    session = chat_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    
    messages = chat_service.get_chat_history(session_id)
    
    return ChatHistoryResponse(
        session_id=session_id,
        messages=messages
    )

@app.get("/sessions")
async def get_all_sessions(db: Session = Depends(get_db)):
    """Obtém todas as sessões de chat"""
    chat_service = chat_service_dep(db)
    sessions = chat_service.get_all_sessions()
    
    return {
        "sessions": [
            {
                "id": session.id,
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None
            }
            for session in sessions
        ]
    }

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True if os.getenv("DEBUG") == "True" else False
    )
