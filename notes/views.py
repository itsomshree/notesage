from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import NoteForm
from .models import Note, Tag


class OwnerQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class NoteListView(OwnerQuerysetMixin, ListView):
    model = Note
    paginate_by = 10
    context_object_name = "notes"

    def get_queryset(self):
        qs = super().get_queryset()

        query = self.request.GET.get("q", "").strip()
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(body__icontains=query))

        tag_name = self.request.GET.get("tag", "").strip()
        if tag_name:
            qs = qs.filter(tags__name=tag_name)

        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["active_tag"] = self.request.GET.get("tag", "")
        context["tags"] = Tag.objects.filter(notes__owner=self.request.user).distinct()
        return context


class NoteDetailView(OwnerQuerysetMixin, DetailView):
    model = Note
    context_object_name = "note"


class NoteCreateView(OwnerQuerysetMixin, CreateView):
    model = Note
    form_class = NoteForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class NoteUpdateView(OwnerQuerysetMixin, UpdateView):
    model = Note
    form_class = NoteForm


class NoteDeleteView(OwnerQuerysetMixin, DeleteView):
    model = Note
    success_url = reverse_lazy("note_list")
