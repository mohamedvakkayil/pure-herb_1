from django.contrib import admin
from .models import JournalEntry, JournalEntryLine


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 2


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'reference', 'entry_type', 'description', 'created_at']
    list_filter = ['date']
    search_fields = ['description', 'reference']
    inlines = [JournalEntryLineInline]
