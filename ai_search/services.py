from functools import lru_cache

from sentence_transformers import SentenceTransformer

from . import pinecone_client

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_text(text: str) -> list[float]:
    model = get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_note(note_id, title: str, body: str, owner_id=None) -> list[float]:
    text = f"{title}\n\n{body}".strip()
    vector = embed_text(text)

    metadata = {"title": title}
    if owner_id is not None:
        metadata["owner_id"] = owner_id

    pinecone_client.upsert_vector(note_id=note_id, vector=vector, metadata=metadata)
    return vector
