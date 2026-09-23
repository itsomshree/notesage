import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from ai_search.services import embed_note, semantic_search  # noqa: E402

SAMPLE_NOTES = [
    (
        101,
        "Pasta recipe",
        "Boil pasta, saute garlic in olive oil, toss together with parmesan.",
        1,
    ),
    (
        102,
        "Q3 budget meeting",
        "Discussed marketing spend overages and revised Q4 projections.",
        1,
    ),
    (
        103,
        "Book recommendation",
        "Someone recommended Project Hail Mary — sci-fi, similar to The Martian.",
        1,
    ),
    (
        104,
        "Confidential salary notes",
        "Discussed salary bands and performance reviews for the team.",
        2,
    ),
]


def run():
    print(f"Embedding and upserting {len(SAMPLE_NOTES)} sample notes...")
    for note_id, title, body, owner_id in SAMPLE_NOTES:
        vector = embed_note(note_id, title, body, owner_id=owner_id)
        print(
            f"  note {note_id} ({title!r}, owner {owner_id}): vector length {len(vector)}"
        )

    # --- Relevance check ---
    query_text = "What did we decide about garlic pasta?"
    print(f"\nsemantic_search({query_text!r}, owner_id=1)")
    matches = semantic_search(query_text, owner_id=1, top_k=3)
    for match in matches:
        print(
            f"  id={match['id']} score={match['score']:.4f} "
            f"title={match.get('metadata', {}).get('title')!r}"
        )

    top_id = matches[0]["id"] if matches else None
    if top_id == "101":
        print(" Relevance check passed: the pasta note ranked first for a pasta query.")
    else:
        print(" Unexpected top match — inspect the scores above.")

    # Owner isolation check
    salary_query = "What are the salary bands for the team?"
    print(
        f"\nsemantic_search({salary_query!r}, owner_id=1)  <- note 104 belongs to owner 2"
    )
    matches = semantic_search(salary_query, owner_id=1, top_k=3)
    leaked_ids = [m["id"] for m in matches if m["id"] == "104"]

    for match in matches:
        print(
            f"  id={match['id']} score={match['score']:.4f} "
            f"title={match.get('metadata', {}).get('title')!r}"
        )

    if not leaked_ids:
        print(
            " Isolation check passed: owner 2's note never appeared in owner 1's results."
        )
    else:
        print(" Isolation check FAILED: another owner's note leaked into the results!")


run()
