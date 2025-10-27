"""
Chatbot com Google Gemini usando LangChain com o texto rico (rich)
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Carregar variáveis de ambiente
load_dotenv()

class LangChainGeminiChatBot:
    def __init__(self, model_name="gemini-flash-latest"):
        """
        Inicializa o chatbot com o modelo Gemini
        """
        self.console = Console()
        # Verificar se a chave da API está configurada
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY não encontrada. "
                "Por favor, defina-a no arquivo .env"
            )
        
        self.console.print(f"🔧 Inicializando Gemini ChatBot com modelo: {model_name}")
        self.console.print("⏳ Carregando modelo...")
        
        # Inicializar o modelo Gemini com streaming
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.7,
            streaming=False
        )
        
        self.console.print("✅ Modelo carregado com sucesso!")
        self.console.print("\n" + "="*50)
        self.console.print("🤖 Gemini ChatBot - Pronto para Conversar!")
        self.console.print("="*50)
        self.console.print("Digite 'sair', 'quit' ou 'exit' para encerrar.")
        self.console.print("Digite 'ajuda' ou 'help' para ver os comandos.")
        self.console.print("-" * 50)
    
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
    
    def _display_response(self, response):
        """Exibe a resposta formatada"""        
        # Usar Markdown para melhor formatação
        md = Markdown(response)
        
        self.console.print(
            Panel(
                md,
                title="[bold green]🤖 Assistente[/bold green]",
                title_align="left",
                border_style="blue",
                padding=(1, 2)
            )
        )

    def _show_help(self):
        """Mostra ajuda dos comandos"""
        help_text = """
[b]Comandos disponíveis:[/b]
• [yellow]sair[/yellow], [yellow]exit[/yellow], [yellow]quit[/yellow] - Encerra o chat
• [yellow]ajuda[/yellow], [yellow]help[/yellow] - Mostra esta mensagem

[b]Exemplos de perguntas:[/b]
• "Explique o que é machine learning"
• "Como funciona um neural network?"
• "Me ajude a debugar um código Python"
"""
        self.console.print(
            Panel(
                help_text, 
                title="[bold]Ajuda[/bold]", 
                border_style="yellow",
                padding=(1, 2)
            )
        )    

    def executar_chat(self):
        """Inicia a sessão de chat"""
        self.console.print(
            Panel.fit(
                "[bold blue]🤖 Gemini ChatBot[/bold blue]\n"
                "Digite 'sair' para encerrar ou 'ajuda' para comandos",
                border_style="green"
            )
        )
        
        while True:
            try:
                # Usar input padrão para evitar problemas com flush
                user_input = input("\n\033[1;33mVocê:\033[0m ").strip()
                
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    self.console.print("[green]Até logo! 👋[/green]")
                    break
                elif user_input.lower() in ['ajuda', 'help']:
                    self._show_help()
                    continue
                elif not user_input:
                    continue
                
                # Processar a pergunta
                with self.console.status("[bold green]Aguarde...[/bold green]", spinner="dots") as status:
                    resposta = self.processar_pergunta(user_input)                
                    if resposta:
                        self._display_response(resposta)
                    
            except KeyboardInterrupt:
                self.console.print("\n[red]Interrompido pelo usuário[/red]")
                break
            except Exception as e:
                self.console.print(f"\n[red]Erro: {str(e)}[/red]")

def main():
    """Função principal"""
    try:
        # Inicializar o chatbot
        chatbot = LangChainGeminiChatBot()
        
        # Iniciar o loop de chat
        chatbot.executar_chat()
        
    except ValueError as e:
        console = Console()
        console.print(f"❌ [red]Erro de configuração: {e}[/red]")
        console.print("\n📝 [bold]Como configurar:[/bold]")
        console.print("1. Crie um arquivo .env na mesma pasta")
        console.print("2. Adicione: GOOGLE_API_KEY=sua_chave_aqui")
        console.print("3. Obtenha uma chave em: https://makersuite.google.com/app/apikey")
    except Exception as e:
        console = Console()
        console.print(f"❌ [red]Erro inesperado: {str(e)}[/red]")

if __name__ == "__main__":
    main()
