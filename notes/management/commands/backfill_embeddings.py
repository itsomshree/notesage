from django.core.management.base import BaseCommand

from notes.models import Note


class Command(BaseCommand):
    help = "Embed every existing note into Pinecone (safe to re-run — upserts are idempotent)."

    def handle(self, *args, **options):
        from ai_search.services import embed_note

        notes = Note.objects.all()
        total = notes.count()

        if total == 0:
            self.stdout.write("No notes to embed.")
            return

        self.stdout.write(f"Embedding {total} note(s)...")
        failures = 0

        for i, note in enumerate(notes, start=1):
            try:
                embed_note(
                    note.pk,
                    note.title,
                    note.body,
                    owner_id=note.owner_id,
                )
                self.stdout.write(
                    f"  [{i}/{total}] embedded note {note.pk} ({note.title!r})"
                )
            except Exception as exc:  # noqa: BLE001
                failures += 1
                self.stderr.write(f"  [{i}/{total}] FAILED note {note.pk}: {exc}")

        self.stdout.write(
            self.style.SUCCESS(f"Done. {total - failures} embedded, {failures} failed.")
        )
