from django.contrib import admin
from .models import Note

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('body', 'created', 'updated')
    list_filter = ('created', 'updated')
    search_fields = ('body',)
    ordering = ('-updated',)
    readonly_fields = ('created', 'updated')