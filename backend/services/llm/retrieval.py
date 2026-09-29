from dataclasses import dataclass
from typing import Any
from backend.services.llm.embed import get_chat_vector_store
from uuid import UUID


@dataclass(frozen=True)
class RetrievedChunk:
    content: str
    metadata: dict[str, Any]


def retrieve(
    chat_id,
    question,
    document_ids,
    top_k_by_document=None,
    document_names=None,
    top_k=10,
    fetch_k=20,
    lambda_mult=0.5,
):
    if top_k < 1 or not document_ids:
        return []

    vector_store = get_chat_vector_store(chat_id)
    top_k_by_document = top_k_by_document or {}
    document_names = document_names or {}

    chunks = []
    for document_id in document_ids:
        document_id = str(document_id)
        per_doc_k = top_k_by_document.get(document_id, top_k)
        if per_doc_k < 1:
            continue
        documents = vector_store.max_marginal_relevance_search(
            question,
            k=per_doc_k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
            filter={"document_id": str(document_id)},
        )
        chunks.extend(
            RetrievedChunk(
                content=document.page_content,
                metadata={
                    **(document.metadata or {}),
                    "document_id": document_id,
                    "filename": document_names.get(document_id)
                    or (document.metadata or {}).get("filename"),
                },
            )
            for document in documents
            if document.page_content
        )

    return chunks