from django.urls import path
from . import views

urlpatterns = [
    # UI HTML pages
    path('', views.dashboard, name='dashboard'),
    path('tickets/new/', views.create_ticket, name='create_ticket'),
    path('tickets/<str:ticket_id>/', views.ticket_detail, name='ticket_detail'),

    # REST API Endpoints (exactly matching project specifications)
    path('api/tickets', views.api_tickets, name='api_tickets'),
    path('api/tickets/<str:ticket_id>', views.api_ticket_detail, name='api_ticket_detail'),
]
