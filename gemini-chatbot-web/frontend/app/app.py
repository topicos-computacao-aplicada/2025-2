# frontend/app/app.py
"""
Aplicação Flask frontend para o Gemini ChatBot
"""

from flask import Flask, render_template, request, jsonify, session
import requests
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# Configurações
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def get_session_id():
    """
    Obtém ou cria um ID de sessão para o usuário
    """
    if 'session_id' not in session:
        session['session_id'] = f"web_{uuid.uuid4().hex[:8]}"
    
    return session['session_id']

@app.route('/')
def index():
    """Página principal do chat"""
    session_id = get_session_id()
    return render_template('index.html', session_id=session_id)

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint para enviar mensagem para o chatbot"""
    try:
        user_message = request.json.get('message', '').strip()
        session_id = get_session_id()
        
        if not user_message:
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        # Enviar mensagem para o backend
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={
                "session_id": session_id,
                "content": user_message
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'user_message': data['user_message'],
                'assistant_message': data['assistant_message']
            })
        else:
            return jsonify({
                'error': 'Erro ao comunicar com o servidor'
            }), 500
            
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'Não foi possível conectar ao servidor. Verifique se o backend está rodando.'
        }), 503
    except Exception as e:
        return jsonify({
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/history')
def get_history():
    """Obtém o histórico do chat"""
    try:
        session_id = get_session_id()
        
        response = requests.get(f"{BACKEND_URL}/sessions/{session_id}/history")
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'messages': data['messages']
            })
        elif response.status_code == 404:
            return jsonify({
                'success': True,
                'messages': []
            })
        else:
            return jsonify({
                'error': 'Erro ao obter histórico'
            }), 500
            
    except Exception as e:
        return jsonify({
            'error': f'Erro ao obter histórico: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    """Health check do frontend e verificação do backend"""
    try:
        # Verificar backend
        backend_response = requests.get(f"{BACKEND_URL}/health")
        backend_status = backend_response.status_code == 200
        
        return jsonify({
            'frontend': 'healthy',
            'backend': 'healthy' if backend_status else 'unhealthy',
            'backend_details': backend_response.json() if backend_status else None
        })
    except:
        return jsonify({
            'frontend': 'healthy',
            'backend': 'unhealthy'
        }), 503

if __name__ == '__main__':
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5001))
    debug = os.getenv("DEBUG", "False") == "True"
    
    app.run(host=host, port=port, debug=debug)
