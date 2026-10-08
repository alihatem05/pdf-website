import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from celery_app import celery_app
from config import CELERY_DATABASE_URL
from models.chunk import Chunk
from models.document import Document
from services.chat.storage import download_to_temp
from services.llm.embeddings import embed_texts

sync_engine = create_engine(CELERY_DATABASE_URL)
SyncSession = sessionmaker(bind=sync_engine)


@celery_app.task
def embed_file(document_id: str, chat_id: str):
    with SyncSession() as session:
        document = session.get(Document, document_id)
        if document is None:
            return

        path = None
        try:
            path = download_to_temp(document.id)
            pages = PyPDFLoader(path).load()
            chunks = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=100
            ).split_documents(pages)

            vectors = embed_texts([c.page_content for c in chunks])

            session.execute(delete(Chunk).where(Chunk.document_id == document.id))
            session.add_all([
                Chunk(
                    document_id=document.id,
                    chat_id=document.chat_id,
                    page=c.metadata.get("page"),
                    content=c.page_content,
                    embedding=v,
                )
                for c, v in zip(chunks, vectors)
            ])
            document.status = "ready"
        except Exception as e:
            session.rollback()
            document.status = "failed"
            document.error_message = str(e)
        finally:
            if path and os.path.exists(path):
                os.remove(path)

        session.commit()