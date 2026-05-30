from django.db import models
from django.utils import timezone

class Ticket(models.Model):
    # Status Choices
    STATUS_OPEN = 'Open'
    STATUS_IN_PROGRESS = 'In Progress'
    STATUS_CLOSED = 'Closed'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_CLOSED, 'Closed'),
    ]

    # Model fields
    ticket_id = models.CharField(max_length=20, unique=True, editable=False, db_index=True)
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket_id} - {self.subject} ({self.customer_name})"

    def save(self, *args, **kwargs):
        # Auto-generate human-readable ticket ID (e.g., TKT-0001) if not set
        if not self.ticket_id:
            # Query for the latest ticket to compute the next number sequentially.
            # Using ordering by id ensures we query the absolute latest row.
            last_ticket = Ticket.objects.all().order_by('-id').first()
            next_num = 1
            if last_ticket and last_ticket.ticket_id:
                try:
                    parts = last_ticket.ticket_id.split('-')
                    if len(parts) == 2 and parts[1].isdigit():
                        next_num = int(parts[1]) + 1
                except (ValueError, IndexError):
                    # Fallback in case of parsing issues
                    pass
            self.ticket_id = f"TKT-{next_num:04d}"
        
        super().save(*args, **kwargs)


class Note(models.Model):
    # Relational link to the Ticket model
    # CASCADE deletes all associated notes if the ticket is removed
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='notes')
    note_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at'] # Chronological timeline order

    def __str__(self):
        return f"Note on {self.ticket.ticket_id} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
