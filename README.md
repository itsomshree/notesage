# NoteSage

A personal knowledge base / notes app built in Django, with an isolated AI
semantic-search feature layered on top. Built primarily as a Django
project – CRUD, auth, the ORM, forms, admin – with the
LLM/embeddings piece kept in its own app so it can be built and understood
independently of the core notes app.

- **Core app (`notes`):** full CRUD on notes, tagging, per-user isolation,
  plain-text search, pagination, Django admin. Works completely standalone,
  with zero dependency on AI features.
- **AI layer (`ai_search`):** semantic search over your notes via
  [Pinecone](https://www.pinecone.io/) + `sentence-transformers`, and an
  "ask your notes" RAG endpoint via the HuggingFace Inference API. Additive,
  not load-bearing – if it's unavailable, the rest of the app still works.

---

## Tech stack

| Layer | Choice |
|---|---|
| Framework | Django 5.2.17 |
| Database | PostgreSQL via Supabase (SQLite fallback for local dev with no `SUPABASE_DB_URL` set) |
| Auth | Django's built-in `django.contrib.auth` |
| Vector DB | Pinecone |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dim, runs locally on CPU) |
| LLM inference | HuggingFace Inference API |
| Frontend | Django templates + Bootstrap 5 |
| Package manager | [`uv`](https://docs.astral.sh/uv/) |

---

## Project structure

```
notesage/
├── config/          # Django project settings, urls, wsgi/asgi
├── accounts/        # signup / login / logout
├── notes/           # core app — Note & Tag models, CRUD views, admin
├── ai_search/        # isolated AI app — embeddings, Pinecone, HF calls, RAG
├── templates/        # base.html + per-app templates
├── static/css/       # style.css (theme, loaded after Bootstrap)
└── manage.py
```

`notes` has no import dependency on `ai_search`. The connection between
them runs the other way: `notes/signals.py` calls into `ai_search` on
note save/delete to keep embeddings in sync, and that call is wrapped in
a `try/except` so a Pinecone or embedding failure never blocks saving a
note – it's just logged.

---

## Setup

### 1. Install dependencies

```bash
uv sync
```

This reads `pyproject.toml` / `uv.lock` and creates a `.venv` for you.
Use `uv run <command>` below instead of manually activating the venv.

### 2. Configure environment variables

Copy the example file and fill in your own values:

```bash
cp .env.example .env
```

| Variable | Required? | Notes |
|---|---|---|
| `DJANGO_SECRET_KEY` | Recommended | Falls back to an insecure dev key if unset – fine for local dev, **not** for anything else. |
| `SUPABASE_DB_URL` | No | If unset, falls back to local `db.sqlite3`. Set this to use Postgres. |
| `PINECONE_API_KEY` | Only for AI features | Required for embedding/semantic search to work. |
| `PINECONE_ENVIRONMENT` | Only for AI features | e.g. `us-east-1`. |
| `PINECONE_CLOUD` | Only for AI features | e.g. `aws`. |
| `PINECONE_INDEX_NAME` | Only for AI features | Defaults to `notesage-notes` if unset. Must match the embedding model's output dimension (384 for `all-MiniLM-L6-v2`). |
| `HUGGINGFACEHUB_API_TOKEN` | Only for "Ask your notes" | Required for the RAG/`ask_question` feature. Semantic search alone doesn't need it. |

The notes app (CRUD, tags, plain-text search, admin) works with **no** AI
variables set at all.

### 3. Run migrations

```bash
uv run manage.py migrate
```

### 4. Create an admin account

Signing up through the app's `/accounts/signup/` page creates a regular
user, **not** a staff account – it can't log into `/admin/`. To access
the Django admin, create a superuser separately:

```bash
uv run manage.py createsuperuser
```

Then log in at `/admin/` with those credentials.

### 5. Run the server

```bash
uv run manage.py runserver
```

Visit `http://127.0.0.1:8000/`– it redirects to your note list (or the
login page if you're not signed in).

---

## AI features

These are optional and isolated in the `ai_search` app.

- **Auto-embedding on save:** every time a note is created or updated, a
  Django signal (`notes/signals.py`) embeds it and upserts the vector into
  Pinecone, keyed by note ID and scoped to the owner. Deleting a note
  removes its vector too.
- **Backfilling existing notes:** if you add notes before Pinecone is
  configured, or change the embedding model, re-embed everything with:

  ```bash
  uv run manage.py backfill_embeddings
  ```

  Safe to re-run – upserts are idempotent.

- **Semantic search vs. plain-text search:** the note list's search box
  (`?q=`) does a plain `icontains` match. The "Ask your notes" button
  (bottom-right, when logged in) does embedding-based semantic search,
  optionally followed by an LLM-generated answer grounded in your top
  matching notes.
- **Manual smoke test:** `ai_search/manual_test.py` upserts a few sample
  notes, checks that a relevant query ranks the right note first, checks
  that one user's notes never leak into another user's results, then
  cleans up after itself:

  ```bash
  uv run python ai_search/manual_test.py
  ```

---

## Running tests

```bash
uv run manage.py test
```

---

## Notes on deployment

This project doesn't currently include deployment configuration – it's
built and run locally.

---

## Open items

- [x] Pick the specific HuggingFace model for LLM inference (currently
      falls back through `Qwen2.5-7B-Instruct` → `Llama-3.1-8B-Instruct`)
- [x] Revisit the embedding model choice (`all-MiniLM-L6-v2` vs
      `bge-small-en-v1.5`) if semantic search relevance needs improving
- [x] Deployment target and config, once that's decided