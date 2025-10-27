# gemini_model.py
"""
Camada de Modelo/AI - Responsável pela integração com o LLM
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Carregar variáveis de ambiente
load_dotenv()

class GeminiModelService:
    """Serviço responsável pela comunicação com o modelo Gemini"""
    
    def __init__(self, model_name: str = "gemini-flash-latest", temperature: float = 0.7):
        """
        Inicializa o serviço do modelo Gemini
        
        Args:
            model_name: Nome do modelo a ser usado
            temperature: Criatividade do modelo (0.0 - 1.0)
        """
        self.model_name = model_name
        self.temperature = temperature
        self._initialize_model()
    
    def _initialize_model(self):
        """Inicializa o modelo Gemini"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY não encontrada. "
                "Por favor, defina-a no arquivo .env"
            )
        
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key,
            temperature=self.temperature,
            streaming=False
        )
    
    def processar_pergunta(self, pergunta: str) -> str:
        """
        Processa uma pergunta e retorna a resposta do modelo
        
        Args:
            pergunta: Texto da pergunta do usuário
            
        Returns:
            Resposta do modelo ou mensagem de erro
        """
        try:
            mensagem = HumanMessage(content=pergunta)
            resposta = self.llm.invoke([mensagem])
            return resposta.content
        except Exception as e:
            return f"❌ Erro ao processar a pergunta: {str(e)}"
    
    def health_check(self) -> bool:
        """Verifica se o modelo está funcionando"""
        try:
            teste = self.processar_pergunta("Responda 'OK'")
            return True
        except:
            return False
