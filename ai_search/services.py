from functools import lru_cache

from sentence_transformers import SentenceTransformer

from . import hf_client, pinecone_client, prompts

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


def semantic_search(query: str, owner_id, top_k: int = 5):
    vector = embed_text(query)
    return pinecone_client.query_similar(
        vector, top_k=top_k, filter={"owner_id": owner_id}
    )


RELEVANCE_MARGIN = 0.15

MIN_SCORE = 0.15


def ask_question(query: str, owner_id, top_k: int = 8) -> dict:
    from notes.models import Note

    matches = semantic_search(query, owner_id=owner_id, top_k=top_k)

    if matches and matches[0]["score"] >= MIN_SCORE:
        matches = semantic_search(query, owner_id=owner_id, top_k=top_k)
        matches = [m for m in matches if m["score"] >= MIN_SCORE]
    else:
        matches = []

    notes_by_id = {
        str(note.pk): note
        for note in Note.objects.filter(
            pk__in=[m["id"] for m in matches], owner_id=owner_id
        )
    }
    ordered_notes = [notes_by_id[m["id"]] for m in matches if m["id"] in notes_by_id]

    result = {"answer": None, "notes": ordered_notes, "error": None}

    messages = prompts.build_rag_messages(query, ordered_notes)
    try:
        result["answer"] = hf_client.chat_completion(messages)
    except hf_client.HFInferenceError:
        result["error"] = (
            "AI answer is temporarily unavailable — showing your matching notes instead."
        )

    return result
