"""
API URLs for Support app.
"""
from django.urls import path
from .views import (
    # Support Category views
    SupportCategoryListAPIView, SupportCategoryRetrieveAPIView,
    SupportCategoryCreateAPIView, SupportCategoryUpdateAPIView,
    SupportCategoryDestroyAPIView,
    # Ticket Priority views
    TicketPriorityListAPIView, TicketPriorityRetrieveAPIView,
    TicketPriorityCreateAPIView, TicketPriorityUpdateAPIView,
    # Ticket Status views
    TicketStatusListAPIView, TicketStatusRetrieveAPIView,
    TicketStatusCreateAPIView,
    # Ticket Tag views
    TicketTagListAPIView, TicketTagRetrieveAPIView,
    TicketTagCreateAPIView,
    # Ticket views
    TicketListAPIView, TicketRetrieveAPIView,
    TicketCreateAPIView, TicketUpdateAPIView,
    TicketDestroyAPIView, TicketCloseAPIView,
    TicketReopenAPIView, UserTicketsAPIView,
    UserTicketRetrieveAPIView,
    # Ticket Message views
    TicketMessageListAPIView, TicketMessageRetrieveAPIView,
    TicketMessageCreateAPIView, TicketMessageDestroyAPIView,
    # Ticket Attachment views
    TicketAttachmentListAPIView, TicketAttachmentRetrieveAPIView,
    TicketAttachmentCreateAPIView, TicketAttachmentDestroyAPIView,
    # Ticket Template views
    TicketTemplateListAPIView, TicketTemplateRetrieveAPIView,
    TicketTemplateCreateAPIView, TicketTemplateDestroyAPIView,
    # FAQ views
    FAQListAPIView, FAQRetrieveAPIView,
    FAQCreateAPIView, FAQUpdateAPIView,
    FAQDestroyAPIView, FAQSearchAPIView,
    FAQHelpfulAPIView,
    # FAQ Category views
    FAQCategoryListAPIView, FAQCategoryRetrieveAPIView,
    FAQCategoryCreateAPIView, FAQCategoryUpdateAPIView,
    FAQCategoryDestroyAPIView,
    # Customer Satisfaction views
    CustomerSatisfactionListAPIView, CustomerSatisfactionRetrieveAPIView,
    CustomerSatisfactionCreateAPIView,
    # Statistics
    SupportStatisticsAPIView, RecentTicketsAPIView
)

