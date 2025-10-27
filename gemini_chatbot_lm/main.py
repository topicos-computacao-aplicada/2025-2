"""
Arquivo principal para executar a aplicação Gemini ChatBot
"""

from chat_app import ChatApplication

def main():
    """Função principal de execução"""
    print("🚀 Iniciando Gemini ChatBot...")
    app = ChatApplication(model_name="gemini-flash-latest")
    app.executar()

if __name__ == "__main__":
    main()