import os
import uuid
import tempfile
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .rag_pdf import query_and_summarize

app = FastAPI(title="PDF Summarizer Backend")

# Se quiser chamar de outra máquina, pode abrir CORS:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "PDF Summarizer Backend rodando..."}

@app.post("/summary/pdf")
async def summarize_pdf(
    file: UploadFile = File(..., description="Arquivo PDF a ser resumido"),
    question: str = Form(..., description="Pergunta que orienta o resumo"),
    k: int = Form(6, description="Quantidade de chunks mais relevantes (top-k)"),
):
    # Verificação básica de tipo
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo .pdf")

    # Cria diretório temporário
    tmp_dir = tempfile.mkdtemp(prefix="pdf_upload_")
    tmp_path = os.path.join(tmp_dir, f"{uuid.uuid4()}_{file.filename}")

    # Salva o arquivo PDF no disco
    try:
        contents = await file.read()
        with open(tmp_path, "wb") as f:
            f.write(contents)

        # Roda o pipeline de RAG + resumo
        result = query_and_summarize(tmp_path, question, k=k)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar PDF: {e}")
    finally:
        # Limpa o arquivo temporário
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            if os.path.exists(tmp_dir):
                os.rmdir(tmp_dir)
        except Exception:
            # se der erro aqui, apenas ignoramos (não é crítico)
            pass

    # Compactar os chunks para não mandar tudo enorme
    chunks_preview: List[dict] = []
    for i, d in enumerate(result["matches"], start=1):
        page = d.metadata.get("page", "NA")
        snippet = d.page_content[:400]
        chunks_preview.append(
            {
                "index": i,
                "page": page,
                "snippet": snippet,
            }
        )

    return {
        "summary": result["summary"],
        "chunks": chunks_preview,
        "k": k,
        "num_chunks_returned": len(chunks_preview),
    }