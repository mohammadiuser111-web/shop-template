"""
Core views for shop-template project.
"""
from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_http_methods


def custom_404(request, exception, template_name='errors/404.html'):
    """Custom 404 error page."""
    return render(request, template_name, status=404)


def custom_500(request, template_name='errors/500.html'):
    """Custom 500 error page."""
    return render(request, template_name, status=500)


def custom_403(request, exception, template_name='errors/403.html'):
    """Custom 403 error page."""
    return render(request, template_name, status=403)


def maintenance(request):
    """Maintenance mode page."""
    from apps.core.models import SiteSettings
    
    site_settings = SiteSettings.get_instance()
    
    context = {
        'message': site_settings.maintenance_message if site_settings else 'در حال حاضر سایت در حال بروزرسانی است.',
    }
    
    return render(request, 'errors/maintenance.html', context, status=503)


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint."""
    return JsonResponse({
        'status': 'ok',
        'timestamp': request.timestamp if hasattr(request, 'timestamp') else None,
    })


@require_http_methods(["GET"])
def ping(request):
    """Ping endpoint."""
    return JsonResponse({'pong': True})
