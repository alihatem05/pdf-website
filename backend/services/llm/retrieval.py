from dataclasses import dataclass
from typing import Any
from backend.services.llm.embed import get_chat_collection
from uuid import UUID

@dataclass(frozen=True)
class RetrievedChunk:
    content: str
    metadata: dict[str, Any]


def retrieve(chat_id: UUID | str, question: str, top_k: int = 4):
    if top_k < 1:
        return []

    try:
        collection = get_chat_collection(chat_id)
    except Exception:
        return []

    result = collection.query(
        query_texts=[question],
        n_results=top_k,
    )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    return [
        RetrievedChunk(content=content, metadata=metadata or {})
        for content, metadata in zip(documents, metadatas)
        if content
    ]