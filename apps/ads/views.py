"""
Views for ads app.
Manages advertisement slots, ads, impressions, and clicks.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from django.conf import settings

from .models import AdSlot, Advertisement, AdImpression, AdClick
from .forms import AdSlotForm, AdvertisementForm, AdSearchForm, AdStatsForm
from .services import AdService, AdRotationService, AdReportService


def is_staff(user):
    """Check if user is staff."""
    return user.is_staff


# ==================== AD DISPLAY VIEWS ====================

@require_http_methods(["GET"])
def display_ad(request, slot_code):
    """Display advertisement for a slot."""
    ad = AdService.get_current_ad(slot_code, request)
    
    if not ad:
        # Return empty response or default content
        return HttpResponse('', content_type='text/html')
    
    # Track impression
    AdService.track_impression(ad, request)
    
    # Render appropriate template based on ad type
    if ad.ad_type == 'image':
        return render(request, 'ads/includes/ad_image.html', {'ad': ad})
    elif ad.ad_type == 'html':
        return HttpResponse(ad.html_content, content_type='text/html')
    elif ad.ad_type == 'script':
        return HttpResponse(ad.script_content, content_type='application/javascript')
    elif ad.ad_type == 'video':
        return render(request, 'ads/includes/ad_video.html', {'ad': ad})
    else:
        return HttpResponse('', content_type='text/html')


@require_http_methods(["GET"])
def display_ad_responsive(request, slot_code, width, height):
    """Display responsive advertisement for a slot with specific dimensions."""
    ad = AdService.get_current_ad(slot_code, request)
    
    if not ad:
        return HttpResponse('', content_type='text/html')
    
    # Track impression
    AdService.track_impression(ad, request)
    
    context = {
        'ad': ad,
        'width': width,
        'height': height,
    }
    
    if ad.ad_type == 'image':
        return render(request, 'ads/includes/ad_image_responsive.html', context)
    elif ad.ad_type == 'html':
        return HttpResponse(ad.html_content, content_type='text/html')
    elif ad.ad_type == 'script':
        return HttpResponse(ad.script_content, content_type='application/javascript')
    elif ad.ad_type == 'video':
        return render(request, 'ads/includes/ad_video_responsive.html', context)
    else:
        return HttpResponse('', content_type='text/html')


# ==================== TRACKING VIEWS ====================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def track_impression(request, ad_id):
    """Track ad impression."""
    ad = get_object_or_404(Advertisement, pk=ad_id)
    
    # Track impression
    AdService.track_impression(ad, request)
    
    # Return 1x1 transparent pixel for tracking
    response = HttpResponse(content_type='image/png')
    response.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82')
    return response


@csrf_exempt
@require_http_methods(["GET", "POST"])
def track_click(request, ad_id):
    """Track ad click and redirect."""
    ad = get_object_or_404(Advertisement, pk=ad_id)
    
    # Track click
    click = AdService.track_click(ad, request)
    
    # Redirect to ad URL if available
    if ad.url:
        return redirect(ad.url)
    
    return redirect('store:home')


# ==================== AD SLOT MANAGEMENT ====================

@login_required
@user_passes_test(is_staff)
def ad_slot_list(request):
    """List all ad slots."""
    slots = AdSlot.objects.all().order_by('name')
    
    # Search
    query = request.GET.get('q')
    if query:
        slots = slots.filter(
            Q(name__icontains=query) | 
            Q(code__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(slots, 20)
    page = request.GET.get('page')
    
    try:
        slots_page = paginator.page(page)
    except PageNotAnInteger:
        slots_page = paginator.page(1)
    except EmptyPage:
        slots_page = paginator.page(paginator.num_pages)
    
    context = {
        'slots': slots_page,
        'query': query,
        'page_title': _('مدیریت Slot‌های تبلیغاتی'),
    }
    return render(request, 'admin_panel/ads.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def ad_slot_create(request):
    """Create a new ad slot."""
    if request.method == 'POST':
        form = AdSlotForm(data=request.POST)
        if form.is_valid():
            slot = form.save()
            messages.success(request, _('Slot تبلیغاتی با موفقیت ایجاد شد.'))
            return redirect('ads:ad_slot_list')
        else:
            messages.error(request, _('لطفاً خطاهای زیر را اصلاح کنید.'))
    else:
        form = AdSlotForm()
    
    context = {
        'form': form,
        'page_title': _('ایجاد Slot تبلیغاتی'),
    }
    return render(request, 'admin_panel/ad_slot_form.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def ad_slot_edit(request, pk):
    """Edit an ad slot."""
    slot = get_object_or_404(AdSlot, pk=pk)
    
    if request.method == 'POST':
        form = AdSlotForm(data=request.POST, instance=slot)
        if form.is_valid():
            form.save()
            # Clear cache for this slot
            AdService.clear_ad_cache(slot_code=slot.code)
            messages.success(request, _('Slot تبلیغاتی با موفقیت بروزرسانی شد.'))
            return redirect('ads:ad_slot_list')
        else:
            messages.error(request, _('لطفاً خطاهای زیر را اصلاح کنید.'))
    else:
        form = AdSlotForm(instance=slot)
    
    context = {
        'form': form,
        'slot': slot,
        'page_title': _('ویرایش Slot تبلیغاتی'),
    }
    return render(request, 'admin_panel/ad_slot_form.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def ad_slot_delete(request, pk):
    """Delete an ad slot."""
    slot = get_object_or_404(AdSlot, pk=pk)
    
    # Check if slot has ads
    if Advertisement.objects.filter(slot=slot).exists():
        messages.error(request, _('نمی‌توان Slot را حذف کرد زیرا حاوی تبلیغات است.'))
        return redirect('ads:ad_slot_list')
    
    slot.delete()
    messages.success(request, _('Slot تبلیغاتی حذف شد.'))
    return redirect('ads:ad_slot_list')


# ==================== ADVERTISEMENT MANAGEMENT ====================

@login_required
@user_passes_test(is_staff)
def ad_list(request):
    """List all advertisements."""
    ads = Advertisement.objects.select_related('slot', 'created_by').order_by('-priority', '-created_at')
    
    # Filter by slot
    slot_id = request.GET.get('slot')
    if slot_id:
        ads = ads.filter(slot__id=slot_id)
    
    # Filter by status
    is_active = request.GET.get('is_active')
    if is_active:
        ads = ads.filter(is_active=(is_active == '1'))
    
    # Filter by ad type
    ad_type = request.GET.get('ad_type')
    if ad_type:
        ads = ads.filter(ad_type=ad_type)
    
    # Search
    query = request.GET.get('q')
    if query:
        ads = ads.filter(
            Q(name__icontains=query) | 
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(ads, 20)
    page = request.GET.get('page')
    
    try:
        ads_page = paginator.page(page)
    except PageNotAnInteger:
        ads_page = paginator.page(1)
    except EmptyPage:
        ads_page = paginator.page(paginator.num_pages)
    
    slots = AdSlot.objects.filter(is_active=True)
    
    context = {
        'ads': ads_page,
        'slots': slots,
        'current_slot': slot_id,
        'current_active': is_active,
        'current_type': ad_type,
        'query': query,
        'page_title': _('مدیریت تبلیغات'),
    }
    return render(request, 'admin_panel/ads.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def ad_create(request):
    """Create a new advertisement."""
    slots = AdSlot.objects.filter(is_active=True)
    
    if request.method == 'POST':
        form = AdvertisementForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.created_by = request.user
            ad.save()
            
            # Clear cache for this slot
            AdService.clear_ad_cache(slot_code=ad.slot.code)
            
            messages.success(request, _('تبلیغ با موفقیت ایجاد شد.'))
            return redirect('ads:ad_list')
        else:
            messages.error(request, _('لطفاً خطاهای زیر را اصلاح کنید.'))
    else:
        form = AdvertisementForm()
    
    context = {
        'form': form,
        'slots': slots,
        'page_title': _('ایجاد تبلیغ جدید'),
    }
    return render(request, 'admin_panel/ad_form.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def ad_edit(request, pk):
    """Edit an advertisement."""
    ad = get_object_or_404(Advertisement, pk=pk)
    slots = AdSlot.objects.filter(is_active=True)
    
    if request.method == 'POST':
        form = AdvertisementForm(data=request.POST, files=request.FILES, instance=ad)
        if form.is_valid():
            ad = form.save()
            # Clear cache for this slot
            AdService.clear_ad_cache(slot_code=ad.slot.code)
            messages.success(request, _('تبلیغ با موفقیت بروزرسانی شد.'))
            return redirect('ads:ad_list')
        else:
            messages.error(request, _('لطفاً خطاهای زیر را اصلاح کنید.'))
    else:
        form = AdvertisementForm(instance=ad)
    
    context = {
        'form': form,
        'ad': ad,
        'slots': slots,
        'page_title': _('ویرایش تبلیغ'),
    }
    return render(request, 'admin_panel/ad_form.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def ad_delete(request, pk):
    """Delete an advertisement."""
    ad = get_object_or_404(Advertisement, pk=pk)
    slot_code = ad.slot.code
    ad.delete()
    
    # Clear cache for this slot
    AdService.clear_ad_cache(slot_code=slot_code)
    
    messages.success(request, _('تبلیغ حذف شد.'))
    return redirect('ads:ad_list')


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def ad_toggle_active(request, pk):
    """Toggle ad active status."""
    ad = get_object_or_404(Advertisement, pk=pk)
    ad.is_active = not ad.is_active
    ad.save()
    
    # Clear cache for this slot
    AdService.clear_ad_cache(slot_code=ad.slot.code)
    
    return JsonResponse({
        'success': True,
        'is_active': ad.is_active
    })


@login_required
@user_passes_test(is_staff)
def ad_stats(request, pk):
    """Advertisement statistics page."""
    ad = get_object_or_404(Advertisement, pk=pk)
    
    # Get stats
    stats = AdService.get_ad_stats(pk)
    
    # Get recent impressions
    recent_impressions = AdImpression.objects.filter(
        ad=ad
    ).select_related('user').order_by('-created_at')[:20]
    
    # Get recent clicks
    recent_clicks = AdClick.objects.filter(
        ad=ad
    ).select_related('user').order_by('-created_at')[:20]
    
    # Get daily stats for chart
    from django.db.models.functions import TruncDate
    from django.db.models import Count
    
    daily_impressions = AdImpression.objects.filter(ad=ad).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')[:30]
    
    daily_clicks = AdClick.objects.filter(ad=ad).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')[:30]
    
    context = {
        'ad': ad,
        'stats': stats,
        'recent_impressions': recent_impressions,
        'recent_clicks': recent_clicks,
        'daily_impressions': list(daily_impressions),
        'daily_clicks': list(daily_clicks),
        'page_title': f"{_('آمار تبلیغ')} - {ad.name}",
    }
    return render(request, 'admin_panel/ad_stats.html', context)


# ==================== REPORT VIEWS ====================

@login_required
@user_passes_test(is_staff)
def ads_report(request):
    """Overall ads report."""
    # Get overall stats
    stats = AdService.get_all_stats()
    
    # Get top performing ads
    top_ads = Advertisement.objects.filter(
        click_count__gt=0
    ).order_by('-click_count')[:10]
    
    # Get recent activity
    recent_impressions = AdImpression.objects.select_related('ad').order_by('-created_at')[:10]
    recent_clicks = AdClick.objects.select_related('ad').order_by('-created_at')[:10]
    
    context = {
        'stats': stats,
        'top_ads': top_ads,
        'recent_impressions': recent_impressions,
        'recent_clicks': recent_clicks,
        'page_title': _('گزارش کلی تبلیغات'),
    }
    return render(request, 'admin_panel/reports.html', context)


@login_required
@user_passes_test(is_staff)
def impression_report(request):
    """Impression report."""
    form = AdStatsForm(request.GET or None)
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    slot_id = request.GET.get('slot')
    
    report = AdReportService.get_impression_report(date_from, date_to, slot_id)
    
    context = {
        'form': form,
        'report': report,
        'page_title': _('گزارش نمایش‌ها'),
    }
    return render(request, 'admin_panel/impression_report.html', context)


@login_required
@user_passes_test(is_staff)
def click_report(request):
    """Click report."""
    form = AdStatsForm(request.GET or None)
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    slot_id = request.GET.get('slot')
    
    report = AdReportService.get_click_report(date_from, date_to, slot_id)
    
    context = {
        'form': form,
        'report': report,
        'page_title': _('گزارش کلیک‌ها'),
    }
    return render(request, 'admin_panel/click_report.html', context)


@login_required
@user_passes_test(is_staff)
def performance_report(request):
    """Performance report."""
    form = AdStatsForm(request.GET or None)
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    report = AdReportService.get_performance_report(date_from, date_to)
    
    context = {
        'form': form,
        'report': report,
        'page_title': _('گزارش عملکرد تبلیغات'),
    }
    return render(request, 'admin_panel/performance_report.html', context)


# ==================== AJAX VIEWS ====================

@require_http_methods(["GET"])
def get_ad_json(request, slot_code):
    """Get ad data as JSON for a slot."""
    ad = AdService.get_current_ad(slot_code, request)
    
    if not ad:
        return JsonResponse({'error': 'No ad found for this slot'}, status=404)
    
    ad_data = {
        'id': str(ad.id),
        'name': ad.name,
        'title': ad.title,
        'description': ad.description,
        'ad_type': ad.ad_type,
        'image_url': ad.image.url if ad.image else None,
        'html_content': ad.html_content,
        'script_content': ad.script_content,
        'video_url': ad.video_url,
        'video_embed_code': ad.video_embed_code,
        'url': ad.url,
        'target': ad.target,
        'priority': ad.priority,
        'is_active': ad.is_active,
    }
    
    return JsonResponse(ad_data)


@require_http_methods(["GET"])
def get_ad_stats_json(request, ad_id):
    """Get ad statistics as JSON."""
    stats = AdService.get_ad_stats(ad_id)
    
    if not stats:
        return JsonResponse({'error': 'Ad not found'}, status=404)
    
    return JsonResponse(stats)


@require_http_methods(["GET"])
def get_slot_stats_json(request, slot_code):
    """Get slot statistics as JSON."""
    stats = AdService.get_slot_stats(slot_code)
    
    if not stats:
        return JsonResponse({'error': 'Slot not found'}, status=404)
    
    return JsonResponse(stats)


@require_http_methods(["GET"])
def get_all_stats_json(request):
    """Get all advertisement statistics as JSON."""
    stats = AdService.get_all_stats()
    
    return JsonResponse(stats)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def clear_ad_cache(request):
    """Clear ad cache."""
    slot_code = request.POST.get('slot_code')
    ad_id = request.POST.get('ad_id')
    
    if slot_code:
        AdService.clear_ad_cache(slot_code=slot_code)
    if ad_id:
        AdService.clear_ad_cache(ad_id=ad_id)
    
    return JsonResponse({'success': True})


# ==================== PUBLIC VIEWS ====================

@require_http_methods(["GET"])
def view_ad(request, ad_id):
    """Public view for an ad."""
    ad = get_object_or_404(Advertisement, pk=ad_id, is_active=True)
    
    # Check if ad is valid
    if not ad.is_valid():
        return redirect('store:home')
    
    # Track impression
    AdService.track_impression(ad, request)
    
    # Track click if this is a click request
    if request.GET.get('track') == 'click':
        AdService.track_click(ad, request)
        if ad.url:
            return redirect(ad.url)
    
    context = {
        'ad': ad,
        'page_title': ad.title or ad.name,
    }
    
    if ad.ad_type == 'image':
        return render(request, 'ads/ad_detail_image.html', context)
    elif ad.ad_type == 'html':
        return render(request, 'ads/ad_detail_html.html', context)
    elif ad.ad_type == 'video':
        return render(request, 'ads/ad_detail_video.html', context)
    else:
        return render(request, 'ads/ad_detail.html', context)
