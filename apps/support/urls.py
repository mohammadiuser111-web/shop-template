"""
URL configuration for support app.
"""
from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # Ticket views
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('tickets/<str:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/<str:ticket_id>/message/', views.add_ticket_message, name='add_ticket_message'),
    path('tickets/<str:ticket_id>/close/', views.close_ticket, name='close_ticket'),
    path('tickets/<str:ticket_id>/reopen/', views.reopen_ticket, name='reopen_ticket'),
    path('tickets/search/', views.ticket_search, name='ticket_search'),
    
    # FAQ views
    path('faq/', views.faq_list, name='faq_list'),
    path('faq/<slug:slug>/', views.faq_detail, name='faq_detail'),
    
    # Contact views
    path('contact/', views.contact, name='contact'),
    
    # Live chat views
    path('chat/', views.live_chat, name='live_chat'),
    path('chat/send/', views.send_chat_message, name='send_chat_message'),
    path('chat/messages/', views.get_chat_messages, name='get_chat_messages'),
    path('chat/end/', views.end_chat_session, name='end_chat_session'),
    
    # AJAX views
    path('ajax/faq/categories/', views.get_faq_categories_ajax, name='get_faq_categories_ajax'),
    path('ajax/ticket/<str:ticket_id>/status/', views.get_ticket_status_ajax, name='get_ticket_status_ajax'),
    path('ajax/ticket/attachment/', views.upload_ticket_attachment_ajax, name='upload_ticket_attachment_ajax'),
]
