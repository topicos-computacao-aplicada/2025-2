from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, files, chat

# Cria as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Agent Backend")

app.include_router(auth.router)
app.include_router(files.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "AI Agent Backend rodando..."}