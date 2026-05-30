from django.contrib import admin
from .models import Ticket, Note

class NoteInline(admin.TabularInline):
    model = Note
    extra = 1

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'customer_name', 'customer_email', 'subject', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('ticket_id', 'customer_name', 'customer_email', 'subject', 'description')
    readonly_fields = ('ticket_id', 'created_at', 'updated_at')
    inlines = [NoteInline]

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'note_text_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('note_text', 'ticket__ticket_id', 'ticket__customer_name')

    def note_text_short(self, obj):
        return obj.note_text[:50] + '...' if len(obj.note_text) > 50 else obj.note_text
    note_text_short.short_description = 'Note Text'
