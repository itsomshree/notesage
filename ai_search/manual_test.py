import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from ai_search import pinecone_client  # noqa: E402
from ai_search.services import embed_note  # noqa: E402

SAMPLE_NOTES = [
    (
        101,
        "Pasta recipe",
        "Boil pasta, saute garlic in olive oil, toss together with parmesan.",
    ),
    (
        102,
        "Q3 budget meeting",
        "Discussed marketing spend overages and revised Q4 projections.",
    ),
    (
        103,
        "Book recommendation",
        "Someone recommended Project Hail Mary — sci-fi, similar to The Martian.",
    ),
]


def run():
    print(f"Embedding and upserting {len(SAMPLE_NOTES)} sample notes...")
    for note_id, title, body in SAMPLE_NOTES:
        vector = embed_note(note_id, title, body, owner_id=1)
        print(
            f"  note {note_id} ({title!r}): vector length {len(vector)}, "
            f"first 3 dims {vector[:3]}"
        )

    query_text = "What did we decide about garlic pasta?"
    print(f"\nQuerying for: {query_text!r}")
    from ai_search.services import embed_text

    query_vector = embed_text(query_text)
    matches = pinecone_client.query_similar(query_vector, top_k=3)

    print("Top matches:")
    for match in matches:
        print(
            f"  id={match['id']} score={match['score']:.4f} "
            f"title={match.get('metadata', {}).get('title')!r}"
        )

    top_id = matches[0]["id"] if matches else None
    if top_id == "101":
        print("\n Sanity check passed: the pasta note ranked first for a pasta query.")
    else:
        print("\n Unexpected top match — inspect the scores above.")


run()
