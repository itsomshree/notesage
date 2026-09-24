SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions about a user's personal notes.\n"
    "Answer ONLY using the note excerpts provided below — do not use outside knowledge.\n"
    "If the notes don't contain enough information to answer, say so plainly instead "
    "of guessing.\n"
    "Keep answers concise. When useful, mention which note(s) the answer comes from "
    "by title."
)

MAX_CHARS_PER_NOTE = 800


def _format_note(note) -> str:
    body = note.body[:MAX_CHARS_PER_NOTE]
    if len(note.body) > MAX_CHARS_PER_NOTE:
        body += "..."
    return f'Title: "{note.title}"\n{body}'


def build_rag_messages(query: str, notes: list) -> list[dict]:
    if not notes:
        context = "(No matching notes were found for this query.)"
    else:
        context = "\n\n---\n\n".join(_format_note(note) for note in notes)

    user_content = (
        f"Here are the user's notes most relevant to their question:\n\n"
        f"{context}\n\n---\n\n"
        f"Question: {query}"
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
