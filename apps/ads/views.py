"""
Views for ads app.
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

from .models import (
    Ad, AdGroup, AdCampaign, AdPlacement, AdClick, AdImpression,
    AdConversion, AdTargeting, AdBudget
)
from .forms import (
    AdForm, AdGroupForm, AdCampaignForm, AdPlacementForm,
    AdSearchForm, AdReportForm
)
from apps.products.models import Product, Category, Brand
from apps.orders.models import Order


def is_staff(user):
    """Check if user is staff."""
    return user.is_staff


# ==================== AD CAMPAIGNS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def campaign_list(request):
    """List all ad campaigns."""
    campaigns = AdCampaign.objects.filter(
        created_by=request.user
    ).select_related('ad_group').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        campaigns = campaigns.filter(status=status_filter)
    
    # Search
    query = request.GET.get('q')
    if query:
        campaigns = campaigns.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(campaign_id__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(campaigns, 20)
    page = request.GET.get('page')
    
    try:
        campaigns_page = paginator.page(page)
    except PageNotAnInteger:
        campaigns_page = paginator.page(1)
    except EmptyPage:
        campaigns_page = paginator.page(paginator.num_pages)
    
    context = {
        'campaigns': campaigns_page,
        'current_status': status_filter,
        'query': query,
        'title': _('Ad Campaigns'),
    }
    return render(request, 'ads/campaign_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_campaign(request):
    """Create a new ad campaign."""
    if request.method == 'POST':
        form = AdCampaignForm(data=request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.created_by = request.user
            campaign.campaign_id = f'CAM-{timezone.now().strftime("%Y%m%d")}-{AdCampaign.objects.count() + 1:04d}'
            campaign.save()
            
            messages.success(request, _('Ad campaign created successfully.'))
            return redirect('ads:campaign_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = AdCampaignForm()
    
    context = {
        'form': form,
        'title': _('Create Ad Campaign'),
    }
    return render(request, 'ads/create_campaign.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_campaign(request, campaign_id):
    """Edit an ad campaign."""
    campaign = get_object_or_404(AdCampaign, pk=campaign_id, created_by=request.user)
    
    if request.method == 'POST':
        form = AdCampaignForm(data=request.POST, instance=campaign)
        if form.is_valid():
            campaign = form.save()
            messages.success(request, _('Ad campaign updated.'))
            return redirect('ads:campaign_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = AdCampaignForm(instance=campaign)
    
    context = {
        'campaign': campaign,
        'form': form,
        'title': _('Edit Ad Campaign'),
    }
    return render(request, 'ads/edit_campaign.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def delete_campaign(request, campaign_id):
    """Delete an ad campaign."""
    campaign = get_object_or_404(AdCampaign, pk=campaign_id, created_by=request.user)
    
    # Check if campaign has ads
    if Ad.objects.filter(campaign=campaign).exists():
        messages.error(request, _('Cannot delete a campaign with active ads.'))
        return redirect('ads:campaign_list')
    
    campaign.delete()
    messages.success(request, _('Ad campaign deleted.'))
    return redirect('ads:campaign_list')


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def update_campaign_status(request, campaign_id):
    """Update campaign status."""
    campaign = get_object_or_404(AdCampaign, pk=campaign_id, created_by=request.user)
    new_status = request.POST.get('status')
    
    if new_status not in dict(AdCampaign.STATUS_CHOICES):
        messages.error(request, _('Invalid status.'))
        return redirect('ads:campaign_list')
    
    campaign.status = new_status
    campaign.save()
    
    messages.success(request, _('Campaign status updated.'))
    return redirect('ads:campaign_list')


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def campaign_detail(request, campaign_id):
    """Campaign detail page."""
    campaign = get_object_or_404(AdCampaign, pk=campaign_id, created_by=request.user)
    
    # Get ads in this campaign
    ads = Ad.objects.filter(campaign=campaign)
    
    # Get statistics
    total_clicks = AdClick.objects.filter(ad__campaign=campaign).count()
    total_impressions = AdImpression.objects.filter(ad__campaign=campaign).count()
    total_conversions = AdConversion.objects.filter(ad__campaign=campaign).count()
    
    # Get budget usage
    budget_usage = ads.aggregate(
        total_spent=Sum('cost_per_click') * Count('id')
    )['total_spent'] or 0
    
    context = {
        'campaign': campaign,
        'ads': ads,
        'total_clicks': total_clicks,
        'total_impressions': total_impressions,
        'total_conversions': total_conversions,
        'budget_usage': budget_usage,
        'title': f"{_('Campaign')} {campaign.name}",
    }
    return render(request, 'ads/campaign_detail.html', context)


# ==================== AD GROUPS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def ad_group_list(request):
    """List all ad groups."""
    groups = AdGroup.objects.filter(
        created_by=request.user
    ).order_by('-created_at')
    
    # Search
    query = request.GET.get('q')
    if query:
        groups = groups.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(groups, 20)
    page = request.GET.get('page')
    
    try:
        groups_page = paginator.page(page)
    except PageNotAnInteger:
        groups_page = paginator.page(1)
    except EmptyPage:
        groups_page = paginator.page(paginator.num_pages)
    
    context = {
        'groups': groups_page,
        'query': query,
        'title': _('Ad Groups'),
    }
    return render(request, 'ads/ad_group_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_ad_group(request):
    """Create a new ad group."""
    if request.method == 'POST':
        form = AdGroupForm(data=request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            
            messages.success(request, _('Ad group created successfully.'))
            return redirect('ads:ad_group_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = AdGroupForm()
    
    context = {
        'form': form,
        'title': _('Create Ad Group'),
    }
    return render(request, 'ads/create_ad_group.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_ad_group(request, group_id):
    """Edit an ad group."""
    group = get_object_or_404(AdGroup, pk=group_id, created_by=request.user)
    
    if request.method == 'POST':
        form = AdGroupForm(data=request.POST, instance=group)
        if form.is_valid():
            group = form.save()
            messages.success(request, _('Ad group updated.'))
            return redirect('ads:ad_group_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = AdGroupForm(instance=group)
    
    context = {
        'group': group,
        'form': form,
        'title': _('Edit Ad Group'),
    }
    return render(request, 'ads/edit_ad_group.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def delete_ad_group(request, group_id):
    """Delete an ad group."""
    group = get_object_or_404(AdGroup, pk=group_id, created_by=request.user)
    
    # Check if group has campaigns
    if AdCampaign.objects.filter(ad_group=group).exists():
        messages.error(request, _('Cannot delete a group with active campaigns.'))
        return redirect('ads:ad_group_list')
    
    group.delete()
    messages.success(request, _('Ad group deleted.'))
    return redirect('ads:ad_group_list')


# ==================== ADS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def ad_list(request):
    """List all ads."""
    ads = Ad.objects.filter(
        campaign__created_by=request.user
    ).select_related('campaign', 'placement').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        ads = ads.filter(status=status_filter)
    
    # Filter by campaign
    campaign_id = request.GET.get('campaign')
    if campaign_id:
        ads = ads.filter(campaign__id=campaign_id)
    
    # Filter by placement
    placement_id = request.GET.get('placement')
    if placement_id:
        ads = ads.filter(placement__id=placement_id)
    
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
    
    campaigns = AdCampaign.objects.filter(created_by=request.user)
    placements = AdPlacement.objects.all()
    
    context = {
        'ads': ads_page,
        'campaigns': campaigns,
        'placements': placements,
        'current_status': status_filter,
        'current_campaign': campaign_id,
        'current_placement': placement_id,
        'query': query,
        'title': _('Ads'),
    }
    return render(request, 'ads/ad_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_ad(request):
    """Create a new ad."""
    campaigns = AdCampaign.objects.filter(created_by=request.user)
    placements = AdPlacement.objects.all()
    products = Product.objects.filter(is_active=True)[:100]
    categories = Category.objects.filter(is_active=True)[:100]
    
    if request.method == 'POST':
        form = AdForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.ad_id = f'AD-{timezone.now().strftime("%Y%m%d")}-{Ad.objects.count() + 1:04d}'
            ad.save()
            
            # Handle targeting
            targeting_data = request.POST.get('targeting')
            if targeting_data:
                try:
                    targeting_data = json.loads(targeting_data)
                    AdTargeting.objects.create(
                        ad=ad,
                        target_url=targeting_data.get('url'),
                        target_product_id=targeting_data.get('product_id'),
                        target_category_id=targeting_data.get('category_id'),
                        target_audience=targeting_data.get('audience'),
                    )
                except json.JSONDecodeError:
                    pass
            
            # Handle budget
            budget_data = request.POST.get('budget')
            if budget_data:
                try:
                    budget_data = json.loads(budget_data)
                    AdBudget.objects.create(
                        ad=ad,
                        daily_budget=budget_data.get('daily_budget'),
                        total_budget=budget_data.get('total_budget'),
                        bidding_strategy=budget_data.get('bidding_strategy'),
                    )
                except json.JSONDecodeError:
                    pass
            
            messages.success(request, _('Ad created successfully.'))
            return redirect('ads:ad_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = AdForm()
    
    context = {
        'form': form,
        'campaigns': campaigns,
        'placements': placements,
        'products': products,
        'categories': categories,
        'title': _('Create Ad'),
    }
    return render(request, 'ads/create_ad.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_ad(request, ad_id):
    """Edit an ad."""
    ad = get_object_or_404(Ad, pk=ad_id, campaign__created_by=request.user)
    
    campaigns = AdCampaign.objects.filter(created_by=request.user)
    placements = AdPlacement.objects.all()
    products = Product.objects.filter(is_active=True)[:100]
    categories = Category.objects.filter(is_active=True)[:100]
    
    if request.method == 'POST':
        form = AdForm(data=request.POST, files=request.FILES, instance=ad)
        if form.is_valid():
            ad = form.save()
            messages.success(request, _('Ad updated.'))
            return redirect('ads:ad_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = AdForm(instance=ad)
    
    context = {
        'ad': ad,
        'form': form,
        'campaigns': campaigns,
        'placements': placements,
        'products': products,
        'categories': categories,
        'title': _('Edit Ad'),
    }
    return render(request, 'ads/edit_ad.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def delete_ad(request, ad_id):
    """Delete an ad."""
    ad = get_object_or_404(Ad, pk=ad_id, campaign__created_by=request.user)
    ad.delete()
    messages.success(request, _('Ad deleted.'))
    return redirect('ads:ad_list')


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def update_ad_status(request, ad_id):
    """Update ad status."""
    ad = get_object_or_404(Ad, pk=ad_id, campaign__created_by=request.user)
    new_status = request.POST.get('status')
    
    if new_status not in dict(Ad.STATUS_CHOICES):
        messages.error(request, _('Invalid status.'))
        return redirect('ads:ad_list')
    
    ad.status = new_status
    ad.save()
    
    messages.success(request, _('Ad status updated.'))
    return redirect('ads:ad_list')


@require_http_methods(["GET"])
def ad_detail(request, ad_id):
    """Ad detail page (public)."""
    ad = get_object_or_404(Ad, pk=ad_id, status='active')
    
    # Record impression
    AdImpression.objects.create(
        ad=ad,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:200],
        referrer=request.META.get('HTTP_REFERER', ''),
    )
    
    # Update ad impression count
    ad.impressions += 1
    ad.save()
    
    context = {
        'ad': ad,
        'title': ad.title or ad.name,
        'meta_title': ad.meta_title or ad.title or ad.name,
        'meta_description': ad.meta_description or ad.description,
    }
    return render(request, 'ads/ad_detail.html', context)


# ==================== AD PLACEMENTS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def placement_list(request):
    """List all ad placements."""
    placements = AdPlacement.objects.all()
    
    # Search
    query = request.GET.get('q')
    if query:
        placements = placements.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(placement_id__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(placements, 20)
    page = request.GET.get('page')
    
    try:
        placements_page = paginator.page(page)
    except PageNotAnInteger:
        placements_page = paginator.page(1)
    except EmptyPage:
        placements_page = paginator.page(paginator.num_pages)
    
    context = {
        'placements': placements_page,
        'query': query,
        'title': _('Ad Placements'),
    }
    return render(request, 'ads/placement_list.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def create_placement(request):
    """Create a new ad placement."""
    if request.method == 'POST':
        form = AdPlacementForm(data=request.POST)
        if form.is_valid():
            placement = form.save(commit=False)
            placement.placement_id = f'PL-{AdPlacement.objects.count() + 1:04d}'
            placement.save()
            
            messages.success(request, _('Ad placement created successfully.'))
            return redirect('ads:placement_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = AdPlacementForm()
    
    context = {
        'form': form,
        'title': _('Create Ad Placement'),
    }
    return render(request, 'ads/create_placement.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET", "POST"])
def edit_placement(request, placement_id):
    """Edit an ad placement."""
    placement = get_object_or_404(AdPlacement, pk=placement_id)
    
    if request.method == 'POST':
        form = AdPlacementForm(data=request.POST, instance=placement)
        if form.is_valid():
            placement = form.save()
            messages.success(request, _('Ad placement updated.'))
            return redirect('ads:placement_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = AdPlacementForm(instance=placement)
    
    context = {
        'placement': placement,
        'form': form,
        'title': _('Edit Ad Placement'),
    }
    return render(request, 'ads/edit_placement.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["POST"])
def delete_placement(request, placement_id):
    """Delete an ad placement."""
    placement = get_object_or_404(AdPlacement, pk=placement_id)
    
    # Check if placement has ads
    if Ad.objects.filter(placement=placement).exists():
        messages.error(request, _('Cannot delete a placement with active ads.'))
        return redirect('ads:placement_list')
    
    placement.delete()
    messages.success(request, _('Ad placement deleted.'))
    return redirect('ads:placement_list')


# ==================== AD TRACKING ====================

@require_http_methods(["GET"])
def track_ad_click(request, ad_id):
    """Track ad click."""
    ad = get_object_or_404(Ad, pk=ad_id, status='active')
    
    # Record click
    AdClick.objects.create(
        ad=ad,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:200],
        referrer=request.META.get('HTTP_REFERER', ''),
        clicked_at=timezone.now(),
    )
    
    # Update ad click count
    ad.clicks += 1
    ad.save()
    
    # Redirect to target URL
    targeting = AdTargeting.objects.filter(ad=ad).first()
    if targeting and targeting.target_url:
        return redirect(targeting.target_url)
    
    return redirect('home')


@require_http_methods(["GET"])
def track_ad_impression(request, ad_id):
    """Track ad impression (for image/iframe ads)."""
    ad = get_object_or_404(Ad, pk=ad_id, status='active')
    
    # Record impression
    AdImpression.objects.create(
        ad=ad,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:200],
        referrer=request.META.get('HTTP_REFERER', ''),
    )
    
    # Update ad impression count
    ad.impressions += 1
    ad.save()
    
    # Return 1x1 transparent pixel
    response = HttpResponse(content_type='image/png')
    response.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82')
    return response


@require_http_methods(["GET"])
def track_ad_conversion(request, ad_id, order_id):
    """Track ad conversion (when order is placed)."""
    ad = get_object_or_404(Ad, pk=ad_id)
    order = get_object_or_404(Order, pk=order_id)
    
    # Check if this conversion already exists
    existing_conversion = AdConversion.objects.filter(
        ad=ad,
        order=order
    ).first()
    
    if not existing_conversion:
        AdConversion.objects.create(
            ad=ad,
            order=order,
            user=order.user,
            conversion_value=order.total_amount,
            converted_at=timezone.now(),
        )
        
        # Update ad conversion count
        ad.conversions += 1
        ad.save()
    
    # Return 1x1 transparent pixel
    response = HttpResponse(content_type='image/png')
    response.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82')
    return response


# ==================== AD REPORTS ====================

@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def ad_reports(request):
    """Ad performance reports."""
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Default to last 30 days
    if not start_date:
        start_date = (timezone.now() - timezone.timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = timezone.now().strftime('%Y-%m-%d')
    
    # Get ads
    ads = Ad.objects.filter(
        campaign__created_by=request.user
    )
    
    # Get statistics
    report_data = {}
    
    for ad in ads:
        clicks = AdClick.objects.filter(
            ad=ad,
            clicked_at__date__range=[start_date, end_date]
        ).count()
        
        impressions = AdImpression.objects.filter(
            ad=ad,
            created_at__date__range=[start_date, end_date]
        ).count()
        
        conversions = AdConversion.objects.filter(
            ad=ad,
            converted_at__date__range=[start_date, end_date]
        ).count()
        
        conversion_value = AdConversion.objects.filter(
            ad=ad,
            converted_at__date__range=[start_date, end_date]
        ).aggregate(total=Sum('conversion_value'))['total'] or 0
        
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
        
        report_data[str(ad.id)] = {
            'ad_id': ad.ad_id,
            'name': ad.name,
            'campaign': ad.campaign.name,
            'impressions': impressions,
            'clicks': clicks,
            'conversions': conversions,
            'conversion_value': conversion_value,
            'ctr': round(ctr, 2),
            'conversion_rate': round(conversion_rate, 2),
            'cost': ad.cost_per_click * clicks if ad.cost_per_click else 0,
        }
    
    # Sort by clicks
    sorted_data = sorted(report_data.values(), key=lambda x: x['clicks'], reverse=True)
    
    # Calculate totals
    total_impressions = sum(item['impressions'] for item in sorted_data)
    total_clicks = sum(item['clicks'] for item in sorted_data)
    total_conversions = sum(item['conversions'] for item in sorted_data)
    total_conversion_value = sum(item['conversion_value'] for item in sorted_data)
    total_cost = sum(item['cost'] for item in sorted_data)
    overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    overall_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
    
    context = {
        'report_data': sorted_data,
        'start_date': start_date,
        'end_date': end_date,
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'total_conversions': total_conversions,
        'total_conversion_value': total_conversion_value,
        'total_cost': total_cost,
        'overall_ctr': round(overall_ctr, 2),
        'overall_conversion_rate': round(overall_conversion_rate, 2),
        'title': _('Ad Performance Reports'),
    }
    return render(request, 'ads/ad_reports.html', context)


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def ad_dashboard(request):
    """Ad dashboard."""
    # Get counts
    total_ads = Ad.objects.filter(campaign__created_by=request.user).count()
    active_ads = Ad.objects.filter(campaign__created_by=request.user, status='active').count()
    total_campaigns = AdCampaign.objects.filter(created_by=request.user).count()
    active_campaigns = AdCampaign.objects.filter(created_by=request.user, status='active').count()
    
    # Get recent ads
    recent_ads = Ad.objects.filter(
        campaign__created_by=request.user
    ).order_by('-created_at')[:5]
    
    # Get top performing ads
    top_ads = Ad.objects.filter(
        campaign__created_by=request.user
    ).annotate(
        total_clicks=Count('adclick')
    ).order_by('-total_clicks')[:5]
    
    # Get recent campaigns
    recent_campaigns = AdCampaign.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:5]
    
    # Get statistics
    total_clicks = AdClick.objects.filter(ad__campaign__created_by=request.user).count()
    total_impressions = AdImpression.objects.filter(ad__campaign__created_by=request.user).count()
    total_conversions = AdConversion.objects.filter(ad__campaign__created_by=request.user).count()
    total_spent = Ad.objects.filter(
        campaign__created_by=request.user
    ).aggregate(total=Sum('cost_per_click'))['total'] or 0
    
    context = {
        'total_ads': total_ads,
        'active_ads': active_ads,
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'recent_ads': recent_ads,
        'top_ads': top_ads,
        'recent_campaigns': recent_campaigns,
        'total_clicks': total_clicks,
        'total_impressions': total_impressions,
        'total_conversions': total_conversions,
        'total_spent': total_spent,
        'title': _('Ad Dashboard'),
    }
    return render(request, 'ads/ad_dashboard.html', context)


# ==================== AJAX VIEWS ====================

@require_http_methods(["GET"])
def get_ad_statistics_ajax(request, ad_id):
    """Get ad statistics via AJAX."""
    ad = get_object_or_404(Ad, pk=ad_id)
    
    # Get statistics for different time periods
    today = timezone.now().date()
    
    # Today
    today_clicks = AdClick.objects.filter(
        ad=ad,
        clicked_at__date=today
    ).count()
    
    today_impressions = AdImpression.objects.filter(
        ad=ad,
        created_at__date=today
    ).count()
    
    # Last 7 days
    last_7_days_clicks = AdClick.objects.filter(
        ad=ad,
        clicked_at__date__gte=today - timezone.timedelta(days=7)
    ).count()
    
    last_7_days_impressions = AdImpression.objects.filter(
        ad=ad,
        created_at__date__gte=today - timezone.timedelta(days=7)
    ).count()
    
    # Last 30 days
    last_30_days_clicks = AdClick.objects.filter(
        ad=ad,
        clicked_at__date__gte=today - timezone.timedelta(days=30)
    ).count()
    
    last_30_days_impressions = AdImpression.objects.filter(
        ad=ad,
        created_at__date__gte=today - timezone.timedelta(days=30)
    ).count()
    
    # All time
    all_time_clicks = AdClick.objects.filter(ad=ad).count()
    all_time_impressions = AdImpression.objects.filter(ad=ad).count()
    all_time_conversions = AdConversion.objects.filter(ad=ad).count()
    
    return JsonResponse({
        'today': {
            'clicks': today_clicks,
            'impressions': today_impressions,
        },
        'last_7_days': {
            'clicks': last_7_days_clicks,
            'impressions': last_7_days_impressions,
        },
        'last_30_days': {
            'clicks': last_30_days_clicks,
            'impressions': last_30_days_impressions,
        },
        'all_time': {
            'clicks': all_time_clicks,
            'impressions': all_time_impressions,
            'conversions': all_time_conversions,
        },
    })


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def get_ad_list_ajax(request):
    """Get ad list via AJAX."""
    ads = Ad.objects.filter(
        campaign__created_by=request.user
    ).select_related('campaign', 'placement')
    
    ads_data = []
    for ad in ads:
        ads_data.append({
            'id': str(ad.id),
            'ad_id': ad.ad_id,
            'name': ad.name,
            'title': ad.title,
            'campaign': ad.campaign.name,
            'placement': ad.placement.name if ad.placement else None,
            'status': ad.status,
            'impressions': ad.impressions,
            'clicks': ad.clicks,
            'conversions': ad.conversions,
            'created_at': ad.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse({'ads': ads_data})


@login_required
@user_passes_test(is_staff)
@require_http_methods(["GET"])
def get_campaign_list_ajax(request):
    """Get campaign list via AJAX."""
    campaigns = AdCampaign.objects.filter(created_by=request.user)
    
    campaigns_data = []
    for campaign in campaigns:
        campaigns_data.append({
            'id': str(campaign.id),
            'campaign_id': campaign.campaign_id,
            'name': campaign.name,
            'description': campaign.description,
            'status': campaign.status,
            'budget': campaign.budget,
            'start_date': campaign.start_date.strftime('%Y-%m-%d') if campaign.start_date else None,
            'end_date': campaign.end_date.strftime('%Y-%m-%d') if campaign.end_date else None,
            'created_at': campaign.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    return JsonResponse({'campaigns': campaigns_data})


@require_http_methods(["GET"])
def get_ad_by_placement_ajax(request, placement_id):
    """Get ads for a specific placement via AJAX."""
    placement = get_object_or_404(AdPlacement, pk=placement_id)
    
    ads = Ad.objects.filter(
        placement=placement,
        status='active'
    ).order_by('-created_at')
    
    ads_data = []
    for ad in ads:
        # Check if user has already seen this ad
        seen = False
        if request.user.is_authenticated:
            seen = AdImpression.objects.filter(
                ad=ad,
                user=request.user
            ).exists()
        
        ads_data.append({
            'id': str(ad.id),
            'name': ad.name,
            'title': ad.title,
            'description': ad.description,
            'image': ad.image.url if ad.image else None,
            'url': ad.get_absolute_url(),
            'seen': seen,
        })
    
    return JsonResponse({'ads': ads_data})


@require_http_methods(["POST"])
@csrf_exempt
def record_ad_view_ajax(request):
    """Record ad view via AJAX."""
    ad_id = request.POST.get('ad_id')
    
    if not ad_id:
        return JsonResponse({'error': 'Ad ID is required'}, status=400)
    
    ad = get_object_or_404(Ad, pk=ad_id, status='active')
    
    # Record impression
    AdImpression.objects.create(
        ad=ad,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:200],
        referrer=request.META.get('HTTP_REFERER', ''),
    )
    
    # Update ad impression count
    ad.impressions += 1
    ad.save()
    
    return JsonResponse({'success': True})
