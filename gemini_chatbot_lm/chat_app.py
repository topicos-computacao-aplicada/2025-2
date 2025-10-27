"""
Camada de Aplicação - Orquestração principal do aplicativo
"""

import sys
from gemini_model import GeminiModelService
from chat_service import ChatService
from rich_ui import RichChatUI

class ChatApplication:
    """Aplicação principal que orquestra todas as camadas"""
    
    def __init__(self, model_name: str = "gemini-flash-latest"):
        """
        Inicializa a aplicação
        
        Args:
            model_name: Nome do modelo Gemini a ser usado
        """
        self.model_name = model_name
        self.ui = RichChatUI()
        self.model_service = None
        self.chat_service = None
        
    def inicializar(self) -> bool:
        """
        Inicializa todos os componentes da aplicação
        
        Returns:
            True se inicialização foi bem sucedida
        """
        try:
            self.ui.console.print("[cyan]🚀 Inicializando Gemini ChatBot...[/cyan]")
            
            # Inicializar serviço do modelo
            self.model_service = GeminiModelService(model_name=self.model_name)
            
            # Inicializar serviço de chat
            self.chat_service = ChatService(self.model_service)
            
            # Verificar saúde do sistema
            if not self.chat_service.is_healthy():
                self.ui.mostrar_erro("Falha na comunicação com o modelo Gemini")
                return False
            
            self.ui.console.print("[green]✅ Sistema inicializado com sucesso![/green]")
            return True
            
        except ValueError as e:
            self.ui.mostrar_erro(f"Erro de configuração: {e}")
            self._mostrar_configuracao()
            return False
        except Exception as e:
            self.ui.mostrar_erro(f"Erro inesperado: {e}")
            return False
    
    def executar(self):
        """Método principal que executa a aplicação"""
        if not self.inicializar():
            return
        
        # Mostrar interface
        self.ui.mostrar_boas_vindas(self.model_name)
        
        # Loop principal
        while True:
            try:
                # Obter input do usuário
                user_input = self.ui.obter_input_usuario()
                
                # Processar comandos especiais
                if self._processar_comando(user_input):
                    if user_input.lower() in ['sair', 'exit', 'quit']:
                        break
                    continue
                
                # Processar mensagem normal
                if user_input:
                    self.ui.mostrar_mensagem_usuario(user_input)
                    
                    with self.ui.console.status(
                        "[bold green]🔮 Processando sua pergunta...[/bold green]", 
                        spinner="dots12"
                    ) as status:
                        resposta = self.chat_service.enviar_mensagem(user_input)
                    
                    self.ui.mostrar_resposta_assistente(resposta)
                    
            except KeyboardInterrupt:
                self.ui.console.print("\n[yellow]⚠️  Interrompido pelo usuário[/yellow]")
                break
            except Exception as e:
                self.ui.mostrar_erro(f"Erro durante execução: {e}")
                break
        
        # Finalizar aplicação
        self.finalizar()
    
    def _processar_comando(self, comando: str) -> bool:
        """
        Processa comandos especiais
        
        Args:
            comando: Comando digitado pelo usuário
            
        Returns:
            True se foi um comando processado
        """
        comando = comando.lower()
        
        if comando in ['sair', 'exit', 'quit']:
            return True
            
        elif comando in ['ajuda', 'help']:
            self.ui.mostrar_ajuda()
            return True
            
        elif comando in ['status', 'info']:
            estatisticas = self.chat_service.get_estatisticas()
            self.ui.mostrar_status(estatisticas)
            return True
            
        elif comando in ['limpar', 'clear']:
            self.chat_service.limpar_historico()
            self.ui.mostrar_info("Histórico da sessão limpo")
            return True
            
        return False
    
    def finalizar(self):
        """Finaliza a aplicação graciosamente"""
        estatisticas = self.chat_service.get_estatisticas()
        self.ui.mostrar_despedida(estatisticas)
    
    def _mostrar_configuracao(self):
        """Mostra instruções de configuração"""
        config_text = """
[bold]📝 Como Configurar:[/bold]

1. [yellow]Crie um arquivo .env[/yellow] na mesma pasta
2. [yellow]Adicione sua chave:[/yellow] GOOGLE_API_KEY=sua_chave_aqui
3. [yellow]Obtenha uma chave em:[/yellow] https://makersuite.google.com/app/apikey
4. [yellow]Execute novamente o aplicativo[/yellow]

[dim]Certifique-se de que o arquivo .env está no mesmo diretório do script.[/dim]
"""
        self.ui.console.print(
            Panel(
                config_text,
                title="[bold red]🔧 Configuração Necessária[/bold red]",
                border_style="red"
            )
        )

def main():
    """Função principal"""
    app = ChatApplication(model_name="gemini-flash-latest")
    app.executar()

if __name__ == "__main__":
    main()
