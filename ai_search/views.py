from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .services import ask_question


class AskView(LoginRequiredMixin, TemplateView):
    template_name = "ai_search/ask_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        context["query"] = query
        context["answer"] = None
        context["results"] = []

        if not query:
            return context

        try:
            result = ask_question(query, owner_id=self.request.user.id)
        except Exception:
            context["error"] = (
                "Semantic search is temporarily unavailable. Please try again shortly."
            )
            return context

        context["answer"] = result["answer"]
        if result["error"]:
            context["error"] = result["error"]

        context["results"] = [{"note": note} for note in result["notes"]]
        return context
