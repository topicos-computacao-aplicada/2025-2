from sqlalchemy.orm import Session
from . import models, schemas

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
