# rich_ui.py
"""
Camada de Apresentação - Interface do usuário com Rich
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.columns import Columns
from rich.table import Table
from rich import print as rprint
from datetime import datetime

class RichChatUI:
    """Interface de usuário rica para o chatbot"""
    
    def __init__(self):
        self.console = Console()
        self.sessao_id = f"sessao_{datetime.now().strftime('%H%M%S')}"
        self.inicio_sessao = datetime.now()
    
    def mostrar_boas_vindas(self, modelo_nome: str):
        """Exibe tela de boas-vindas"""
        welcome_text = f"""
[b]Bem-vindo ao Gemini ChatBot![/b]

[blue]• Modelo:[/blue] {modelo_nome}
[blue]• Sessão:[/blue] {self.sessao_id}
[blue]• Início:[/blue] {self.inicio_sessao.strftime('%H:%M:%S')}

[dim]Digite sua pergunta ou 'ajuda' para comandos disponíveis[/dim]
"""
        self.console.print(
            Panel.fit(
                welcome_text,
                title="[bold cyan]🤖 Assistente de IA Gemini[/bold cyan]",
                border_style="green",
                padding=(1, 2)
            )
        )
    
    def mostrar_ajuda(self):
        """Exibe painel de ajuda"""
        help_text = """
[b]🎯 Comandos Disponíveis:[/b]

[yellow]• ajuda[/yellow] - Mostra esta mensagem
[yellow]• status[/yellow] - Mostra informações da sessão
[yellow]• limpar[/yellow] - Limpa o histórico
[yellow]• sair[/yellow] - Encerra o aplicativo

[b]💡 Exemplos de Perguntas:[/b]

• "Explique o que é inteligência artificial"
• "Me ajude com um código Python para ordenação"
• "Qual a diferença entre machine learning e deep learning?"
• "Como posso melhorar a performance do meu algoritmo?"

[b]🎨 Recursos:[/b]

• Formatação [bold]Markdown[/bold] automática
• Realce de [bold]syntax[/bold] para código
• Interface [bold]rica e interativa[/bold]
"""
        self.console.print(
            Panel(
                help_text,
                title="[bold yellow]📚 Ajuda & Comandos[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
                width=80
            )
        )
    
    def mostrar_status(self, estatisticas: dict):
        """Exibe status da sessão"""
        duracao = datetime.now() - self.inicio_sessao
        
        table = Table(title="[bold]📊 Status da Sessão[/bold]", show_header=False)
        table.add_column("Metrica", style="bold cyan")
        table.add_column("Valor", style="white")
        
        table.add_row("Sessão ID", self.sessao_id)
        table.add_row("Duração", str(duracao).split('.')[0])
        table.add_row("Mensagens", str(estatisticas['total_mensagens']))
        table.add_row("Modelo", estatisticas['modelo'])
        table.add_row("Status", "[green]Ativo[/green]")
        
        self.console.print(table)
    
    def mostrar_mensagem_usuario(self, mensagem: str):
        """Exibe mensagem do usuário formatada"""
        self.console.print(f"\n[bold yellow]👤 Você:[/bold yellow] {mensagem}")
    
    def mostrar_resposta_assistente(self, resposta: str):
        """Exibe resposta do assistente formatada"""
        md = Markdown(resposta)
        self.console.print(
            Panel(
                md,
                title="[bold green]🤖 Assistente[/bold green]",
                title_align="left",
                border_style="blue",
                padding=(1, 2)
            )
        )
    
    def mostrar_erro(self, mensagem: str):
        """Exibe mensagem de erro"""
        self.console.print(
            Panel(
                f"[red]{mensagem}[/red]",
                title="[bold red]❌ Erro[/bold red]",
                border_style="red"
            )
        )
    
    def mostrar_info(self, mensagem: str):
        """Exibe mensagem informativa"""
        self.console.print(f"[dim]💡 {mensagem}[/dim]")
    
    def obter_input_usuario(self) -> str:
        """Obtém input do usuário com prompt personalizado"""
        try:
            return self.console.input("\n[bold yellow]💬 Sua mensagem: [/bold yellow]").strip()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.mostrar_erro(f"Erro ao ler input: {e}")
            return ""
    
    def mostrar_despedida(self, estatisticas: dict):
        """Exibe mensagem de despedida com resumo"""
        duracao = datetime.now() - self.inicio_sessao
        
        resumo_texto = f"""
[b]Resumo da Sessão:[/b]

[cyan]• Duração:[/cyan] {str(duracao).split('.')[0]}
[cyan]• Mensagens:[/cyan] {estatisticas['total_mensagens']}
[cyan]• Modelo:[/cyan] {estatisticas['modelo']}
[cyan]• Sessão:[/cyan] {self.sessao_id}

[green]Obrigado por usar o Gemini ChatBot! 👋[/green]
"""
        self.console.print(
            Panel(
                resumo_texto,
                title="[bold green]🎯 Sessão Finalizada[/bold green]",
                border_style="green"
            )
        )
