"""
Views for support app (tickets, FAQ, contact, live chat).
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    Ticket, TicketMessage, SupportCategory, FAQ, FAQCategory,
    ContactMessage, LiveChatSession, LiveChatMessage
)
from .forms import (
    TicketForm, TicketMessageForm, FAQForm, ContactForm,
    TicketSearchForm
)
from apps.accounts.models import User


# ==================== TICKET SYSTEM ====================

@login_required
@require_http_methods(["GET"])
def ticket_list(request):
    """List user's support tickets."""
    # Filter by status
    status_filter = request.GET.get('status', 'all')
    category_filter = request.GET.get('category')
    search_query = request.GET.get('q')
    
    tickets = Ticket.objects.filter(user=request.user).select_related(
        'category', 'assigned_to'
    ).prefetch_related('messages').order_by('-created_at')
    
    if status_filter != 'all':
        tickets = tickets.filter(status=status_filter)
    
    if category_filter:
        tickets = tickets.filter(category__id=category_filter)
    
    if search_query:
        tickets = tickets.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) | 
            Q(ticket_id__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(tickets, 10)
    page = request.GET.get('page')
    
    try:
        tickets_page = paginator.page(page)
    except PageNotAnInteger:
        tickets_page = paginator.page(1)
    except EmptyPage:
        tickets_page = paginator.page(paginator.num_pages)
    
    categories = SupportCategory.objects.filter(is_active=True)
    
    context = {
        'tickets': tickets_page,
        'categories': categories,
        'current_status': status_filter,
        'current_category': category_filter,
        'search_query': search_query,
        'title': _('My Support Tickets'),
    }
    return render(request, 'support/ticket_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def create_ticket(request):
    """Create a new support ticket."""
    categories = SupportCategory.objects.filter(is_active=True)
    
    if request.method == 'POST':
        form = TicketForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            ticket = Ticket.objects.create(
                user=request.user,
                category=form.cleaned_data.get('category'),
                title=form.cleaned_data.get('title'),
                description=form.cleaned_data.get('description'),
                priority=form.cleaned_data.get('priority'),
                status='open',
            )
            
            # Add attachments
            attachments = request.FILES.getlist('attachments')
            for attachment in attachments:
                ticket.attachments.create(file=attachment)
            
            # Create initial message
            TicketMessage.objects.create(
                ticket=ticket,
                user=request.user,
                content=form.cleaned_data.get('description'),
                is_internal=False,
            )
            
            # Send notification email
            send_mail(
                subject=f'New Support Ticket: {ticket.title}',
                message=f'Ticket ID: {ticket.ticket_id}\n\n{ticket.description}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.SUPPORT_EMAIL],
                fail_silently=True,
            )
            
            messages.success(request, _('Your support ticket has been created.'))
            return redirect('support:ticket_detail', ticket_id=ticket.ticket_id)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = TicketForm()
    
    context = {
        'form': form,
        'categories': categories,
        'title': _('Create Support Ticket'),
    }
    return render(request, 'support/create_ticket.html', context)


@login_required
@require_http_methods(["GET"])
def ticket_detail(request, ticket_id):
    """View ticket details and messages."""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
    
    # Mark as read
    if ticket.status == 'open' and not ticket.user_read_at:
        ticket.user_read_at = timezone.now()
        ticket.save()
    
    messages = TicketMessage.objects.filter(
        ticket=ticket
    ).select_related('user', 'admin_user').order_by('created_at')
    
    # Message form
    message_form = TicketMessageForm()
    
    context = {
        'ticket': ticket,
        'messages': messages,
        'message_form': message_form,
        'title': f"{_('Ticket')} #{ticket.ticket_id}: {ticket.title}",
    }
    return render(request, 'support/ticket_detail.html', context)


@login_required
@require_http_methods(["POST"])
def add_ticket_message(request, ticket_id):
    """Add a message to a ticket."""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
    
    form = TicketMessageForm(data=request.POST, files=request.FILES)
    if form.is_valid():
        message = TicketMessage.objects.create(
            ticket=ticket,
            user=request.user,
            content=form.cleaned_data.get('content'),
            is_internal=False,
        )
        
        # Add attachments
        attachments = request.FILES.getlist('attachments')
        for attachment in attachments:
            message.attachments.create(file=attachment)
        
        # Update ticket status
        if ticket.status == 'closed':
            ticket.status = 'reopened'
            ticket.save()
        
        # Send notification
        send_mail(
            subject=f'New Message on Ticket #{ticket.ticket_id}',
            message=f'User: {request.user.get_full_name() or request.user.username}\n\n{form.cleaned_data.get("content")}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.SUPPORT_EMAIL],
            fail_silently=True,
        )
        
        messages.success(request, _('Your message has been added.'))
    else:
        messages.error(request, _('Please correct the errors below.'))
    
    return redirect('support:ticket_detail', ticket_id=ticket_id)


@login_required
@require_http_methods(["POST"])
def close_ticket(request, ticket_id):
    """Close a support ticket."""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
    
    ticket.status = 'closed'
    ticket.closed_by = request.user
    ticket.closed_at = timezone.now()
    ticket.save()
    
    messages.success(request, _('Ticket has been closed.'))
    return redirect('support:ticket_detail', ticket_id=ticket_id)


@login_required
@require_http_methods(["POST"])
def reopen_ticket(request, ticket_id):
    """Reopen a closed ticket."""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, user=request.user)
    
    ticket.status = 'reopened'
    ticket.save()
    
    messages.success(request, _('Ticket has been reopened.'))
    return redirect('support:ticket_detail', ticket_id=ticket_id)


# ==================== FAQ ====================

@require_http_methods(["GET"])
def faq_list(request):
    """List all FAQs."""
    faqs = FAQ.objects.filter(is_active=True).select_related('category')
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(FAQCategory, slug=category_slug, is_active=True)
        faqs = faqs.filter(category=category)
    
    # Search
    query = request.GET.get('q')
    if query:
        faqs = faqs.filter(
            Q(question__icontains=query) | 
            Q(answer__icontains=query) | 
            Q(category__name__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(faqs, 20)
    page = request.GET.get('page')
    
    try:
        faqs_page = paginator.page(page)
    except PageNotAnInteger:
        faqs_page = paginator.page(1)
    except EmptyPage:
        faqs_page = paginator.page(paginator.num_pages)
    
    categories = FAQCategory.objects.filter(is_active=True)
    
    context = {
        'faqs': faqs_page,
        'categories': categories,
        'current_category': category_slug,
        'query': query,
        'title': _('Frequently Asked Questions'),
    }
    return render(request, 'support/faq_list.html', context)


@require_http_methods(["GET"])
def faq_detail(request, slug):
    """FAQ detail page."""
    faq = get_object_or_404(FAQ, slug=slug, is_active=True)
    
    # Increment view count
    faq.view_count += 1
    faq.save()
    
    # Related FAQs
    related_faqs = FAQ.objects.filter(
        category=faq.category,
        is_active=True
    ).exclude(pk=faq.pk).order_by('-view_count')[:5]
    
    context = {
        'faq': faq,
        'related_faqs': related_faqs,
        'title': faq.question,
        'meta_title': faq.meta_title or faq.question,
        'meta_description': faq.meta_description or faq.answer[:200],
    }
    return render(request, 'support/faq_detail.html', context)


# ==================== CONTACT ====================

@require_http_methods(["GET", "POST"])
def contact(request):
    """Contact form page."""
    if request.method == 'POST':
        form = ContactForm(data=request.POST)
        if form.is_valid():
            contact_message = ContactMessage.objects.create(
                name=form.cleaned_data.get('name'),
                email=form.cleaned_data.get('email'),
                phone=form.cleaned_data.get('phone'),
                subject=form.cleaned_data.get('subject'),
                message=form.cleaned_data.get('message'),
                department=form.cleaned_data.get('department'),
                user=request.user if request.user.is_authenticated else None,
                ip_address=request.META.get('REMOTE_ADDR'),
            )
            
            # Send email
            send_mail(
                subject=f'Contact Form: {form.cleaned_data.get("subject")}',
                message=f"Name: {form.cleaned_data.get('name')}\n"
                       f"Email: {form.cleaned_data.get('email')}\n"
                       f"Phone: {form.cleaned_data.get('phone')}\n\n"
                       f"{form.cleaned_data.get('message')}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.SUPPORT_EMAIL],
                fail_silently=True,
            )
            
            messages.success(request, _('Your message has been sent. We will get back to you soon.'))
            return redirect('support:contact')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'title': _('Contact Us'),
    }
    return render(request, 'support/contact.html', context)


# ==================== LIVE CHAT ====================

@login_required
@require_http_methods(["GET"])
def live_chat(request):
    """Live chat page."""
    # Get or create chat session
    session = LiveChatSession.objects.filter(
        user=request.user,
        is_active=True
    ).first()
    
    if not session:
        session = LiveChatSession.objects.create(
            user=request.user,
            session_id=f'session_{request.user.id}_{timezone.now().timestamp()}',
        )
    
    # Get messages
    messages = LiveChatMessage.objects.filter(
        session=session
    ).select_related('user', 'admin_user').order_by('created_at')[:50]
    
    context = {
        'session': session,
        'messages': messages,
        'title': _('Live Chat'),
    }
    return render(request, 'support/live_chat.html', context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def send_chat_message(request):
    """Send a chat message via AJAX."""
    session_id = request.POST.get('session_id')
    message_content = request.POST.get('message')
    
    session = get_object_or_404(LiveChatSession, session_id=session_id, user=request.user)
    
    message = LiveChatMessage.objects.create(
        session=session,
        user=request.user,
        content=message_content,
        is_admin=False,
    )
    
    # Update session last activity
    session.last_activity = timezone.now()
    session.save()
    
    return JsonResponse({
        'success': True,
        'message': {
            'id': str(message.id),
            'content': message.content,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user': {
                'name': request.user.get_full_name() or request.user.username,
                'is_admin': False,
            }
        }
    })


@login_required
@require_http_methods(["GET"])
@csrf_exempt
def get_chat_messages(request):
    """Get chat messages via AJAX."""
    session_id = request.GET.get('session_id')
    last_message_id = request.GET.get('last_message_id')
    
    session = get_object_or_404(LiveChatSession, session_id=session_id, user=request.user)
    
    messages = LiveChatMessage.objects.filter(session=session)
    
    if last_message_id:
        messages = messages.filter(id__gt=last_message_id)
    
    messages = messages.select_related('user', 'admin_user').order_by('created_at')
    
    messages_data = []
    for message in messages:
        messages_data.append({
            'id': str(message.id),
            'content': message.content,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user': {
                'name': message.get_sender_name(),
                'is_admin': message.is_admin,
            }
        })
    
    return JsonResponse({
        'messages': messages_data,
        'has_more': False,  # Implement pagination if needed
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def end_chat_session(request):
    """End a chat session."""
    session_id = request.POST.get('session_id')
    
    session = get_object_or_404(LiveChatSession, session_id=session_id, user=request.user)
    session.is_active = False
    session.ended_at = timezone.now()
    session.save()
    
    return JsonResponse({'success': True})


# ==================== SEARCH ====================

@require_http_methods(["GET", "POST"])
def ticket_search(request):
    """Search tickets."""
    form = TicketSearchForm(data=request.GET or None)
    
    tickets = Ticket.objects.none()
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        
        tickets = Ticket.objects.filter(user=request.user)
        
        if query:
            tickets = tickets.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) | 
                Q(ticket_id__icontains=query)
            )
        
        if category:
            tickets = tickets.filter(category=category)
        
        if status:
            tickets = tickets.filter(status=status)
        
        tickets = tickets.select_related('category').order_by('-created_at')
    
    context = {
        'form': form,
        'tickets': tickets,
        'title': _('Search Tickets'),
    }
    return render(request, 'support/ticket_search.html', context)


# ==================== AJAX VIEWS ====================

@require_http_methods(["GET"])
def get_faq_categories_ajax(request):
    """Get FAQ categories via AJAX."""
    categories = FAQCategory.objects.filter(is_active=True)
    
    categories_data = []
    for category in categories:
        categories_data.append({
            'id': str(category.id),
            'name': category.name,
            'slug': category.slug,
            'faq_count': FAQ.objects.filter(category=category, is_active=True).count(),
        })
    
    return JsonResponse({'categories': categories_data})


@require_http_methods(["GET"])
def get_ticket_status_ajax(request, ticket_id):
    """Get ticket status via AJAX."""
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    
    if ticket.user != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    return JsonResponse({
        'status': ticket.status,
        'unread_messages': TicketMessage.objects.filter(
            ticket=ticket,
            created_at__gt=ticket.user_read_at or timezone.now()
        ).count(),
    })


@require_http_methods(["POST"])
def upload_ticket_attachment_ajax(request):
    """Upload attachment via AJAX."""
    if not request.FILES.get('file'):
        return JsonResponse({'error': 'No file provided'}, status=400)
    
    file = request.FILES['file']
    
    # In a real implementation, save to temporary storage
    # For now, return success
    return JsonResponse({
        'success': True,
        'file_name': file.name,
        'file_size': file.size,
    })
