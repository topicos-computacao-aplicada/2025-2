// frontend/static/js/chat.js
/**
 * JavaScript para controle do chat frontend
 */

class ChatApp {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.clearChatBtn = document.getElementById('clearChat');
        this.loadHistoryBtn = document.getElementById('loadHistory');
        this.checkHealthBtn = document.getElementById('checkHealth');
        
        this.initEventListeners();
        this.loadHistory();
    }
    
    initEventListeners() {
        // Enviar mensagem
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Ações do chat
        this.clearChatBtn.addEventListener('click', () => this.clearChat());
        this.loadHistoryBtn.addEventListener('click', () => this.loadHistory());
        this.checkHealthBtn.addEventListener('click', () => this.checkHealth());
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) {
            this.showStatus('Por favor, digite uma mensagem.', 'error');
            return;
        }
        
        this.setLoading(true);
        
        try {
            // Adicionar mensagem do usuário imediatamente
            this.addMessage(message, 'user');
            this.messageInput.value = '';
            
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Adicionar resposta do assistente
                this.addMessage(data.assistant_message.content, 'assistant');
                this.scrollToBottom();
            } else {
                this.showStatus(data.error || 'Erro ao enviar mensagem', 'error');
                // Remover mensagem do usuário em caso de erro
                this.removeLastUserMessage();
            }
            
        } catch (error) {
            console.error('Erro:', error);
            this.showStatus('Erro de conexão. Tente novamente.', 'error');
            this.removeLastUserMessage();
        } finally {
            this.setLoading(false);
        }
    }
    
    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const now = new Date();
        const timeString = now.toLocaleTimeString('pt-BR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        messageDiv.innerHTML = `
            <div class="message-content">${this.escapeHtml(content)}</div>
            <div class="message-time">${timeString}</div>
        `;
        
        // Remover mensagem de boas-vindas se existir
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    removeLastUserMessage() {
        const userMessages = this.chatMessages.querySelectorAll('.user-message');
        if (userMessages.length > 0) {
            userMessages[userMessages.length - 1].remove();
        }
    }
    
    async loadHistory() {
        try {
            const response = await fetch('/history');
            const data = await response.json();
            
            if (data.success) {
                this.chatMessages.innerHTML = '';
                
                if (data.messages.length === 0) {
                    this.chatMessages.innerHTML = `
                        <div class="welcome-message">
                            <p>Olá! Sou seu assistente de IA. Como posso ajudá-lo hoje?</p>
                        </div>
                    `;
                } else {
                    data.messages.forEach(msg => {
                        this.addMessage(msg.content, msg.message_type);
                    });
                }
                
                this.scrollToBottom();
            }
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
            this.showStatus('Erro ao carregar histórico', 'error');
        }
    }
    
    clearChat() {
        if (confirm('Tem certeza que deseja limpar o chat? O histórico será perdido.')) {
            this.chatMessages.innerHTML = `
                <div class="welcome-message">
                    <p>Olá! Sou seu assistente de IA. Como posso ajudá-lo hoje?</p>
                </div>
            `;
            this.showStatus('Chat limpo com sucesso', 'success');
        }
    }
    
    async checkHealth() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            if (data.backend === 'healthy') {
                this.showStatus('Sistema saudável! Backend conectado.', 'success');
            } else {
                this.showStatus('Backend offline. Verifique se o servidor está rodando.', 'error');
            }
        } catch (error) {
            this.showStatus('Erro ao verificar saúde do sistema', 'error');
        }
    }
    
    setLoading(loading) {
        if (loading) {
            this.sendButton.disabled = true;
            this.loadingSpinner.style.display = 'block';
            this.sendButton.querySelector('span').textContent = 'Enviando...';
        } else {
            this.sendButton.disabled = false;
            this.loadingSpinner.style.display = 'none';
            this.sendButton.querySelector('span').textContent = 'Enviar';
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    showStatus(message, type) {
        const statusDiv = document.getElementById('statusMessage');
        statusDiv.textContent = message;
        statusDiv.className = `status-message show status-${type}`;
        
        setTimeout(() => {
            statusDiv.classList.remove('show');
        }, 5000);
    }
    
    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;")
            .replace(/\n/g, '<br>');
    }
}

// Inicializar aplicação quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
