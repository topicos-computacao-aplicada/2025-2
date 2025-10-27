# backend/services/chat_service.py
"""
Serviço para operações de banco de dados do chat
"""

from sqlalchemy.orm import Session
from models.chat_models import ChatSession, ChatMessage
from models.schemas import ChatSessionCreate, MessageCreate
import uuid
from datetime import datetime

class ChatService:
    """Serviço para operações de chat no banco de dados"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, session_data: ChatSessionCreate) -> ChatSession:
        """
        Cria uma nova sessão de chat
        
        Args:
            session_data: Dados da sessão
            
        Returns:
            Sessão criada
        """
        db_session = ChatSession(
            session_id=session_data.session_id
        )
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        return db_session
    
    def get_session(self, session_id: str) -> ChatSession:
        """
        Obtém uma sessão pelo ID
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Sessão encontrada ou None
        """
        return self.db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    
    def create_message(self, message_data: MessageCreate, message_type: str) -> ChatMessage:
        """
        Cria uma nova mensagem
        
        Args:
            message_data: Dados da mensagem
            message_type: Tipo da mensagem ('user' ou 'assistant')
            
        Returns:
            Mensagem criada
        """
        db_message = ChatMessage(
            session_id=message_data.session_id,
            message_type=message_type,
            content=message_data.content
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message
    
    def get_chat_history(self, session_id: str) -> list:
        """
        Obtém histórico de mensagens de uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Lista de mensagens ordenadas por timestamp
        """
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp.asc()).all()
        
        return [msg.to_dict() for msg in messages]
    
    def get_all_sessions(self) -> list:
        """
        Obtém todas as sessões
        
        Returns:
            Lista de sessões
        """
        return self.db.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()
    
    def generate_session_id(self) -> str:
        """
        Gera um ID único para sessão
        
        Returns:
            ID da sessão
        """
        return f"session_{uuid.uuid4().hex[:8]}"
