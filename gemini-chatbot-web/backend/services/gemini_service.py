# backend/services/gemini_service.py
"""
Serviço para integração com o Google Gemini
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate

load_dotenv()

class GeminiService:
    """Serviço para comunicação com o modelo Gemini"""
    
    def __init__(self, model_name: str = "gemini-flash-latest", temperature: float = 0.7):
        """
        Inicializa o serviço do Gemini
        
        Args:
            model_name: Nome do modelo
            temperature: Criatividade do modelo (0.0 - 1.0)
        """
        self.model_name = model_name
        self.temperature = temperature
        self._initialize_model()
    
    def _initialize_model(self):
        """Inicializa o modelo Gemini"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não encontrada no ambiente")
        
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key,
            temperature=self.temperature,
            streaming=False
        )
    
    def get_response(self, message: str, context: str = None) -> str:
        """
        Obtém resposta do modelo Gemini
        
        Args:
            message: Mensagem do usuário
            context: Contexto adicional (opcional)
            
        Returns:
            Resposta do modelo
        """
        try:
            if context:
                prompt_template = PromptTemplate(
                    template="Contexto: {context}\n\nPergunta: {message}\nResposta:",
                    input_variables=["context", "message"]
                )
                formatted_prompt = prompt_template.format(context=context, message=message)
                human_message = HumanMessage(content=formatted_prompt)
            else:
                human_message = HumanMessage(content=message)
            
            response = self.llm.invoke([human_message])
            return response.content
            
        except Exception as e:
            return f"❌ Erro ao processar a pergunta: {str(e)}"
    
    def health_check(self) -> bool:
        """Verifica se o serviço está saudável"""
        try:
            test_response = self.get_response("Responda 'OK'")
            return True
        except:
            return False
