from dataclasses import dataclass
from typing import Any
from backend.services.llm.embed import get_chat_vector_store
from uuid import UUID

@dataclass(frozen=True)
class RetrievedChunk:
    content: str
    metadata: dict[str, Any]


def retrieve(chat_id, question, top_k = 4, fetch_k = 20, lambda_mult = 0.5):
    if top_k < 1:
        return []

    vector_store = get_chat_vector_store(chat_id)

    documents = vector_store.max_marginal_relevance_search(
        question,
        k=top_k,
        fetch_k=fetch_k,
        lambda_mult=lambda_mult,
    )
    return [
        RetrievedChunk(content=document.page_content, metadata=document.metadata or {})
        for document in documents
        if document.page_content
    ]