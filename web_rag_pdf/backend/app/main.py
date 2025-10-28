from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .api.endpoints import router
from .core.config import settings

os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)

app = FastAPI(
    title="RAG PDF API",
    description="API para upload de PDFs e perguntas usando RAG com Gemini.",
    version="1.0.0",
)

origins = [
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Bem-vindo à RAG PDF API! Acesse /api/docs para a documentação da API."}