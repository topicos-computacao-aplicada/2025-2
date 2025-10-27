# chat_service.py
"""
Camada de Serviço - Lógica de negócio e orquestração
"""

from gemini_model import GeminiModelService

class ChatService:
    """Serviço de chat que orquestra a lógica de conversação"""
    
    def __init__(self, model_service: GeminiModelService):
        """
        Inicializa o serviço de chat
        
        Args:
            model_service: Instância do serviço do modelo
        """
        self.model_service = model_service
        self.historico = []
        self.contador_mensagens = 0
    
    def enviar_mensagem(self, mensagem: str) -> str:
        """
        Processa uma mensagem do usuário e retorna a resposta
        
        Args:
            mensagem: Mensagem do usuário
            
        Returns:
            Resposta do assistente
        """
        if not mensagem.strip():
            return "Por favor, digite uma mensagem válida."
        
        self.contador_mensagens += 1
        self.historico.append({"usuario": mensagem, "timestamp": "agora"})
        
        resposta = self.model_service.processar_pergunta(mensagem)
        
        self.historico[-1]["assistente"] = resposta
        return resposta
    
    def get_estatisticas(self) -> dict:
        """Retorna estatísticas da sessão"""
        return {
            "total_mensagens": self.contador_mensagens,
            "modelo": self.model_service.model_name,
            "historico_tamanho": len(self.historico)
        }
    
    def limpar_historico(self):
        """Limpa o histórico da sessão"""
        self.historico.clear()
        self.contador_mensagens = 0
    
    def is_healthy(self) -> bool:
        """Verifica se o serviço está funcionando"""
        return self.model_service.health_check()
