from django.contrib import admin

from .models import Note, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at", "updated_at")
    list_filter = ("tags", "created_at")
    search_fields = ("title", "body")
    autocomplete_fields = ("tags",)
