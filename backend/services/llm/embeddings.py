from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_texts(texts: list[str]):
    return _model.encode(texts, normalize_embeddings=True, batch_size=32).tolist()


def embed_query(text: str):
    return embed_texts([text])[0]