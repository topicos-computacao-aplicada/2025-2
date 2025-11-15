import os
import uuid
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Defina a variável de ambiente OPENAI_API_KEY ou o arquivo .env")

client = OpenAI(api_key=OPENAI_API_KEY)

# Troque aqui pelo modelo que você quiser (ex.: um GPT-3.x se disponível)
DEFAULT_MODEL = "gpt-4.1-mini"

# Memória em memória (RAM) por sessão: {session_id: [mensagens]}
# Cada mensagem será um dict: {"role": "user" | "assistant", "content": "texto"}
SESSION_MEMORY: Dict[str, List[Dict[str, str]]] = {}

# Limite de interações armazenadas (10 últimas interações "completas")
MAX_TURNS = 10

def create_session_id() -> str:
    return str(uuid.uuid4())

def get_session_history(session_id: str) -> List[Dict[str, str]]:
    return SESSION_MEMORY.setdefault(session_id, [])

def add_to_session_history(session_id: str, role: str, content: str) -> None:
    history = get_session_history(session_id)
    history.append({"role": role, "content": content})
    # mantemos no máximo 2 * MAX_TURNS mensagens (user+assistant)
    if len(history) > 2 * MAX_TURNS:
        # remove as mais antigas
        over = len(history) - 2 * MAX_TURNS
        del history[0:over]

def build_prompt_from_context(user_message: str, user_files_text: str, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Monta a lista de mensagens para enviar ao modelo.
    """
    system_content = (
        "Você é um assistente de IA integrado a um sistema que possui usuários e arquivos.\n"
        "Você deve responder de forma clara e útil, usando as informações dos arquivos do usuário quando relevante.\n"
        "Os arquivos do usuário (texto resumido) são:\n"
        f"{user_files_text if user_files_text else '(nenhum arquivo cadastrado)'}"
    )

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_content}
    ]

    # adiciona histórico (curto prazo)
    messages.extend(history)

    # nova mensagem do usuário
    messages.append({"role": "user", "content": user_message})

    return messages


def call_llm(messages: List[Dict[str, str]]) -> str:
    """
    Chama o modelo da OpenAI.
    Usando API Responses (nova) como exemplo.
    """
    response = client.responses.create(
        model=DEFAULT_MODEL,
        input=[{"role": m["role"], "content": m["content"]} for m in messages]
    )

    # saída padrão (primeiro output de texto)
    # (API Responses pode ter múltiplos outputs; aqui simplificamos)
    output = response.output[0].content[0].text
    return output


def chat_with_agent(session_id: str, user_message: str, user_files_text: str) -> str:
    history = get_session_history(session_id)
    messages = build_prompt_from_context(user_message, user_files_text, history)
    assistant_reply = call_llm(messages)

    # atualiza memória
    add_to_session_history(session_id, "user", user_message)
    add_to_session_history(session_id, "assistant", assistant_reply)

    return assistant_reply