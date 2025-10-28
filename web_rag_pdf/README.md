# RAG PDF App

Uma aplicação completa para upload de PDFs e perguntas sobre o conteúdo usando RAG (Retrieval-Augmented Generation) com FastAPI, Flask e Gemini.

## Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
pip3 install sentence-transformers
uvicorn app.main:app --port 8000
```

Em caso de problemas de incompatibilidade de bibliotecas com o ChromaDB:

```bash
pip install --upgrade pyarrow
uvicorn app.main:app --port 8000
pip uninstall chromadb
pip install chromadb
pip install --upgrade "datasets>=2.20.0"
```

## Frontend

```bash
cd frontend
pip3 install -r requirements.txt
python3 app.py
```