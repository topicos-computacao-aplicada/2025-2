# Instruções do Agente de Resumos de arquivos

## 1. Aplicação Backend

Prepara ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instala as dependências

```bash
pip3 install -r requirements.txt
```

Crie o arquivo .env com a variável OPENAI_API_KEY

Executa o servidor Uvicorn
```bash
uvicorn backend.app.main:app
```

## 2. Aplicação Frontend

```bash
python3 frontend/client.py
```