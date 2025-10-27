"""
Chatbot com Google Gemini usando LangChain
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.callbacks import StreamingStdOutCallbackHandler

# Carregar variáveis de ambiente
load_dotenv()

class LangChainGeminiChatBot:
    def __init__(self, model_name="gemini-flash-latest"):
        """
        Inicializa o chatbot com o modelo Gemini
        """
        # Verificar se a chave da API está configurada
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY não encontrada. "
                "Por favor, defina-a no arquivo .env"
            )
        
        print(f"🔧 Inicializando Gemini ChatBot com modelo: {model_name}")
        print("⏳ Carregando modelo...")
        
        # Inicializar o modelo Gemini com streaming
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
        
        print("✅ Modelo carregado com sucesso!")
        print("\n" + "="*50)
        print("🤖 Gemini ChatBot - Pronto para Conversar!")
        print("="*50)
        print("Digite 'sair', 'quit' ou 'exit' para encerrar.")
        print("-" * 50)
    
    def processar_pergunta(self, pergunta):
        """
        Processa a pergunta do usuário e retorna a resposta do modelo
        """
        try:
            # Criar uma mensagem no formato esperado pelo LangChain
            mensagem = HumanMessage(content=pergunta)
            
            # Fazer a chamada para o modelo
            resposta = self.llm.invoke([mensagem])
            
            return resposta.content
            
        except Exception as e:
            return f"❌ Erro ao processar a pergunta: {str(e)}"
    
    def executar_chat(self):
        """Loop principal do chat"""
        while True:
            try:
                # Ler input do usuário
                pergunta = input("\n💬 Você: ").strip()
                
                # Verificar se o usuário quer sair
                if pergunta.lower() in ['sair', 'quit', 'exit', '']:
                    print("\n👋 Até logo! Obrigado por usar o Gemini ChatBot.")
                    break
                
                # Processar a pergunta
                print("🤖 Gemini: ", end="", flush=True)
                resposta = self.processar_pergunta(pergunta)
                
                # Adicionar uma quebra de linha após a resposta streamed
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrompido pelo usuário. Até logo!")
                break
            except Exception as e:
                print(f"\n❌ Erro inesperado: {str(e)}")

def main():
    """Função principal"""
    try:
        # Inicializar o chatbot
        chatbot = LangChainGeminiChatBot()
        
        # Iniciar o loop de chat
        chatbot.executar_chat()
        
    except ValueError as e:
        print(f"❌ Erro de configuração: {e}")
        print("\n📝 Como configurar:")
        print("1. Crie um arquivo .env na mesma pasta")
        print("2. Adicione: GOOGLE_API_KEY=sua_chave_aqui")
        print("3. Obtenha uma chave em: https://makersuite.google.com/app/apikey")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

if __name__ == "__main__":
    main()