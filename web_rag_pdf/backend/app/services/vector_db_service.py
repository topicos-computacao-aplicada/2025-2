import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict
from ..core.config import settings

class VectorDBService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def create_collection(self, collection_name: str):
        try:
            # Tentar obter a coleção se existir
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            print(f"✅ Coleção '{collection_name}' já existe, reutilizando...")
            return collection
        except Exception:
            # Se não existir, criar nova coleção
            print(f"📝 Criando nova coleção: '{collection_name}'")
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            return collection

    def get_collection(self, collection_name: str):
        try:
            return self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
        except Exception as e:
            print(f"❌ Erro ao obter coleção '{collection_name}': {e}")
            # Se a coleção não existe, criá-la
            return self.create_collection(collection_name)

    def add_documents_to_collection(self, collection_name: str, texts: List[str], metadatas: List[Dict], ids: List[str]):
        try:
            # Garantir que a coleção existe antes de adicionar documentos
            collection = self.create_collection(collection_name)
            
            print(f"📄 Adicionando {len(texts)} chunks à coleção '{collection_name}'...")
            
            # Verificar se já existem documentos na coleção
            existing_count = collection.count()
            if existing_count > 0:
                print(f"⚠️  Coleção já contém {existing_count} documentos. Adicionando novos...")
            
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            print(f"✅ {len(texts)} documentos adicionados com sucesso à coleção '{collection_name}'")
            
        except Exception as e:
            print(f"❌ Erro ao adicionar documentos à coleção '{collection_name}': {e}")
            raise

    def query_collection(self, collection_name: str, query_text: str, n_results: int = 5) -> List[str]:
        try:
            collection = self.get_collection(collection_name)
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results['documents'][0] if results and results['documents'] else []
        except Exception as e:
            print(f"❌ Erro ao consultar coleção '{collection_name}': {e}")
            return []