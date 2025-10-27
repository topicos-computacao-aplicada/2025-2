import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import time

# Carregar variáveis de ambiente
load_dotenv()

# --- 1. Inicialização do LLM ---
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    print("LLM (Google Gemini) inicializado com sucesso.")
except Exception as e:
    print(f"Erro ao inicializar o Google Gemini: {e}")
    exit()

# --- 2. Definição do Prompt Template ---
template = """Você é um assistente de IA amigável e prestativo.
Responda à seguinte pergunta:

Pergunta do Usuário: {pergunta}
Resposta:"""

prompt = PromptTemplate(
    input_variables=["pergunta"],
    template=template,
)

# --- 3. Loop de Interação ---
print("\n--- Chatbot (Gemini) ---")
print("Digite 'sair' ou 'quit' para encerrar.")

while True:
    pergunta_usuario = input("Você: ")

    if pergunta_usuario.lower() in ['sair', 'quit']:
        print("Até logo!")
        break

    try:
        # Formatar o prompt
        prompt_formatado = prompt.format(pergunta=pergunta_usuario)
        t1 = time.time()
        print("Processando...")
        
        # Chamar o modelo diretamente
        resposta = llm.invoke(prompt_formatado)
        print(f"IA: {resposta.content.strip()}")
        t2 = time.time()
        print(f"(Tempo de resposta: {t2 - t1:.2f} segundos)\n")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
