from dotenv import load_dotenv
import os
import google.generativeai as genai
from typing import List, Dict
from app.clients.abstract_client import AbstractClient
from app.schemas import LLMParameters
from app.openai_generative_model import OpenAIGenerativeModel
load_dotenv()

class OpenAIClient(AbstractClient):
    def __init__(self,llm_config: LLMParameters):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = os.getenv("OPENAI_MODEL", "gemini-pro")
        self._configure_client(llm_config)
    
    def _configure_client(self,llm_config: LLMParameters):
        """Configura o cliente OpenAI"""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY não encontrada no ambiente")
        
        self.model = OpenAIGenerativeModel(self.model_name,generation_config=llm_config)
        self.model.client.api_key = self.api_key