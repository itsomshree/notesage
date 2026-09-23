import os
from functools import lru_cache

from pinecone import Pinecone, ServerlessSpec

INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "notesage-notes")
EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 output size


@lru_cache(maxsize=1)
def get_client() -> Pinecone:
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        raise RuntimeError("PINECONE_API_KEY is not set (check your .env)")
    return Pinecone(api_key=api_key)


def get_or_create_index(
    index_name: str = INDEX_NAME, dimension: int = EMBEDDING_DIMENSION
):
    pc = get_client()
    existing_names = {idx["name"] for idx in pc.list_indexes()}
    if index_name not in existing_names:
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=os.environ.get("PINECONE_CLOUD", "aws"),
                region=os.environ.get("PINECONE_ENVIRONMENT", "us-east-1"),
            ),
        )
    return pc.Index(index_name)


def upsert_vector(note_id, vector, metadata=None, index=None):
    index = index or get_or_create_index()
    index.upsert(
        vectors=[
            {
                "id": str(note_id),
                "values": vector,
                "metadata": metadata or {},
            }
        ]
    )


def query_similar(vector, top_k=5, filter=None, index=None):
    index = index or get_or_create_index()
    result = index.query(
        vector=vector,
        top_k=top_k,
        include_metadata=True,
        filter=filter,
    )
    return result.get("matches", [])


def delete_vector(note_id, index=None):
    index = index or get_or_create_index()
    index.delete(ids=[str(note_id)])
