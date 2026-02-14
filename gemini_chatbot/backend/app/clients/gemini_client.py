from dotenv import load_dotenv
import os
import google.generativeai as genai
from typing import List, Dict
from app.clients.abstract_client import AbstractClient
from app.schemas import LLMParameters
load_dotenv()

class GeminiClient(AbstractClient):
    def __init__(self,llm_config: LLMParameters):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-pro")
        self._configure_client(llm_config)
    
    def _configure_client(self,llm_config: LLMParameters):
        """Configura o cliente Gemini"""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não encontrada no ambiente")
        
        self.model = genai.GenerativeModel(self.model_name,generation_config=llm_config)