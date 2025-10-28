import google.generativeai as genai
from typing import List, Tuple
from ..core.config import settings

class RAGService:
    def __init__(self, vector_db_service):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY não configurada")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-flash-latest')
        self.vector_db_service = vector_db_service

    def generate_response(self, document_id: int, collection_name: str, question: str) -> Tuple[str, List[str]]:
        print(f"🤔 Processando pergunta: '{question}' para documento {document_id}")
        
        relevant_chunks = self.vector_db_service.query_collection(
            collection_name=collection_name,
            query_text=question,
            n_results=5
        )

        print(f"📚 Chunks relevantes encontrados: {len(relevant_chunks)}")

        if not relevant_chunks:
            return "Não consegui encontrar informações relevantes no documento para responder à sua pergunta.", []

        context = "\n".join(relevant_chunks)
        prompt = f"""Com base no contexto fornecido abaixo, responda à pergunta do usuário de forma precisa e concisa.

CONTEXTO:
{context}

PERGUNTA: {question}

INSTRUÇÕES:
- Responda APENAS com base nas informações do contexto fornecido
- Se a resposta não estiver no contexto, diga: "Não encontrei informações sobre isso no documento"
- Seja direto e objetivo na resposta
- Use as informações do contexto de forma fiel

RESPOSTA:"""

        try:
            print("🧠 Consultando modelo Gemini...")
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            print(f"✅ Resposta gerada: {answer[:100]}...")
            return answer, relevant_chunks
        except Exception as e:
            print(f"❌ Erro ao gerar resposta com Gemini: {e}")
            return "Ocorreu um erro ao processar sua pergunta. Tente novamente.", []