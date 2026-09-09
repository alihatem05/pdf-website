from dataclasses import dataclass
from typing import Any
from backend.services.embed import chroma_collection
from uuid import UUID

@dataclass(frozen=True)
class RetrievedChunk:
    content: str
    metadata: dict[str, Any]


def retrieve(chat_id: UUID | str, question: str, top_k: int = 4):
    if top_k < 1:
        return []

    result = chroma_collection.query(
        query_texts=[question],
        n_results=top_k,
        where={"chat_id": str(chat_id)},
    )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    return [
        RetrievedChunk(content=content, metadata=metadata or {})
        for content, metadata in zip(documents, metadatas)
        if content
    ]