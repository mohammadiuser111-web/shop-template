"""
Views for notifications app.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.utils import timezone
from django.conf import settings

from .models import (
    Notification, NotificationTemplate, NotificationPreference,
    EmailNotification, PushNotification, SMSNotification,
    NotificationCategory
)
from .forms import (
    NotificationForm, NotificationTemplateForm,
    NotificationPreferenceForm, NotificationSearchForm
)
from apps.accounts.models import User


def is_staff(user):
    """Check if user is staff."""
    return user.is_staff


# ==================== NOTIFICATIONS ====================

@login_required
@require_http_methods(["GET"])
def notification_list(request):
    """List user's notifications."""
    # Filter by status
    status_filter = request.GET.get('status', 'unread')
    category_filter = request.GET.get('category')
    search_query = request.GET.get('q')
    
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender', 'template', 'category').order_by('-created_at')
    
    if status_filter == 'unread':
        notifications = notifications.filter(is_read=False)
    elif status_filter == 'read':
        notifications = notifications.filter(is_read=True)
    elif status_filter == 'archived':
        notifications = notifications.filter(is_archived=True)
    
    if category_filter:
        notifications = notifications.filter(category__id=category_filter)
    
    if search_query:
        notifications = notifications.filter(
            Q(title__icontains=search_query) | 
            Q(message__icontains=search_query) | 
            Q(template__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page')
    
    try:
        notifications_page = paginator.page(page)
    except PageNotAnInteger:
        notifications_page = paginator.page(1)
    except EmptyPage:
        notifications_page = paginator.page(paginator.num_pages)
    
    categories = NotificationCategory.objects.filter(is_active=True)
    
    context = {
        'notifications': notifications_page,
        'categories': categories,
        'current_status': status_filter,
        'current_category': category_filter,
        'search_query': search_query,
        'title': _('My Notifications'),
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
@require_http_methods(["GET"])
def notification_detail(request, notification_id):
    """Notification detail page."""
    notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
    
    # Mark as read
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
    
    context = {
        'notification': notification,
        'title': notification.title,
    }
    return render(request, 'notifications/notification_detail.html', context)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
    
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    """Mark all notifications as read."""
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    )
    
    notifications.update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def archive_notification(request, notification_id):
    """Archive a notification."""
    notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
    
    notification.is_archived = True
    notification.archived_at = timezone.now()
    notification.save()
    
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def delete_notification(request, notification_id):
    """Delete a notification."""
    notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
    
    notification.delete()
    
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def delete_all_notifications(request):
    """Delete all notifications."""
    notifications = Notification.objects.filter(recipient=request.user)
    notifications.delete()
    
    return JsonResponse({'success': True})


# ==================== NOTIFICATION TEMPLATES ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def template_list(request):
    """List notification templates."""
    templates = NotificationTemplate.objects.all()
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        templates = templates.filter(category__id=category_filter)
    
    # Search
    query = request.GET.get('q')
    if query:
        templates = templates.filter(
            Q(name__icontains=query) | 
            Q(subject__icontains=query) | 
            Q(message__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(templates, 20)
    page = request.GET.get('page')
    
    try:
        templates_page = paginator.page(page)
    except PageNotAnInteger:
        templates_page = paginator.page(1)
    except EmptyPage:
        templates_page = paginator.page(paginator.num_pages)
    
    categories = NotificationCategory.objects.filter(is_active=True)
    
    context = {
        'templates': templates_page,
        'categories': categories,
        'current_category': category_filter,
        'query': query,
        'title': _('Notification Templates'),
    }
    return render(request, 'notifications/template_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_template(request):
    """Create a new notification template."""
    if request.method == 'POST':
        form = NotificationTemplateForm(data=request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            
            messages.success(request, _('Notification template created successfully.'))
            return redirect('notifications:template_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = NotificationTemplateForm()
    
    context = {
        'form': form,
        'title': _('Create Notification Template'),
    }
    return render(request, 'notifications/create_template.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_template(request, template_id):
    """Edit a notification template."""
    template = get_object_or_404(NotificationTemplate, pk=template_id)
    
    if request.method == 'POST':
        form = NotificationTemplateForm(data=request.POST, instance=template)
        if form.is_valid():
            template = form.save()
            messages.success(request, _('Notification template updated.'))
            return redirect('notifications:template_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = NotificationTemplateForm(instance=template)
    
    context = {
        'template': template,
        'form': form,
        'title': _('Edit Notification Template'),
    }
    return render(request, 'notifications/edit_template.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def delete_template(request, template_id):
    """Delete a notification template."""
    template = get_object_or_404(NotificationTemplate, pk=template_id)
    
    # Check if template is used
    if Notification.objects.filter(template=template).exists():
        messages.error(request, _('Cannot delete a template that is in use.'))
        return redirect('notifications:template_list')
    
    template.delete()
    messages.success(request, _('Notification template deleted.'))
    return redirect('notifications:template_list')


# ==================== NOTIFICATION PREFERENCES ====================

@login_required
@require_http_methods(["GET", "POST"])
def notification_preferences(request):
    """Manage user's notification preferences."""
    preferences = NotificationPreference.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = NotificationPreferenceForm(data=request.POST)
        if form.is_valid():
            # Save preferences
            category = form.cleaned_data.get('category')
            channel = form.cleaned_data.get('channel')
            is_enabled = form.cleaned_data.get('is_enabled')
            
            # Update or create preference
            preference, created = NotificationPreference.objects.get_or_create(
                user=request.user,
                category=category,
                channel=channel,
                defaults={'is_enabled': is_enabled}
            )
            
            if not created:
                preference.is_enabled = is_enabled
                preference.save()
            
            messages.success(request, _('Notification preferences updated.'))
            return redirect('notifications:notification_preferences')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = NotificationPreferenceForm()
    
    # Get all preferences grouped by category
    categories = NotificationCategory.objects.filter(is_active=True)
    channels = ['email', 'push', 'sms', 'web']
    
    preferences_matrix = {}
    for category in categories:
        preferences_matrix[str(category.id)] = {
            'category': category,
            'email': False,
            'push': False,
            'sms': False,
            'web': False,
        }
    
    for preference in preferences:
        if str(preference.category_id) in preferences_matrix:
            preferences_matrix[str(preference.category_id)][preference.channel] = preference.is_enabled
    
    context = {
        'form': form,
        'categories': categories,
        'channels': channels,
        'preferences_matrix': preferences_matrix,
        'title': _('Notification Preferences'),
    }
    return render(request, 'notifications/notification_preferences.html', context)


@login_required
@require_http_methods(["POST"])
def update_preferences_ajax(request):
    """Update notification preferences via AJAX."""
    category_id = request.POST.get('category_id')
    channel = request.POST.get('channel')
    is_enabled = request.POST.get('is_enabled') == 'true'
    
    if not category_id or not channel:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    category = get_object_or_404(NotificationCategory, pk=category_id)
    
    # Update or create preference
    preference, created = NotificationPreference.objects.get_or_create(
        user=request.user,
        category=category,
        channel=channel,
        defaults={'is_enabled': is_enabled}
    )
    
    if not created:
        preference.is_enabled = is_enabled
        preference.save()
    
    return JsonResponse({'success': True, 'is_enabled': is_enabled})


# ==================== NOTIFICATION CATEGORIES ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def category_list(request):
    """List notification categories."""
    categories = NotificationCategory.objects.all()
    
    # Search
    query = request.GET.get('q')
    if query:
        categories = categories.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(categories, 20)
    page = request.GET.get('page')
    
    try:
        categories_page = paginator.page(page)
    except PageNotAnInteger:
        categories_page = paginator.page(1)
    except EmptyPage:
        categories_page = paginator.page(paginator.num_pages)
    
    context = {
        'categories': categories_page,
        'query': query,
        'title': _('Notification Categories'),
    }
    return render(request, 'notifications/category_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_category(request):
    """Create a new notification category."""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == '1'
        
        category = NotificationCategory.objects.create(
            name=name,
            description=description,
            is_active=is_active,
            created_by=request.user,
        )
        
        messages.success(request, _('Notification category created successfully.'))
        return redirect('notifications:category_list')
    
    context = {
        'title': _('Create Notification Category'),
    }
    return render(request, 'notifications/create_category.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_category(request, category_id):
    """Edit a notification category."""
    category = get_object_or_404(NotificationCategory, pk=category_id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        category.is_active = request.POST.get('is_active') == '1'
        category.save()
        
        messages.success(request, _('Notification category updated.'))
        return redirect('notifications:category_list')
    
    context = {
        'category': category,
        'title': _('Edit Notification Category'),
    }
    return render(request, 'notifications/edit_category.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def delete_category(request, category_id):
    """Delete a notification category."""
    category = get_object_or_404(NotificationCategory, pk=category_id)
    
    # Check if category is used
    if NotificationTemplate.objects.filter(category=category).exists():
        messages.error(request, _('Cannot delete a category that is in use.'))
        return redirect('notifications:category_list')
    
    if Notification.objects.filter(category=category).exists():
        messages.error(request, _('Cannot delete a category that has notifications.'))
        return redirect('notifications:category_list')
    
    category.delete()
    messages.success(request, _('Notification category deleted.'))
    return redirect('notifications:category_list')


# ==================== NOTIFICATION SENDING ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def send_notification(request):
    """Send a notification to users."""
    if request.method == 'POST':
        form = NotificationForm(data=request.POST)
        if form.is_valid():
            notification = Notification.objects.create(
                sender=request.user,
                title=form.cleaned_data.get('title'),
                message=form.cleaned_data.get('message'),
                notification_type=form.cleaned_data.get('notification_type'),
                category=form.cleaned_data.get('category'),
                template=form.cleaned_data.get('template'),
                url=form.cleaned_data.get('url'),
                is_priority=form.cleaned_data.get('is_priority'),
            )
            
            # Send to selected users/groups
            recipients = form.cleaned_data.get('recipients')
            user_groups = form.cleaned_data.get('user_groups')
            
            if recipients:
                for user in recipients:
                    Notification.objects.create(
                        sender=request.user,
                        recipient=user,
                        title=notification.title,
                        message=notification.message,
                        notification_type=notification.notification_type,
                        category=notification.category,
                        template=notification.template,
                        url=notification.url,
                        is_priority=notification.is_priority,
                        parent=notification,
                    )
            
            if user_groups:
                for group in user_groups:
                    for user in group.user_set.all():
                        Notification.objects.create(
                            sender=request.user,
                            recipient=user,
                            title=notification.title,
                            message=notification.message,
                            notification_type=notification.notification_type,
                            category=notification.category,
                            template=notification.template,
                            url=notification.url,
                            is_priority=notification.is_priority,
                            parent=notification,
                        )
            
            messages.success(request, _('Notification sent successfully.'))
            return redirect('notifications:notification_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = NotificationForm()
    
    context = {
        'form': form,
        'title': _('Send Notification'),
    }
    return render(request, 'notifications/send_notification.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def send_bulk_notification(request):
    """Send bulk notification via AJAX."""
    title = request.POST.get('title')
    message = request.POST.get('message')
    notification_type = request.POST.get('notification_type')
    user_ids = request.POST.getlist('user_ids[]')
    
    if not title or not message or not user_ids:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    # Create parent notification
    parent = Notification.objects.create(
        sender=request.user,
        title=title,
        message=message,
        notification_type=notification_type,
        is_bulk=True,
    )
    
    # Send to each user
    sent_count = 0
    for user_id in user_ids:
        user = get_object_or_404(User, pk=user_id)
        Notification.objects.create(
            sender=request.user,
            recipient=user,
            title=title,
            message=message,
            notification_type=notification_type,
            parent=parent,
        )
        sent_count += 1
    
    return JsonResponse({
        'success': True,
        'sent_count': sent_count,
    })


# ==================== NOTIFICATION DASHBOARD ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def notification_dashboard(request):
    """Notification dashboard."""
    # Get counts
    total_notifications = Notification.objects.count()
    unread_notifications = Notification.objects.filter(is_read=False).count()
    total_templates = NotificationTemplate.objects.count()
    total_categories = NotificationCategory.objects.count()
    
    # Get recent notifications
    recent_notifications = Notification.objects.order_by('-created_at')[:10]
    
    # Get most used templates
    most_used_templates = Notification.objects.values('template__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Get notification statistics by type
    by_type = Notification.objects.values('notification_type').annotate(
        count=Count('id')
    )
    
    # Get notification statistics by category
    by_category = Notification.objects.values('category__name').annotate(
        count=Count('id')
    )
    
    context = {
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'total_templates': total_templates,
        'total_categories': total_categories,
        'recent_notifications': recent_notifications,
        'most_used_templates': most_used_templates,
        'by_type': by_type,
        'by_category': by_category,
        'title': _('Notification Dashboard'),
    }
    return render(request, 'notifications/notification_dashboard.html', context)


# ==================== AJAX VIEWS ====================

@login_required
@require_http_methods(["GET"])
def get_unread_count_ajax(request):
    """Get unread notification count via AJAX."""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False,
        is_archived=False
    ).count()
    
    return JsonResponse({'count': count})


@login_required
@require_http_methods(["GET"])
def get_recent_notifications_ajax(request):
    """Get recent notifications via AJAX."""
    limit = request.GET.get('limit', 10)
    
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_archived=False
    ).select_related('sender', 'category').order_by('-created_at')[:int(limit)]
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': str(notification.id),
            'title': notification.title,
            'message': notification.message[:100] + '...' if len(notification.message) > 100 else notification.message,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'sender': notification.sender.get_full_name() or notification.sender.username if notification.sender else None,
            'category': notification.category.name if notification.category else None,
            'url': notification.url,
        })
    
    return JsonResponse({'notifications': notifications_data})


@login_required
@require_http_methods(["GET"])
def get_notification_preferences_ajax(request):
    """Get user's notification preferences via AJAX."""
    preferences = NotificationPreference.objects.filter(user=request.user)
    
    preferences_data = {}
    for preference in preferences:
        key = f"{preference.category_id}_{preference.channel}"
        preferences_data[key] = preference.is_enabled
    
    return JsonResponse({'preferences': preferences_data})


@login_required
@require_http_methods(["POST"])
def mark_notification_read_ajax(request, notification_id):
    """Mark notification as read via AJAX."""
    notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
    
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["GET"])
def get_notification_stats_ajax(request):
    """Get notification statistics via AJAX."""
    total = Notification.objects.filter(recipient=request.user).count()
    unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    archived = Notification.objects.filter(recipient=request.user, is_archived=True).count()
    
    return JsonResponse({
        'total': total,
        'unread': unread,
        'archived': archived,
    })


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def get_template_list_ajax(request):
    """Get template list via AJAX."""
    templates = NotificationTemplate.objects.all()
    
    templates_data = []
    for template in templates:
        templates_data.append({
            'id': str(template.id),
            'name': template.name,
            'subject': template.subject,
            'message': template.message[:100] + '...' if len(template.message) > 100 else template.message,
            'category': template.category.name if template.category else None,
            'is_active': template.is_active,
        })
    
    return JsonResponse({'templates': templates_data})


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def get_category_list_ajax(request):
    """Get category list via AJAX."""
    categories = NotificationCategory.objects.filter(is_active=True)
    
    categories_data = []
    for category in categories:
        categories_data.append({
            'id': str(category.id),
            'name': category.name,
            'description': category.description,
            'is_active': category.is_active,
        })
    
    return JsonResponse({'categories': categories_data})
