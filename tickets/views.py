import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Ticket, Note

# ==========================================
# UI Views (HTML Templates)
# ==========================================

def dashboard(request):
    """
    Renders the central CRM dashboard.
    Retrieves initial stats and tickets.
    """
    tickets = Ticket.objects.all()
    
    # Calculate stats for the dashboard counters
    stats = {
        'total': tickets.count(),
        'open': tickets.filter(status=Ticket.STATUS_OPEN).count(),
        'in_progress': tickets.filter(status=Ticket.STATUS_IN_PROGRESS).count(),
        'closed': tickets.filter(status=Ticket.STATUS_CLOSED).count(),
    }
    
    # Return recent tickets (limit to 50 initially, search/filters will fetch all)
    recent_tickets = tickets[:50]
    
    context = {
        'stats': stats,
        'tickets': recent_tickets,
        'status_choices': Ticket.STATUS_CHOICES
    }
    return render(request, 'tickets/dashboard.html', context)


def create_ticket(request):
    """
    Handles standard HTTP GET/POST for creating a ticket.
    Provides a fallback if JavaScript is disabled.
    """
    if request.method == 'POST':
        name = request.POST.get('customer_name')
        email = request.POST.get('customer_email')
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        
        if not all([name, email, subject, description]):
            return render(request, 'tickets/create.html', {
                'error': 'All fields are required.',
                'values': request.POST
            })
            
        ticket = Ticket.objects.create(
            customer_name=name,
            customer_email=email,
            subject=subject,
            description=description
        )
        return redirect('ticket_detail', ticket_id=ticket.ticket_id)
        
    return render(request, 'tickets/create.html')


def ticket_detail(request, ticket_id):
    """
    Renders the details page of a specific ticket, including its notes timeline.
    """
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    notes = ticket.notes.all()
    
    context = {
        'ticket': ticket,
        'notes': notes,
        'status_choices': Ticket.STATUS_CHOICES
    }
    return render(request, 'tickets/detail.html', context)


# ==========================================
# REST API Endpoints (JSON)
# ==========================================

@csrf_exempt
def api_tickets(request):
    """
    POST /api/tickets - Create a ticket
    GET /api/tickets - List tickets with optional ?status and ?search filters
    """
    if request.method == 'GET':
        status_filter = request.GET.get('status')
        search_query = request.GET.get('search')
        
        tickets = Ticket.objects.all()
        
        # Apply status filter if provided
        if status_filter:
            tickets = tickets.filter(status=status_filter)
            
        # Apply search query across multiple fields if provided
        if search_query:
            tickets = tickets.filter(
                Q(ticket_id__icontains=search_query) |
                Q(customer_name__icontains=search_query) |
                Q(customer_email__icontains=search_query) |
                Q(subject__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            
        # Serialize response
        data = []
        for t in tickets:
            data.append({
                'ticket_id': t.ticket_id,
                'customer_name': t.customer_name,
                'customer_email': t.customer_email,
                'subject': t.subject,
                'status': t.status,
                'created_at': t.created_at.isoformat()
            })
            
        return JsonResponse(data, safe=False)
        
    elif request.method == 'POST':
        try:
            # Handle standard JSON body
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
            
        customer_name = body.get('customer_name')
        customer_email = body.get('customer_email')
        subject = body.get('subject')
        description = body.get('description')
        
        if not all([customer_name, customer_email, subject, description]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
            
        ticket = Ticket.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            subject=subject,
            description=description
        )
        
        return JsonResponse({
            'ticket_id': ticket.ticket_id,
            'created_at': ticket.created_at.isoformat()
        }, status=201)
        
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_ticket_detail(request, ticket_id):
    """
    GET /api/tickets/{ticket_id} - Retrieve detailed ticket info + notes
    PUT /api/tickets/{ticket_id} - Update status and/or add a new note
    """
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    
    if request.method == 'GET':
        notes_data = []
        for note in ticket.notes.all():
            notes_data.append({
                'id': note.id,
                'note_text': note.note_text,
                'created_at': note.created_at.isoformat()
            })
            
        return JsonResponse({
            'ticket_id': ticket.ticket_id,
            'customer_name': ticket.customer_name,
            'customer_email': ticket.customer_email,
            'subject': ticket.subject,
            'description': ticket.description,
            'status': ticket.status,
            'created_at': ticket.created_at.isoformat(),
            'updated_at': ticket.updated_at.isoformat(),
            'notes': notes_data
        })
        
    elif request.method == 'PUT':
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
            
        status = body.get('status')
        new_note_text = body.get('notes') # This represents the note text to add
        
        updated = False
        
        # 1. Update status if valid
        if status:
            valid_statuses = [choice[0] for choice in Ticket.STATUS_CHOICES]
            if status not in valid_statuses:
                return JsonResponse({'error': f'Invalid status. Must be one of {valid_statuses}'}, status=400)
            ticket.status = status
            updated = True
            
        # 2. Add new note if provided
        if new_note_text and str(new_note_text).strip():
            Note.objects.create(
                ticket=ticket,
                note_text=str(new_note_text).strip()
            )
            updated = True
            
        if updated:
            ticket.save() # This triggers the updated_at timestamp update
            
        return JsonResponse({
            'success': True,
            'updated_at': ticket.updated_at.isoformat()
        })
        
    return JsonResponse({'error': 'Method not allowed'}, status=405)
