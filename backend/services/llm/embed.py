from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.celery_app import celery_app
from backend.config import CELERY_DATABASE_URL
from backend.models.document import Document

sync_engine = create_engine(CELERY_DATABASE_URL)
SyncSession = sessionmaker(bind=sync_engine)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
chroma = chromadb.PersistentClient(path=str(Path(__file__).resolve().parents[2] / "chroma_data"))


def get_chat_collection(chat_id):
    return chroma.get_or_create_collection(
        f"chat_{chat_id}",
        embedding_function=embedding_fn,
    )

@celery_app.task
def embed_file(document_id: str, chat_id: str):
    with SyncSession() as session:
        document = session.get(Document, document_id)
        if document is None:
            return

        try:
            collection = get_chat_collection(chat_id)
            pages = PyPDFLoader(document.storage_path).load()
            chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(pages)

            texts = [c.page_content for c in chunks]
            metadatas = [
                {
                    "document_id": str(document.id),
                    "chat_id": str(document.chat_id),
                    "page": c.metadata.get("page"),
                }
                for c in chunks
            ]
            ids = [f"{document.id}-{i}" for i in range(len(chunks))]

            collection.add(documents=texts, metadatas=metadatas, ids=ids)

            document.status = "ready"
        except Exception as e:
            document.status = "failed"
            document.error_message = str(e)

        session.commit()

def delete_embedding(chat_id):
    try:
        chroma.delete_collection(f"chat_{chat_id}")
    except Exception:
        pass
