from openai import OpenAI
from app.schemas import LLMParameters


# Classe wrapper para manter compatibilidade com a interface do Gemini (atributo .text)
class OpenAIResponse:
    def __init__(self, text: str):
        self.text = text


# Essa classe é um adapter feito para ter a mesma interface da classe genai.GenerativeModel
class OpenAIGenerativeModel:
    def __init__(self,model_name="gpt-4o-mini", generation_config: LLMParameters = None):
        self.client = OpenAI()
        self.model_name = model_name
        generation_config.pop('top_k',None) # Openai não tem o parâmetro top_k
        self.config = generation_config
    
    def generate_content(self, full_prompt):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}],
            **self.config
        )
        
        # Retornar objeto com atributo .text (mesma interface do Gemini)
        return OpenAIResponse(text=response.choices[0].message.content)