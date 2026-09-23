from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from notes.models import Note

from .services import semantic_search


class AskView(LoginRequiredMixin, TemplateView):
    template_name = "ai_search/ask_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        context["query"] = query
        context["results"] = []

        if not query:
            return context

        try:
            matches = semantic_search(query, owner_id=self.request.user.id, top_k=5)
        except Exception:
            context["error"] = (
                "Semantic search is temporarily unavailable. Please try again shortly."
            )
            return context

        notes_by_id = {
            str(note.pk): note
            for note in Note.objects.filter(
                pk__in=[m["id"] for m in matches], owner=self.request.user
            )
        }
        context["results"] = [
            {"note": notes_by_id[m["id"]], "score": m["score"]}
            for m in matches
            if m["id"] in notes_by_id
        ]
        return context
