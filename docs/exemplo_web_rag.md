# Projeto Web RAG

Projetar e implementar um sistema RAG que permite aos usuários interagir com seus próprios documentos PDF.

Este será um projeto que aplica boas práticas de Engenharia de IA e Engenharia de Software, enfatizando modularidade, escalabilidade e manutenibilidade.

### **Objetivo da Aplicação:**

Desenvolver uma aplicação web onde um usuário pode fazer upload de um arquivo PDF e, em seguida, fazer perguntas em linguagem natural sobre o conteúdo desse PDF, obtendo respostas precisas e 
contextualizadas graças ao RAG.

---

### **Arquitetura Proposta:**

Vamos adotar uma arquitetura de microserviços simplificada, com um backend (FastAPI) para lógica de negócio e IA, e um frontend (Flask) para a interface do usuário.

*   **Frontend (Flask):**
    *   Responsável pela interface do usuário (HTML, CSS).
    *   Gerencia o upload de arquivos e a submissão de perguntas.
    *   Consome a API do Backend via `requests`.
*   **Backend (FastAPI):**
    *   API RESTful para upload de documentos e processamento de perguntas.
    *   **Armazenamento de Metadados/Documentos:** SQLite com SQLAlchemy (ORM).
    *   **Processamento de PDF:** `pypdf`.
    *   **Geração de Embeddings e Banco de Dados Vetorial:** ChromaDB.
    *   **Modelo de Linguagem (LLM):** Gemini (via API da Google).
    *   **Orquestração RAG:** Lógica para chunking, embedding, retrieval e augmentation.

---

### **Passo a Passo da Implementação:**

Vamos dividir o projeto em módulos lógicos para facilitar a compreensão e a implementação.

#### **0. Configuração Inicial e Estrutura do Projeto**

Primeiro, vamos organizar nosso projeto e preparar os ambientes.

1.  **Estrutura de Diretórios:**

    ```
    rag_pdf_app/
    ├── backend/
    │   ├── app/
    │   │   ├── api/
    │   │   │   ├── __init__.py
    │   │   │   └── endpoints.py    # Rotas da API (upload, chat)
    │   │   ├── core/
    │   │   │   ├── __init__.py
    │   │   │   ├── config.py       # Variáveis de ambiente, configurações
    │   │   │   └── security.py     # (Opcional, para chaves de API, etc.)
    │   │   ├── db/
    │   │   │   ├── __init__.py
    │   │   │   ├── database.py     # Inicialização do SQLAlchemy
    │   │   │   ├── models.py       # Modelos SQLAlchemy
    │   │   │   └── crud.py         # Operações CRUD
    │   │   ├── services/
    │   │   │   ├── __init__.py
    │   │   │   ├── pdf_processor.py # Lógica para extrair texto, chunking
    │   │   │   ├── embedding_service.py # Geração de embeddings
    │   │   │   ├── vector_db_service.py # Interação com ChromaDB
    │   │   │   └── rag_service.py  # Orquestração do RAG e LLM
    │   │   └── main.py             # Instância principal do FastAPI
    │   ├── tests/                  # Testes para o backend
    │   └── requirements.txt        # Dependências do backend
    │
    ├── frontend/
    │   ├── static/
    │   │   ├── css/
    │   │   │   └── style.css       # Estilos
    │   │   └── js/                 # (Opcional) Scripts JS
    │   ├── templates/
    │   │   ├── base.html
    │   │   ├── index.html          # Página inicial/upload
    │   │   └── chat.html           # Página de chat com documento
    │   ├── app.py                  # Instância principal do Flask
    │   └── requirements.txt        # Dependências do frontend
    │
    └── .env                        # Variáveis de ambiente (chaves de API)
    ```