urlpatterns = [
    # Support Categories
    path('categories/', SupportCategoryListAPIView.as_view(), name='api-support-categories-list'),
    path('categories/<uuid:parent_id>/', SupportCategoryListAPIView.as_view(), name='api-support-category-children-list'),
    path('categories/create/', SupportCategoryCreateAPIView.as_view(), name='api-support-categories-create'),
    path('categories/<uuid:pk>/', SupportCategoryRetrieveAPIView.as_view(), name='api-support-categories-retrieve'),
    path('categories/<uuid:pk>/update/', SupportCategoryUpdateAPIView.as_view(), name='api-support-categories-update'),
    path('categories/<uuid:pk>/delete/', SupportCategoryDestroyAPIView.as_view(), name='api-support-categories-delete'),
    
    # Ticket Priorities
    path('priorities/', TicketPriorityListAPIView.as_view(), name='api-ticket-priorities-list'),
    path('priorities/<uuid:pk>/', TicketPriorityRetrieveAPIView.as_view(), name='api-ticket-priorities-retrieve'),
    path('priorities/create/', TicketPriorityCreateAPIView.as_view(), name='api-ticket-priorities-create'),
    path('priorities/<uuid:pk>/update/', TicketPriorityUpdateAPIView.as_view(), name='api-ticket-priorities-update'),
    
    # Ticket Statuses
    path('statuses/', TicketStatusListAPIView.as_view(), name='api-ticket-statuses-list'),
    path('statuses/<uuid:pk>/', TicketStatusRetrieveAPIView.as_view(), name='api-ticket-statuses-retrieve'),
    path('statuses/create/', TicketStatusCreateAPIView.as_view(), name='api-ticket-statuses-create'),
    
    # Ticket Tags
    path('tags/', TicketTagListAPIView.as_view(), name='api-ticket-tags-list'),
    path('tags/<uuid:pk>/', TicketTagRetrieveAPIView.as_view(), name='api-ticket-tags-retrieve'),
    path('tags/create/', TicketTagCreateAPIView.as_view(), name='api-ticket-tags-create'),
    
    # Tickets
    path('tickets/', TicketListAPIView.as_view(), name='api-tickets-list'),
    path('tickets/recent/', RecentTicketsAPIView.as_view(), name='api-tickets-recent'),
    path('tickets/create/', TicketCreateAPIView.as_view(), name='api-tickets-create'),
    path('tickets/<uuid:pk>/', TicketRetrieveAPIView.as_view(), name='api-tickets-retrieve'),
    path('tickets/<uuid:pk>/update/', TicketUpdateAPIView.as_view(), name='api-tickets-update'),
    path('tickets/<uuid:pk>/delete/', TicketDestroyAPIView.as_view(), name='api-tickets-delete'),
    path('tickets/<uuid:pk>/close/', TicketCloseAPIView.as_view(), name='api-tickets-close'),
    path('tickets/<uuid:pk>/reopen/', TicketReopenAPIView.as_view(), name='api-tickets-reopen'),
    
    # User Tickets
    path('my/tickets/', UserTicketsAPIView.as_view(), name='api-my-tickets-list'),
    path('my/tickets/<uuid:pk>/', UserTicketRetrieveAPIView.as_view(), name='api-my-tickets-retrieve'),
    
    # Ticket Messages
    path('tickets/<uuid:ticket_id>/messages/', TicketMessageListAPIView.as_view(), name='api-ticket-messages-list'),
    path('messages/<uuid:pk>/', TicketMessageRetrieveAPIView.as_view(), name='api-ticket-messages-retrieve'),
    path('messages/create/', TicketMessageCreateAPIView.as_view(), name='api-ticket-messages-create'),
    path('messages/<uuid:pk>/delete/', TicketMessageDestroyAPIView.as_view(), name='api-ticket-messages-delete'),
    
    # Ticket Attachments
    path('tickets/<uuid:ticket_id>/attachments/', TicketAttachmentListAPIView.as_view(), name='api-ticket-attachments-list'),
    path('attachments/<uuid:pk>/', TicketAttachmentRetrieveAPIView.as_view(), name='api-ticket-attachments-retrieve'),
    path('attachments/create/', TicketAttachmentCreateAPIView.as_view(), name='api-ticket-attachments-create'),
    path('attachments/<uuid:pk>/delete/', TicketAttachmentDestroyAPIView.as_view(), name='api-ticket-attachments-delete'),
    
    # Ticket Templates
    path('templates/', TicketTemplateListAPIView.as_view(), name='api-ticket-templates-list'),
    path('templates/<uuid:category_id>/', TicketTemplateListAPIView.as_view(), name='api-ticket-templates-category-list'),
    path('templates/<uuid:pk>/', TicketTemplateRetrieveAPIView.as_view(), name='api-ticket-templates-retrieve'),
    path('templates/create/', TicketTemplateCreateAPIView.as_view(), name='api-ticket-templates-create'),
    path('templates/<uuid:pk>/delete/', TicketTemplateDestroyAPIView.as_view(), name='api-ticket-templates-delete'),
    
    # FAQs
    path('faqs/', FAQListAPIView.as_view(), name='api-faqs-list'),
    path('faqs/search/', FAQSearchAPIView.as_view(), name='api-faqs-search'),
    path('faqs/<uuid:pk>/', FAQRetrieveAPIView.as_view(), name='api-faqs-retrieve'),
    path('faqs/<uuid:pk>/helpful/', FAQHelpfulAPIView.as_view(), name='api-faqs-helpful'),
    path('faqs/create/', FAQCreateAPIView.as_view(), name='api-faqs-create'),
    path('faqs/<uuid:pk>/update/', FAQUpdateAPIView.as_view(), name='api-faqs-update'),
    path('faqs/<uuid:pk>/delete/', FAQDestroyAPIView.as_view(), name='api-faqs-delete'),
    
    # Category-specific FAQs
    path('categories/<uuid:category_id>/faqs/', FAQListAPIView.as_view(), name='api-category-faqs-list'),
    
    # Tag-specific FAQs
    path('tags/<uuid:tag_id>/faqs/', FAQListAPIView.as_view(), name='api-tag-faqs-list'),
    
    # FAQ Categories
    path('faq-categories/', FAQCategoryListAPIView.as_view(), name='api-faq-categories-list'),
    path('faq-categories/<uuid:parent_id>/', FAQCategoryListAPIView.as_view(), name='api-faq-category-children-list'),
    path('faq-categories/create/', FAQCategoryCreateAPIView.as_view(), name='api-faq-categories-create'),
    path('faq-categories/<uuid:pk>/', FAQCategoryRetrieveAPIView.as_view(), name='api-faq-categories-retrieve'),
    path('faq-categories/<uuid:pk>/update/', FAQCategoryUpdateAPIView.as_view(), name='api-faq-categories-update'),
    path('faq-categories/<uuid:pk>/delete/', FAQCategoryDestroyAPIView.as_view(), name='api-faq-categories-delete'),
    
    # Customer Satisfaction
    path('satisfaction/', CustomerSatisfactionListAPIView.as_view(), name='api-satisfaction-list'),
    path('satisfaction/<uuid:pk>/', CustomerSatisfactionRetrieveAPIView.as_view(), name='api-satisfaction-retrieve'),
    path('satisfaction/create/', CustomerSatisfactionCreateAPIView.as_view(), name='api-satisfaction-create'),
    
    # Statistics
    path('statistics/', SupportStatisticsAPIView.as_view(), name='api-support-statistics'),
]
