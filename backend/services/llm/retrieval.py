from dataclasses import dataclass
from typing import Any
from uuid import UUID
import numpy as np
from sqlalchemy import select
from models.chunk import Chunk
from services.llm.embed import SyncSession
from services.llm.embeddings import embed_query


@dataclass(frozen=True)
class RetrievedChunk:
    content: str
    metadata: dict[str, Any]


def _mmr(query_vec, candidate_vecs, k: int, lambda_mult: float):
    cands = np.asarray(candidate_vecs, dtype=float)
    q = np.asarray(query_vec, dtype=float)
    sim_q = cands @ q
    sim_cc = cands @ cands.T

    selected = [int(np.argmax(sim_q))]
    remaining = set(range(len(cands))) - set(selected)
    while remaining and len(selected) < k:
        best = max(
            remaining,
            key=lambda i: lambda_mult * sim_q[i]
            - (1 - lambda_mult) * max(sim_cc[i][j] for j in selected),
        )
        selected.append(best)
        remaining.remove(best)
    return selected


def retrieve(chat_id, question, document_ids, top_k_by_document=None, document_names=None, top_k=10, fetch_k=20, lambda_mult=0.5):
    if top_k < 1 or not document_ids:
        return []

    top_k_by_document = top_k_by_document or {}
    document_names = document_names or {}
    query_vec = embed_query(question)

    chunks = []
    with SyncSession() as session:
        for document_id in document_ids:
            key = str(document_id)
            per_doc_k = top_k_by_document.get(key, top_k)
            if per_doc_k < 1:
                continue

            rows = session.scalars(
                select(Chunk)
                .where(Chunk.chat_id == chat_id, Chunk.document_id == UUID(key))
                .order_by(Chunk.embedding.cosine_distance(query_vec))
                .limit(fetch_k)
            ).all()
            if not rows:
                continue

            picked = _mmr(query_vec, [r.embedding for r in rows], per_doc_k, lambda_mult)
            chunks.extend(
                RetrievedChunk(
                    content=rows[i].content,
                    metadata={
                        "document_id": key,
                        "chat_id": str(rows[i].chat_id),
                        "page": rows[i].page,
                        "filename": document_names.get(key),
                    },
                )
                for i in picked
                if rows[i].content
            )

    return chunks