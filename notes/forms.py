from django import forms

from .models import Note, Tag


class NoteForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        label="Tags",
        help_text="Comma-seperated, e.g. work, ideas, recipes",
        widget=forms.TextInput(attrs={"placeholder": "work, ideas, recipes"}),
    )

    class Meta:
        model = Note
        fields = ("title", "body")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["tags_input"].initial = ", ".join(
                self.instance.tags.values_list("name", flat=True)
            )

    def clean_tags_input(self):
        raw = self.cleaned_data.get("tags_input", "")
        names = [name.strip() for name in raw.split(",") if name.strip()]
        seen, unique_names = set(), []
        for name in names:
            key = name.lower()
            if key not in seen:
                seen.add(key)
                unique_names.append(name)
        return unique_names

    def save(self, commit=True):
        note = super().save(commit=commit)

        def sync_tags():
            tags = [
                Tag.objects.get_or_create(name__iexact=name, defaults={"name": name})[0]
                for name in self.cleaned_data["tags_input"]
            ]
            note.tags.set(tags)

        if commit:
            sync_tags()
        else:
            self.save_m2m = sync_tags

        return note
