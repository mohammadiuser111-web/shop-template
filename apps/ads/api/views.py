"""
API views for ads app.
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from ..models import AdSlot, Advertisement, AdImpression, AdClick
from .serializers import (
    AdSlotSerializer, AdvertisementSerializer,
    AdImpressionSerializer, AdClickSerializer,
    AdvertisementStatsSerializer, AdSlotStatsSerializer,
    AdsOverallStatsSerializer, AdDisplaySerializer,
    ReportDataSerializer, PerformanceReportSerializer
)
from ..services import AdService, AdReportService


# AdSlot Views
class AdSlotListCreateAPIView(generics.ListCreateAPIView):
    """List and create ad slots."""
    
    queryset = AdSlot.objects.filter(is_active=True).order_by('name')
    serializer_class = AdSlotSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=(is_active.lower() == 'true'))
        
        # Search
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(
                models.Q(name__icontains=query) | 
                models.Q(code__icontains=query) | 
                models.Q(description__icontains=query)
            )
        
        return queryset


class AdSlotRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an ad slot."""
    
    queryset = AdSlot.objects.all()
    serializer_class = AdSlotSerializer
    permission_classes = [permissions.IsAdminUser]


# Advertisement Views
class AdvertisementListCreateAPIView(generics.ListCreateAPIView):
    """List and create advertisements."""
    
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = Advertisement.objects.select_related('slot', 'created_by').order_by('-priority', '-created_at')
        
        # Filter by slot
        slot_id = self.request.query_params.get('slot_id')
        if slot_id:
            queryset = queryset.filter(slot__id=slot_id)
        
        # Filter by slot code
        slot_code = self.request.query_params.get('slot_code')
        if slot_code:
            queryset = queryset.filter(slot__code=slot_code)
        
        # Filter by ad type
        ad_type = self.request.query_params.get('ad_type')
        if ad_type:
            queryset = queryset.filter(ad_type=ad_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=(is_active.lower() == 'true'))
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Search
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(
                models.Q(name__icontains=query) | 
                models.Q(title__icontains=query) | 
                models.Q(description__icontains=query)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)


class AdvertisementRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an advertisement."""
    
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAdminUser]


# Ad Display Views
class AdDisplayAPIView(APIView):
    """Get ad for display in a slot."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, slot_code):
        """Get ad for a slot."""
        ad = AdService.get_current_ad(slot_code, request)
        
        if not ad:
            return Response({'error': 'No ad found for this slot'}, status=status.HTTP_404_NOT_FOUND)
        
        # Track impression
        AdService.track_impression(ad, request)
        
        # Serialize ad data
        serializer = AdDisplaySerializer(ad)
        return Response(serializer.data)


class AdDisplayResponsiveAPIView(APIView):
    """Get responsive ad for display in a slot."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, slot_code, width, height):
        """Get responsive ad for a slot with specific dimensions."""
        ad = AdService.get_current_ad(slot_code, request)
        
        if not ad:
            return Response({'error': 'No ad found for this slot'}, status=status.HTTP_404_NOT_FOUND)
        
        # Track impression
        AdService.track_impression(ad, request)
        
        # Serialize ad data
        serializer = AdDisplaySerializer(ad)
        data = serializer.data
        data['width'] = width
        data['height'] = height
        return Response(data)


# Tracking Views
class AdImpressionCreateAPIView(APIView):
    """Create ad impression tracking record."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, ad_id):
        """Track ad impression."""
        ad = get_object_or_404(Advertisement, pk=ad_id)
        
        # Track impression
        impression = AdService.track_impression(ad, request)
        
        if impression:
            serializer = AdImpressionSerializer(impression)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response({'error': 'Impression already tracked'}, status=status.HTTP_200_OK)


class AdClickCreateAPIView(APIView):
    """Create ad click tracking record."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, ad_id):
        """Track ad click."""
        ad = get_object_or_404(Advertisement, pk=ad_id)
        
        # Track click
        click = AdService.track_click(ad, request)
        
        if click:
            serializer = AdClickSerializer(click)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response({'error': 'Click tracking failed'}, status=status.HTTP_400_BAD_REQUEST)


# Statistics Views
class AdvertisementStatsAPIView(APIView):
    """Get advertisement statistics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, ad_id):
        """Get stats for an advertisement."""
        stats = AdService.get_ad_stats(ad_id)
        
        if not stats:
            return Response({'error': 'Ad not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Prepare response data
        data = {
            'id': stats['ad'].id,
            'name': stats['ad'].name,
            'title': stats['ad'].title,
            'ad_type': stats['ad'].ad_type,
            'impression_count': stats['impressions'],
            'click_count': stats['clicks'],
            'ctr': stats['ctr'],
            'conversion_rate': stats.get('conversion_rate', 0)
        }
        
        serializer = AdvertisementStatsSerializer(data)
        return Response(serializer.data)


class AdSlotStatsAPIView(APIView):
    """Get ad slot statistics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, slot_code):
        """Get stats for an ad slot."""
        stats = AdService.get_slot_stats(slot_code)
        
        if not stats:
            return Response({'error': 'Slot not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Prepare response data
        data = {
            'id': stats['slot'].id,
            'name': stats['slot'].name,
            'code': stats['slot'].code,
            'total_impressions': stats['total_impressions'],
            'total_clicks': stats['total_clicks'],
            'total_ads': stats['total_ads'],
            'active_ads': stats['active_ads'],
            'average_ctr': stats['average_ctr']
        }
        
        serializer = AdSlotStatsSerializer(data)
        return Response(serializer.data)


class AdsOverallStatsAPIView(APIView):
    """Get overall ads statistics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Get overall ads statistics."""
        stats = AdService.get_all_stats()
        
        # Prepare top ads data
        top_ads_data = []
        for ad in stats.get('top_ads', []):
            top_ads_data.append({
                'id': ad.id,
                'name': ad.name,
                'title': ad.title,
                'ad_type': ad.ad_type,
                'impression_count': ad.impression_count,
                'click_count': ad.click_count,
                'ctr': ad.get_ctr()
            })
        
        # Prepare response data
        data = {
            'total_ads': stats['total_ads'],
            'active_ads': stats['active_ads'],
            'total_impressions': stats['total_impressions'],
            'total_clicks': stats['total_clicks'],
            'overall_ctr': stats['overall_ctr'],
            'top_ads': top_ads_data
        }
        
        serializer = AdsOverallStatsSerializer(data)
        return Response(serializer.data)


# Report Views
class ImpressionReportAPIView(APIView):
    """Get impression report data."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Get impression report."""
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        slot_code = request.query_params.get('slot_code')
        
        report = AdReportService.get_impression_report(date_from, date_to, slot_code)
        
        serializer = ReportDataSerializer(report, many=True)
        return Response(serializer.data)


class ClickReportAPIView(APIView):
    """Get click report data."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Get click report."""
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        slot_code = request.query_params.get('slot_code')
        
        report = AdReportService.get_click_report(date_from, date_to, slot_code)
        
        serializer = ReportDataSerializer(report, many=True)
        return Response(serializer.data)


class PerformanceReportAPIView(APIView):
    """Get performance report data."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Get performance report."""
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        report = AdReportService.get_performance_report(date_from, date_to)
        
        # Format report data
        formatted_report = []
        for item in report:
            formatted_report.append({
                'ad_id': item['id'],
                'name': item['name'],
                'slot_name': item['slot__name'],
                'total_impressions': item['total_impressions'],
                'total_clicks': item['total_clicks'],
                'ctr': item['ctr']
            })
        
        serializer = PerformanceReportSerializer(formatted_report, many=True)
        return Response(serializer.data)
