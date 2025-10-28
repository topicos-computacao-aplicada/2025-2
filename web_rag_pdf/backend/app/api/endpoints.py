from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import uuid
import traceback

from ..db.database import get_db
from ..db import crud, schemas
from ..core.config import settings

router = APIRouter()

def get_pdf_processor():
    from ..services.pdf_processor import PDFProcessor
    return PDFProcessor()

def get_vector_db_service():
    from ..services.vector_db_service import VectorDBService
    return VectorDBService()

@router.post("/upload-pdf/", response_model=schemas.Document)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        print(f"📥 Iniciando upload do arquivo: {file.filename}")
        
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Apenas arquivos PDF são permitidos")

        # Garantir que o diretório de upload existe
        os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)
        
        file_location = os.path.join(settings.DOCUMENTS_DIR, file.filename)
        print(f"💾 Salvando arquivo em: {file_location}")
        
        with open(file_location, "wb+") as file_object:
            content = await file.read()
            file_object.write(content)

        # Processar PDF
        pdf_processor = get_pdf_processor()
        print("🔍 Extraindo texto do PDF...")
        full_text = pdf_processor.extract_text(file_location)
        
        if not full_text.strip():
            raise HTTPException(status_code=400, detail="Não foi possível extrair texto do PDF. O arquivo pode estar vazio ou corrompido.")
        
        print(f"📝 Texto extraído: {len(full_text)} caracteres")
        
        # Criar chunks
        print("✂️  Criando chunks do texto...")
        chunks = pdf_processor.chunk_text(full_text)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Não foi possível criar chunks do texto extraído.")

        print(f"📦 Criados {len(chunks)} chunks")
        
        # Gerar nome único para a coleção
        collection_name = f"doc_{uuid.uuid4().hex}"
        print(f"🏷️  Nome da coleção: {collection_name}")
        
        # Preparar dados para o ChromaDB
        chunk_ids = [f"chunk_{i}_{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]
        metadatas = [{"source": file.filename, "chunk_id": id, "chunk_index": i} for i, id in enumerate(chunk_ids)]

        # Adicionar ao ChromaDB
        vector_db_service = get_vector_db_service()
        print("🗄️  Adicionando documentos ao ChromaDB...")
        
        vector_db_service.add_documents_to_collection(
            collection_name=collection_name,
            texts=chunks,
            metadatas=metadatas,
            ids=chunk_ids
        )

        # Salvar metadados no SQLite
        print("💾 Salvando metadados no banco de dados...")
        db_document = crud.create_document(
            db=db,
            document=schemas.DocumentCreate(
                filename=file.filename,
                filepath=file_location,
                chroma_collection_name=collection_name
            )
        )
        
        print(f"✅ Upload concluído com sucesso! Documento ID: {db_document.id}")
        return db_document
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro durante upload: {str(e)}")
        print(f"🔍 Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.post("/ask-pdf/", response_model=schemas.ChatResponse)
async def ask_pdf(chat_request: schemas.ChatRequest, db: Session = Depends(get_db)):
    try:
        db_document = crud.get_document(db, chat_request.document_id)
        if not db_document:
            raise HTTPException(status_code=404, detail="Documento não encontrado.")

        from ..services.rag_service import RAGService
        from ..services.vector_db_service import VectorDBService
        
        vector_db_service = VectorDBService()
        rag_service = RAGService(vector_db_service)
        
        answer, source_chunks = rag_service.generate_response(
            document_id=chat_request.document_id,
            collection_name=db_document.chroma_collection_name,
            question=chat_request.question
        )
        return schemas.ChatResponse(answer=answer, source_chunks=source_chunks)
        
    except Exception as e:
        print(f"❌ Erro durante consulta: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")

@router.get("/documents/", response_model=list[schemas.Document])
async def get_documents(db: Session = Depends(get_db)):
    documents = crud.get_all_documents(db)
    return documents

@router.get("/documents/{document_id}", response_model=schemas.Document)
async def get_document_details(document_id: int, db: Session = Depends(get_db)):
    document = crud.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return document