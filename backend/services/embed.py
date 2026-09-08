from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions
from backend.celery_app import celery_app
from backend.models.document import Document
from backend.config import CELERY_DATABASE_URL

sync_engine = create_engine(CELERY_DATABASE_URL)
SyncSession = sessionmaker(bind=sync_engine)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
chroma = chromadb.PersistentClient(path="./chroma_data")
chroma_collection = chroma.get_or_create_collection("documents", embedding_function=embedding_fn)


@celery_app.task
def embed_file(document_id: str):
    with SyncSession() as session:
        document = session.get(Document, document_id)
        if document is None:
            return

        try:
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

            chroma_collection.add(documents=texts, metadatas=metadatas, ids=ids)

            document.status = "ready"
        except Exception as e:
            document.status = "failed"
            document.error_message = str(e)

        session.commit()


def delete_embedding(chat_id):
    chroma_collection.delete(where={"chat_id": str(chat_id)})