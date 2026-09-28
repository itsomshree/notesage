from django.contrib import admin

from .models import Note, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)

    def note_count(self, obj):
        return obj.notes.count()


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at", "updated_at")
    list_filter = ("tags", "created_at")
    search_fields = ("title", "body")
    autocomplete_fields = ("tags",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("owner",)
    list_per_page = 25
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "body", "owner", "tags")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
