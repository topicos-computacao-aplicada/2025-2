import os
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def send_pdf_for_summary(pdf_path: str, question: str, k: int = 6):
    if not os.path.exists(pdf_path):
        print(f"Erro: arquivo não encontrado -> {pdf_path}")
        return

    with open(pdf_path, "rb") as f:
        files = {"file": (os.path.basename(pdf_path), f, "application/pdf")}
        data = {"question": question, "k": str(k)}

        print("\nEnviando PDF para o backend, aguarde...")
        resp = requests.post(f"{BACKEND_URL}/summary/pdf", files=files, data=data)

    if resp.status_code != 200:
        print("Erro na requisição:", resp.status_code, resp.text)
        return

    result = resp.json()

    print("\n================= CHUNKS (PREVIEW) =================")
    for c in result.get("chunks", []):
        print(f"\n--- Chunk {c['index']} (page {c['page']}) ---")
        print(c["snippet"])
        if len(c["snippet"]) >= 400:
            print("...")

    print("\n==================== RESUMO (LLM) ====================")
    print(result.get("summary", ""))
    print("\n======================================================\n")

def main():
    print("=== Cliente de Terminal: Resumo de PDF (RAG) ===")
    print(f"Backend configurado em: {BACKEND_URL}")

    while True:
        print("\nMenu:")
        print("1 - Resumir um PDF")
        print("0 - Sair")

        op = input("Escolha uma opção: ").strip()

        if op == "0":
            print("Saindo.")
            break
        elif op == "1":
            pdf_path = input("Caminho completo do arquivo PDF: ").strip()
            question = input("Pergunta para orientar o resumo (ex: 'Faça um resumo geral'): ").strip()
            k_str = input("Valor de k (top-k chunks) [padrão 6]: ").strip()
            k = int(k_str) if k_str.isdigit() else 6

            send_pdf_for_summary(pdf_path, question, k)
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()