2.  **Configuração de Ambientes Virtuais e Dependências:**

    *   **Crie um arquivo `.env` na raiz do projeto:**
        ```
        GEMINI_API_KEY="SUA_CHAVE_API_GOOGLE_GEMINI"
        ```
        (Obtenha sua chave API Gemini em [Google AI Studio](https://aistudio.google.com/app/apikey)).

    *   **Backend:**
        ```bash
        cd rag_pdf_app/backend
        python -m venv venv
        source venv/bin/activate  # ou `.\venv\Scripts\activate` no Windows
        pip install fastapi uvicorn "python-multipart" sqlalchemy pypdf chromadb google-generativeai python-dotenv "sentence-transformers>=2.2.0"
        pip freeze > requirements.txt
        ```
        *`sentence-transformers` será usado para embeddings. Embora Gemini possa gerar embeddings, é comum usar um modelo dedicado para chunks, e depois o mesmo modelo para a query.*

    *   **Frontend:**
        ```bash
        cd rag_pdf_app/frontend
        python -m venv venv
        source venv/bin/activate  # ou `.\venv\Scripts\activate` no Windows
        pip install Flask requests python-dotenv
        pip freeze > requirements.txt
        ```

#### **1. Implementação do Backend (FastAPI)**

Vamos construir a espinha dorsal da nossa aplicação.

##### **1.1. Configuração Básica e Variáveis de Ambiente (`backend/app/core/`)**

*   `backend/app/core/config.py`:
    ```python
    import os
    from dotenv import load_dotenv

    load_dotenv()

    class Settings:
        GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
        DATABASE_URL: str = "sqlite:///./sql_app.db" # Caminho para o SQLite DB
        DOCUMENTS_DIR: str = "uploaded_documents" # Diretório para armazenar PDFs
        CHROMA_DB_PATH: str = "./chroma_db" # Caminho para o ChromaDB
        EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2" # Modelo de embedding

    settings = Settings()
    ```

*   `backend/app/main.py`:
    ```python
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from .api import endpoints
    from .core.config import settings
    import os

    # Crie o diretório para uploads se não existir
    os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)

    app = FastAPI(
        title="RAG PDF API",
        description="API para upload de PDFs e perguntas usando RAG com Gemini.",
        version="1.0.0",
    )

    # Configuração de CORS para permitir comunicação com o frontend Flask
    origins = [
        "http://localhost:5000",  # Endereço do nosso frontend Flask
        # Adicione outros domínios se for necessário em produção
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(endpoints.router, prefix="/api")

    @app.get("/")
    async def root():
        return {"message": "Bem-vindo à RAG PDF API! Acesse /api/docs para a documentação da API."}
    ```

##### **1.2. Banco de Dados Relacional (SQLite + SQLAlchemy) (`backend/app/db/`)**

*   `backend/app/db/database.py`:
    ```python
    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    from ..core.config import settings

    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} # Necessário para SQLite
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()

    # Função para obter uma sessão de banco de dados
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    ```

*   `backend/app/db/models.py`:
    ```python
    from sqlalchemy import Column, Integer, String, DateTime
    from sqlalchemy.sql import func
    from .database import Base

    class Document(Base):
        __tablename__ = "documents"

        id = Column(Integer, primary_key=True, index=True)
        filename = Column(String, index=True)
        filepath = Column(String)
        uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
        chroma_collection_name = Column(String, unique=True, index=True) # Nome da coleção no ChromaDB

    # Para criar as tabelas no banco de dados na inicialização
    def create_db_and_tables():
        Base.metadata.create_all(bind=engine)
    from .database import engine # Importar engine aqui para usar create_all
    create_db_and_tables() # Chamar na inicialização do app ou em main.py
    ```
    *Obs: A chamada `create_db_and_tables()` deve ser feita uma vez ao iniciar o aplicativo, por exemplo, em `main.py` após a criação da instância do FastAPI.*

*   `backend/app/db/crud.py`:
    ```python
    from sqlalchemy.orm import Session
    from . import models, schemas # Assumindo que teremos schemas Pydantic

    def create_document(db: Session, document: schemas.DocumentCreate):
        db_document = models.Document(
            filename=document.filename,
            filepath=document.filepath,
            chroma_collection_name=document.chroma_collection_name
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document

    def get_document(db: Session, document_id: int):
        return db.query(models.Document).filter(models.Document.id == document_id).first()

    def get_document_by_collection_name(db: Session, collection_name: str):
        return db.query(models.Document).filter(models.Document.chroma_collection_name == collection_name).first()

    def get_all_documents(db: Session):
        return db.query(models.Document).all()
    ```

*   **Schemas Pydantic (`backend/app/db/schemas.py`):**
    ```python
    from pydantic import BaseModel
    from datetime import datetime
    from typing import Optional

    class DocumentBase(BaseModel):
        filename: str
        chroma_collection_name: str

    class DocumentCreate(DocumentBase):
        filepath: str

    class Document(DocumentBase):
        id: int
        filepath: str
        uploaded_at: datetime

        class Config:
            orm_mode = True

    class ChatRequest(BaseModel):
        document_id: int
        question: str

    class ChatResponse(BaseModel):
        answer: str
        source_chunks: Optional[list] = None
    ```

##### **1.3. Serviços de Processamento de Documentos e RAG (`backend/app/services/`)**

*   `backend/app/services/pdf_processor.py`:
    ```python
    from pypdf import PdfReader
    import os
    from typing import List
    from langchain.text_splitter import RecursiveCharacterTextSplitter # Ótima para chunking

    class PDFProcessor:
        def extract_text(self, pdf_path: str) -> str:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or "" # Adiciona texto de cada página
            return text

        def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                add_start_index=True,
            )
            chunks = [doc.page_content for doc in text_splitter.create_documents()]
            return chunks
    ```

*   `backend/app/services/embedding_service.py`:
    ```python
    from sentence_transformers import SentenceTransformer
    from typing import List

    class EmbeddingService:
        def __init__(self, model_name: str):
            self.model = SentenceTransformer(model_name)

        def generate_embeddings(self, texts: List) -> List[List]:
            return self.model.encode(texts).tolist()

        def generate_embedding(self, text: str) -> List:
            return self.model.encode(text).tolist()
    ```

*   `backend/app/services/vector_db_service.py`:
    ```python
    import chromadb
    from chromadb.utils import embedding_functions
    from typing import List, Dict
    from ..core.config import settings
    from .embedding_service import EmbeddingService

    class VectorDBService:
        def __init__(self, embedding_service: EmbeddingService):
            self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
            # Usar um embedding_function do ChromaDB que utilize nosso EmbeddingService
            # Para simplificar, vamos passar o modelo de embedding como str ou criar uma função customizada
            # Para este exemplo, vamos usar o embedding_functions.SentenceTransformerEmbeddingFunction
            # e garantir que ele esteja configurado com o mesmo modelo
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=settings.EMBEDDING_MODEL_NAME
            )
            self.embedding_service = embedding_service # Manter referência ao nosso serviço

        def create_collection(self, collection_name: str):
            try:
                collection = self.client.create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function # Usar a função de embedding configurada
                )
                return collection
            except Exception as e:
                print(f"Error creating collection {collection_name}: {e}")
                return self.client.get_collection(name=collection_name, embedding_function=self.embedding_function) # Tenta obter se já existe

        def get_collection(self, collection_name: str):
            return self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function # Garante que a função de embedding é a mesma
            )

        def add_documents_to_collection(self, collection_name: str, texts: List, metadatas: List[Dict], ids: List):
            collection = self.get_collection(collection_name)
            # ChromaDB irá gerar embeddings automaticamente se uma embedding_function for fornecida na coleção
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

        def query_collection(self, collection_name: str, query_text: str, n_results: int = 5) -> List:
            collection = self.get_collection(collection_name)
            # A query_texts é vetorizada automaticamente pela embedding_function da coleção
            results = collection.query(
                query_texts=,
                n_results=n_results
            )
            return results['documents'][0] if results and results['documents'] else []
    ```
    *Nota: A `embedding_function` do ChromaDB simplifica a integração. O `self.embedding_service` ainda pode ser útil para gerar embeddings de queries antes de passar para o ChromaDB se a função de 
embedding padrão da coleção não for usada diretamente na query.*

*   `backend/app/services/rag_service.py`:
    ```python
    import google.generativeai as genai
    from typing import List
    from ..core.config import settings
    from .vector_db_service import VectorDBService
    from .embedding_service import EmbeddingService

    class RAGService:
        def __init__(self, vector_db_service: VectorDBService, embedding_service: EmbeddingService):
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro') # Ou 'gemini-1.5-pro-latest'
            self.vector_db_service = vector_db_service
            self.embedding_service = embedding_service

        def generate_response(self, document_id: int, collection_name: str, question: str) -> (str, List):
            # 1. Recuperação (Retrieval)
            # O query_collection já usa o embedding_function da coleção para a query_text
            relevant_chunks = self.vector_db_service.query_collection(
                collection_name=collection_name,
                query_text=question,
                n_results=5 # Ajuste conforme a necessidade
            )

            if not relevant_chunks:
                return "Não consegui encontrar informações relevantes no documento para responder à sua pergunta.", []

            # 2. Aumento (Augmentation)
            context = "\n".join(relevant_chunks)
            prompt = f"""Você é um assistente de IA prestativo e preciso, treinado para responder perguntas com base em um contexto fornecido.
            Responda à pergunta do usuário APENAS com as informações contidas no contexto abaixo.
            Se a resposta não puder ser encontrada no contexto, responda "Não consegui encontrar a resposta no documento fornecido.".

            Contexto:
            {context}

            Pergunta do usuário: {question}

            Resposta:"""

            # 3. Geração (Generation)
            try:
                response = self.model.generate_content(prompt)
                return response.text, relevant_chunks
            except Exception as e:
                print(f"Erro ao gerar resposta com Gemini: {e}")
                return "Ocorreu um erro ao processar sua pergunta.", []
    ```

##### **1.4. Endpoints da API (FastAPI) (`backend/app/api/endpoints.py`)**

*   `backend/app/api/endpoints.py`:
    ```python
    from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
    from sqlalchemy.orm import Session
    from ..db.database import get_db
    from ..db import crud, schemas, models
    from ..core.config import settings
    from ..services.pdf_processor import PDFProcessor
    from ..services.embedding_service import EmbeddingService
    from ..services.vector_db_service import VectorDBService
    from ..services.rag_service import RAGService
    import os
    import uuid # Para gerar IDs únicos para coleções

    router = APIRouter()

    # Inicializa os serviços
    pdf_processor = PDFProcessor()
    embedding_service = EmbeddingService(settings.EMBEDDING_MODEL_NAME)
    vector_db_service = VectorDBService(embedding_service)
    rag_service = RAGService(vector_db_service, embedding_service)

    # Garante que as tabelas do DB são criadas
    models.create_db_and_tables()

    @router.post("/upload-pdf/", response_model=schemas.Document)
    async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
        # 1. Salvar o arquivo PDF
        file_location = os.path.join(settings.DOCUMENTS_DIR, file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        # 2. Extrair texto do PDF
        full_text = pdf_processor.extract_text(file_location)

        # 3. Chunking do texto
        chunks = pdf_processor.chunk_text(full_text)
        if not chunks:
            raise HTTPException(status_code=400, detail="Não foi possível extrair texto ou criar chunks do PDF.")

        # 4. Gerar um nome de coleção único para o ChromaDB
        collection_name = f"doc_{uuid.uuid4().hex}"

        # 5. Adicionar chunks ao ChromaDB
        # Os IDs dos chunks podem ser gerados sequencialmente ou com UUIDs
        chunk_ids = 
        metadatas = [{"source": file.filename, "chunk_id": id} for id in chunk_ids]

        vector_db_service.add_documents_to_collection(
            collection_name=collection_name,
            texts=chunks,
            metadatas=metadatas,
            ids=chunk_ids
        )

        # 6. Salvar metadados do documento no SQLite
        db_document = crud.create_document(
            db=db,
            document=schemas.DocumentCreate(
                filename=file.filename,
                filepath=file_location,
                chroma_collection_name=collection_name
            )
        )
        return db_document

    @router.post("/ask-pdf/", response_model=schemas.ChatResponse)
    async def ask_pdf(chat_request: schemas.ChatRequest, db: Session = Depends(get_db)):
        # 1. Obter metadados do documento
        db_document = crud.get_document(db, chat_request.document_id)
        if not db_document:
            raise HTTPException(status_code=404, detail="Documento não encontrado.")

        # 2. Chamar o serviço RAG
        answer, source_chunks = rag_service.generate_response(
            document_id=chat_request.document_id,
            collection_name=db_document.chroma_collection_name,
            question=chat_request.question
        )
        return schemas.ChatResponse(answer=answer, source_chunks=source_chunks)

    @router.get("/documents/", response_model=list)
    async def get_documents(db: Session = Depends(get_db)):
        documents = crud.get_all_documents(db)
        return documents

    @router.get("/documents/{document_id}", response_model=schemas.Document)
    async def get_document_details(document_id: int, db: Session = Depends(get_db)):
        document = crud.get_document(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento não encontrado.")
        return document
    ```

##### **Para rodar o Backend:**

No diretório `rag_pdf_app/backend`, execute:
```bash
uvicorn app.main:app --reload --port 8000
```
Isso iniciará o servidor FastAPI na porta 8000. Você pode acessar a documentação interativa em `http://localhost:8000/api/docs`.

---

#### **2. Implementação do Frontend (Flask)**

Agora, vamos criar a interface do usuário para interagir com nossa API.

##### **2.1. Estrutura de Templates e Estilos (`frontend/`)**

*   `frontend/templates/base.html`:
    ```html
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{% block title %}RAG PDF App{% endblock %}</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    </head>
    <body>
        <div class="container">
            {% block content %}{% endblock %}
        </div>
    </body>
    </html>
    ```

*   `frontend/templates/index.html`:
    ```html
    {% extends "base.html" %}

    {% block title %}Upload PDF{% endblock %}

    {% block content %}
    <h1>Bem-vindo ao RAG PDF App</h1>
    <p>Faça upload de um documento PDF e comece a fazer perguntas sobre ele!</p>

    <div class="card">
        <h2>Upload de PDF</h2>
        <form action="{{ url_for('upload') }}" method="post" enctype="multipart/form-data">
            <input type="file" name="pdf_file" accept=".pdf" required>
            <button type="submit">Upload</button>
        </form>
        {% if message %}
            <p class="message">{{ message }}</p>
        {% endif %}
    </div>

    <div class="card">
        <h2>Documentos Enviados</h2>
        {% if documents %}
        <ul>
            {% for doc in documents %}
            <li>
                <a href="{{ url_for('chat_document', doc_id=doc.id) }}">{{ doc.filename }}</a>
                (ID: {{ doc.id }}) - Enviado em: {{ doc.uploaded_at.strftime('%d/%m/%Y %H:%M') }}
            </li>
            {% endfor %}
        </ul>
        {% else %}
        <p>Nenhum documento enviado ainda.</p>
        {% endif %}
    </div>
    {% endblock %}
    ```

*   `frontend/templates/chat.html`:
    ```html
    {% extends "base.html" %}

    {% block title %}Chat com {{ document.filename }}{% endblock %}

    {% block content %}
    <h1>Chat com: {{ document.filename }}</h1>
    <p>ID do Documento: {{ document.id }}</p>

    <div class="chat-container">
        <div id="chat-messages" class="chat-messages">
            <!-- As mensagens serão adicionadas aqui via JS ou diretamente do Flask -->
            {% if chat_history %}
                {% for entry in chat_history %}
                    <div class="message user-message">
                        <strong>Você:</strong> {{ entry.question }}
                    </div>
                    <div class="message bot-message">
                        <strong>Assistente:</strong> {{ entry.answer }}
                        {% if entry.source_chunks %}
                            <details>
                                <summary>Trechos da Fonte</summary>
                                <p>{{ entry.source_chunks | join('<br>') | safe }}</p>
                            </details>
                        {% endif %}
                    </div>
                {% endfor %}
            {% endif %}
        </div>

        <div class="chat-input">
            <form id="chat-form" action="{{ url_for('ask_document', doc_id=document.id) }}" method="post">
                <input type="text" name="question" placeholder="Faça sua pergunta aqui..." required>
                <button type="submit">Perguntar</button>
            </form>
            {% if message %}
                <p class="message">{{ message }}</p>
            {% endif %}
        </div>
    </div>
    {% endblock %}
    ```

*   `frontend/static/css/style.css`:
    ```css
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        margin: 0;
        padding: 20px;
        background-color: #f4f4f4;
        color: #333;
    }

    .container {
        max-width: 900px;
        margin: 0 auto;
        background: #fff;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }

    h1, h2 {
        color: #0056b3;
        text-align: center;
    }

    .card {
        background-color: #e9f7ff;
        border: 1px solid #cceeff;
        border-radius: 5px;
        padding: 20px;
        margin-bottom: 20px;
    }

    form {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }

    form input,
    form input {
        flex-grow: 1;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
    }

    form button {
        padding: 10px 15px;
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    form button:hover {
        background-color: #0056b3;
    }

    ul {
        list-style: none;
        padding: 0;
    }

    li {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        padding: 10px;
        margin-bottom: 5px;
        border-radius: 4px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    li a {
        color: #007bff;
        text-decoration: none;
        font-weight: bold;
    }

    li a:hover {
        text-decoration: underline;
    }

    .message {
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
    }

    .message.user-message {
        background-color: #e0f7fa;
        text-align: right;
    }

    .message.bot-message {
        background-color: #f0f0f0;
        text-align: left;
    }

    .message.error {
        color: red;
        font-weight: bold;
    }

    .chat-container {
        border: 1px solid #ddd;
        border-radius: 8px;
        overflow: hidden;
        margin-top: 20px;
        display: flex;
        flex-direction: column;
        height: 600px; /* Altura fixa para o chat */
    }

    .chat-messages {
        flex-grow: 1;
        padding: 15px;
        overflow-y: auto; /* Scroll para mensagens */
        background-color: #fafafa;
    }

    .chat-input {
        padding: 15px;
        border-top: 1px solid #eee;
        background-color: #f0f0f0;
    }

    .chat-input form {
        margin-top: 0;
    }

    details {
        margin-top: 10px;
        font-size: 0.9em;
        color: #555;
    }

    details summary {
        cursor: pointer;
        font-weight: bold;
    }

    details p {
        background-color: #e8e8e8;
        padding: 8px;
        border-radius: 4px;
        margin-top: 5px;
    }
    ```

##### **2.2. Aplicação Flask (`frontend/app.py`)**

```python
from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import os
from dotenv import load_dotenv

load_dotenv() # Carrega variáveis do .env

app = Flask(__name__)
app.secret_key = os.urandom(24) # Chave secreta para sessões

BACKEND_API_URL = "http://localhost:8000/api" # URL do nosso backend FastAPI

@app.route('/')
def index():
    try:
        response = requests.get(f"{BACKEND_API_URL}/documents/")
        response.raise_for_status() # Lança exceção para status HTTP de erro (4xx ou 5xx)
        documents = response.json()
    except requests.exceptions.RequestException as e:
        documents = []
        flash(f"Erro ao carregar documentos do backend: {e}", "error")

    # Inicia o histórico de chat para o index page (vazio por enquanto)
    session.setdefault('chat_history', {})
    return render_template('index.html', documents=documents)

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf_file' not in request.files:
        flash('Nenhum arquivo enviado!', 'error')
        return redirect(url_for('index'))

    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        flash('Nenhum arquivo selecionado!', 'error')
        return redirect(url_for('index'))

    if pdf_file and pdf_file.filename.endswith('.pdf'):
        try:
            files = {'file': (pdf_file.filename, pdf_file.read(), 'application/pdf')}
            response = requests.post(f"{BACKEND_API_URL}/upload-pdf/", files=files)
            response.raise_for_status()
            doc_info = response.json()
            flash(f'Documento "{doc_info["filename"]}" (ID: {doc_info["id"]}) enviado com sucesso!', 'success')
            return redirect(url_for('chat_document', doc_id=doc_info["id"]))
        except requests.exceptions.RequestException as e:
            flash(f"Erro ao enviar PDF: {e}", "error")
            return redirect(url_for('index'))
    else:
        flash('Formato de arquivo inválido. Por favor, envie um PDF.', 'error')
        return redirect(url_for('index'))

@app.route('/document/<int:doc_id>')
def chat_document(doc_id):
    try:
        response = requests.get(f"{BACKEND_API_URL}/documents/{doc_id}")
        response.raise_for_status()
        document = response.json()
    except requests.exceptions.RequestException as e:
        flash(f"Erro ao carregar documento: {e}", "error")
        return redirect(url_for('index'))

    # Inicializa o histórico de chat para este documento, se não existir
    if str(doc_id) not in session['chat_history']:
        session['chat_history'] = []

    return render_template('chat.html', document=document, chat_history=session['chat_history'])

@app.route('/document/<int:doc_id>/ask', methods=['POST'])
def ask_document(doc_id):
    question = request.form.get('question')
    if not question:
        flash('Por favor, digite uma pergunta.', 'error')
        return redirect(url_for('chat_document', doc_id=doc_id))

    try:
        payload = {"document_id": doc_id, "question": question}
        response = requests.post(f"{BACKEND_API_URL}/ask-pdf/", json=payload)
        response.raise_for_status()
        chat_response = response.json()

        # Armazena a pergunta e a resposta no histórico de chat da sessão
        if str(doc_id) not in session['chat_history']:
            session['chat_history'] = []
        session['chat_history'].append({
            'question': question,
            'answer': chat_response.get('answer', 'Nenhuma resposta fornecida.'),
            'source_chunks': chat_response.get('source_chunks', [])
        })
        session.modified = True # Sinaliza que a sessão foi modificada

    except requests.exceptions.RequestException as e:
        flash(f"Erro ao perguntar ao documento: {e}", "error")

    return redirect(url_for('chat_document', doc_id=doc_id))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

##### **Para rodar o Frontend:**

No diretório `rag_pdf_app/frontend`, execute:
```bash
python app.py
```
Isso iniciará o servidor Flask na porta 5000. Acesse `http://localhost:5000` no seu navegador.

---

### **Boas Práticas de Engenharia de IA e Engenharia de Software Aplicadas:**

1.  **Modularidade e Separação de Preocupações:**
    *   **Backend (FastAPI):** Dividido em `api`, `core`, `db`, `services`. Cada diretório tem uma responsabilidade clara (e.g., `services` lida com a lógica de negócio específica do RAG e PDF).
    *   **Frontend (Flask):** Lida exclusivamente com a apresentação e interação do usuário, delegando a lógica complexa ao backend.
    *   **Decoplamento:** Frontend e backend são separados, podendo ser desenvolvidos e escalados independentemente.

2.  **Gerenciamento de Dependências:**
    *   Uso de `venv` para isolar dependências.
    *   `requirements.txt` para replicar o ambiente.

3.  **Configuração Centralizada:**
    *   `backend/app/core/config.py` para todas as configurações de ambiente e parâmetros.
    *   Uso de `.env` para variáveis sensíveis (chaves de API), evitando hardcoding.

4.  **ORM (SQLAlchemy):**
    *   Abstrai a interação com o banco de dados (SQLite), tornando o código mais limpo e menos propenso a erros de SQL.
    *   Facilita a migração para outros bancos de dados relacionais no futuro.

5.  **Validação de Dados (Pydantic no FastAPI):**
    *   Os `schemas.py` definem a estrutura dos dados esperados para requisições e respostas, garantindo que a API seja robusta e fácil de usar.

6.  **Tratamento de Erros:**
    *   Uso de `HTTPException` no FastAPI para retornar erros padronizados.
    *   `try-except` blocos no Flask para capturar erros de rede (`requests.exceptions.RequestException`) e apresentar feedback ao usuário.
    *   Uso de `flash` no Flask para mensagens temporárias ao usuário.

7.  **Persistência de Dados:**
    *   **ChromaDB:** Especializado para armazenamento e busca de vetores, essencial para o "Retrieval" do RAG.
    *   **SQLite:** Para metadados de documentos, proporcionando uma solução leve e integrada.

8.  **APIs Bem Definidas:**
    *   FastAPI gera automaticamente a documentação OpenAPI/Swagger, tornando a API fácil de entender e consumir.
    *   Endpoints claros e concisos (`/upload-pdf`, `/ask-pdf`, `/documents`).

9.  **Segurança (Básico):**
    *   Gerenciamento de chaves de API via `.env`.
    *   CORS configurado para permitir comunicação controlada entre frontend e backend.
    *   Uso de `app.secret_key` para sessões Flask.

10. **Extensibilidade e Otimização de IA:**
    *   **Modelos de Embedding:** O serviço de embedding pode ser facilmente trocado (e.g., de `sentence-transformers` para o modelo de embedding do próprio Gemini, ou para um modelo customizado).
    *   **LLM:** Facilmente configurável para usar diferentes modelos Gemini ou outros LLMs compatíveis com a mesma interface.
    *   **Estratégias de Chunking:** O `PDFProcessor` usa `RecursiveCharacterTextSplitter`, mas pode ser expandido para diferentes lógicas de fragmentação.
    *   **Prompt Engineering:** O prompt no `rag_service.py` é projetado para ancorar a resposta do LLM no contexto, minimizando alucinações.
    *   **Otimizações RAG:** Abrimos portas para adicionar re-ranking, filtragem de metadados, ou busca híbrida como melhorias futuras.

---

### **Próximos Passos e Melhorias (Desafios para o Aluno!):**

*   **Autenticação e Autorização:** Implementar login de usuário e controle de acesso a documentos.
*   **Melhoria de UI/UX:** Adicionar spinners de carregamento, feedback em tempo real no chat, melhor estilização.
*   **Gerenciamento de Erros Mais Sofisticado:** Retornar mensagens de erro mais específicas do backend para o frontend.
*   **Dockerização:** Empacotar frontend e backend em contêineres Docker para facilitar a implantação.
*   **Deploy em Produção:** Usar Gunicorn/Uvicorn com Nginx/Apache para o backend, e um servidor web para o Flask (ou servi o Flask como um aplicativo WSGI atrás de um proxy).
*   **Monitoramento e Logging:** Implementar logging estruturado e métricas para observar o desempenho da aplicação e dos modelos de IA.
*   **Cache:** Implementar cache para embeddings ou respostas do LLM para perguntas frequentes.
*   **Testes:** Escrever testes unitários e de integração para garantir a funcionalidade e estabilidade do sistema.
*   **Redução de Custo/Escalabilidade:** Avaliar o uso de bancos de dados vetoriais gerenciados (Pinecone, Weaviate) e LLMs mais eficientes em custo para grandes volumes.
*   **Avaliação de RAG:** Como você mediria a qualidade das respostas do seu sistema RAG? (Relevância dos chunks, factualidade da resposta, etc.)

Com esta estrutura, vocês têm uma base sólida para construir uma aplicação web com RAG que é ao mesmo tempo funcional e segue princípios de engenharia de software e IA. Mãos à obra!
2025-10-26T12:16:02
