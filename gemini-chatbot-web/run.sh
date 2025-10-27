#!/bin/bash

# Script para executar o projeto Gemini ChatBot Web

echo "🚀 Iniciando Gemini ChatBot Web..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Por favor, instale Python 3.8 ou superior."
    exit 1
fi

# Verificar se as dependências estão instaladas
echo "📦 Verificando dependências..."

cd backend
if [ ! -d "venv" ]; then
    echo "🐍 Criando ambiente virtual..."
    python3 -m venv venv
fi

echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

echo "📥 Instalando dependências do backend..."
pip3 install -r requirements.txt

echo "🏃 Iniciando backend..."
python3 main.py &

BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

cd ../frontend
if [ ! -d "venv" ]; then
    echo "🐍 Criando ambiente virtual..."
    python3 -m venv venv
fi

echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

echo "📥 Instalando dependências do frontend..."
pip3 install -r requirements.txt

echo "⏳ Aguardando backend iniciar..."
sleep 5

echo "🌐 Iniciando frontend..."
python3 app/app.py

FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Função para encerrar processos
cleanup() {
    echo "🛑 Encerrando aplicação..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT

echo "✅ Aplicação rodando!"
echo "📱 Frontend: http://localhost:5001"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Pressione Ctrl+C para parar"

# Manter script rodando
wait