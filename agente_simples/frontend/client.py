# frontend/client.py
import requests
import getpass
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def register():
    print("=== Registro de usuário ===")
    username = input("Username: ").strip()
    password = getpass.getpass("Senha: ").strip()

    resp = requests.post(
        f"{BACKEND_URL}/auth/register",
        json={"username": username, "password": password},
    )
    if resp.status_code == 200:
        print("Usuário registrado com sucesso!")
    else:
        print("Erro ao registrar:", resp.status_code, resp.text)

def login():
    print("=== Login ===")
    username = input("Username: ").strip()
    password = getpass.getpass("Senha: ").strip()

    resp = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"username": username, "password": password},
    )
    if resp.status_code != 200:
        print("Erro ao logar:", resp.status_code, resp.text)
        return None, None

    data = resp.json()
    user = data["user"]
    session_id = data["session_id"]
    print(f"Login bem-sucedido. Usuário: {user['username']}, session_id: {session_id}")
    return user, session_id

def content_file(path_file: str) -> str:
    if not os.path.isfile(path_file):
        raise FileNotFoundError(f"Arquivo não encontrado: {path_file}")
    with open(path_file, "r", encoding="utf-8") as f:
        return f.read()

def upload_file(session_id: str):
    print("=== Criar arquivo do usuário ===")
    filename = input("Nome do arquivo (apenas identificador, ex: notas.txt): ").strip()
    try:
        content = content_file(filename)
        resp = requests.post(
            f"{BACKEND_URL}/files/",
            json={"filename": filename, "content": content},
            headers={"X-Session-Id": session_id},
        )
        if resp.status_code == 200:
            print("Arquivo registrado com sucesso:", resp.json())
        else:
            print("Erro ao criar arquivo:", resp.status_code, resp.text)
    except Exception as e:
        print("Erro ao processar o arquivo:", str(e))

def list_files(session_id: str):
    print("=== Listar arquivos do usuário ===")
    resp = requests.get(
        f"{BACKEND_URL}/files/",
        headers={"X-Session-Id": session_id},
    )
    if resp.status_code == 200:
        files = resp.json()
        if not files:
            print("Nenhum arquivo cadastrado.")
        else:
            for f in files:
                print(f"- ({f['id']}) {f['filename']}")
    else:
        print("Erro ao listar arquivos:", resp.status_code, resp.text)

def chat(session_id: str):
    print("=== Chat com o agente de IA ===")
    print("Digite 'sair' para encerrar o chat.")
    while True:
        msg = input("Você: ")
        if msg.lower().strip() in ("sair", "exit", "quit"):
            print("Encerrando chat.")
            break

        resp = requests.post(
            f"{BACKEND_URL}/chat/",
            json={"message": msg},
            headers={"X-Session-Id": session_id},
        )
        if resp.status_code == 200:
            data = resp.json()
            print(f"Agente: {data['reply']}")
            print(f"[Memória atual: {data['memory_size']} mensagens armazenadas]")
        else:
            print("Erro no chat:", resp.status_code, resp.text)
            if resp.status_code == 401:
                print("Sessão expirada ou inválida.")
                break

def main():
    print("=== Cliente Terminal - AI Agent ===")
    print(f"Backend: {BACKEND_URL}")
    session_id = None
    user = None

    while True:
        print("\nMenu principal:")
        print("1 - Registrar usuário")
        print("2 - Login")
        print("3 - Criar arquivo (requer login)")
        print("4 - Listar arquivos (requer login)")
        print("5 - Chat com agente (requer login)")
        print("0 - Sair")

        op = input("Escolha uma opção: ").strip()

        if op == "1":
            register()
        elif op == "2":
            user, session_id = login()
        elif op == "3":
            if not session_id:
                print("Você precisa estar logado.")
            else:
                upload_file(session_id)
        elif op == "4":
            if not session_id:
                print("Você precisa estar logado.")
            else:
                list_files(session_id)
        elif op == "5":
            if not session_id:
                print("Você precisa estar logado.")
            else:
                chat(session_id)
        elif op == "0":
            print("Saindo.")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()