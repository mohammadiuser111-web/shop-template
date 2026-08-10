"""
Ads API Views
ViewSets and APIViews for ads models
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.ads.models import AdSpace, AdBanner, AdImpression, AdClick
from api.serializers.ads_serializers import (
    AdSpaceSerializer,
    AdSpaceListSerializer,
    AdBannerSerializer,
    AdBannerListSerializer,
    AdBannerCreateSerializer,
    AdBannerUpdateSerializer,
    AdImpressionSerializer,
    AdClickSerializer,
    AdImpressionCreateSerializer,
    AdClickCreateSerializer,
    AdStatsSerializer,
)
from api.pagination import CustomPageNumberPagination


class AdSpaceViewSet(viewsets.ModelViewSet):
    """ViewSet for AdSpace model"""
    
    serializer_class = AdSpaceSerializer
    queryset = AdSpace.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AdSpaceListSerializer
        return AdSpaceSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def banners(self, request, pk=None):
        ad_space = self.get_object()
        banners = AdBanner.objects.filter(
            ad_space=ad_space,
            is_active=True,
            starts_at__lte=self.request.date_today,
            ends_at__gte=self.request.date_today
        ).order_by('-priority', '-created_at')
        
        serializer = AdBannerListSerializer(banners, many=True, context={'request': request})
        return Response(serializer.data)


class AdBannerViewSet(viewsets.ModelViewSet):
    """ViewSet for AdBanner model"""
    
    serializer_class = AdBannerSerializer
    queryset = AdBanner.objects.all().order_by('-priority', '-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ad_space', 'is_active', 'status']
    search_fields = ['title', 'url']
    ordering_fields = ['title', 'priority', 'created_at', 'starts_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AdBannerListSerializer
        elif self.action == 'create':
            return AdBannerCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return AdBannerUpdateSerializer
        return AdBannerSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        banner = self.get_object()
        banner.is_active = True
        banner.save()
        return Response({'status': 'success', 'id': banner.id})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        banner = self.get_object()
        banner.is_active = False
        banner.save()
        return Response({'status': 'success', 'id': banner.id})
    
    @action(detail=True, methods=['get'])
    def impressions(self, request, pk=None):
        banner = self.get_object()
        impressions = AdImpression.objects.filter(banner=banner).order_by('-created_at')
        serializer = AdImpressionSerializer(impressions, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def clicks(self, request, pk=None):
        banner = self.get_object()
        clicks = AdClick.objects.filter(banner=banner).order_by('-created_at')
        serializer = AdClickSerializer(clicks, many=True, context={'request': request})
        return Response(serializer.data)


class AdImpressionViewSet(viewsets.ModelViewSet):
    """ViewSet for AdImpression model"""
    
    serializer_class = AdImpressionSerializer
    queryset = AdImpression.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['banner', 'session_key']
    ordering_fields = ['created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_permissions(self):
        return [IsAdminUser()]


class AdClickViewSet(viewsets.ModelViewSet):
    """ViewSet for AdClick model"""
    
    serializer_class = AdClickSerializer
    queryset = AdClick.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['banner', 'user', 'session_key']
    ordering_fields = ['created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_permissions(self):
        return [IsAdminUser()]


class AdImpressionCreateAPIView(APIView):
    """APIView for recording ad impressions"""
    
    permission_classes = [AllowAny]
    serializer_class = AdImpressionCreateSerializer
    
    def post(self, request):
        serializer = AdImpressionCreateSerializer(data=request.data)
        if serializer.is_valid():
            banner_id = serializer.validated_data['banner_id']
            user_id = serializer.validated_data.get('user_id')
            session_key = serializer.validated_data.get('session_key')
            referrer = serializer.validated_data.get('referrer', '')
            user_agent = serializer.validated_data.get('user_agent', '')
            ip_address = serializer.validated_data.get('ip_address', '')
            
            try:
                banner = AdBanner.objects.get(id=banner_id)
            except AdBanner.DoesNotExist:
                return Response({'error': 'Banner not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Create impression
            AdImpression.objects.create(
                banner=banner,
                user_id=user_id,
                session_key=session_key,
                referrer=referrer,
                user_agent=user_agent,
                ip_address=ip_address
            )
            
            # Update banner impression count
            banner.impressions += 1
            banner.save()
            
            return Response({'status': 'success'})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AdClickCreateAPIView(APIView):
    """APIView for recording ad clicks"""
    
    permission_classes = [AllowAny]
    serializer_class = AdClickCreateSerializer
    
    def post(self, request):
        serializer = AdClickCreateSerializer(data=request.data)
        if serializer.is_valid():
            banner_id = serializer.validated_data['banner_id']
            user_id = serializer.validated_data.get('user_id')
            session_key = serializer.validated_data.get('session_key')
            referrer = serializer.validated_data.get('referrer', '')
            user_agent = serializer.validated_data.get('user_agent', '')
            ip_address = serializer.validated_data.get('ip_address', '')
            
            try:
                banner = AdBanner.objects.get(id=banner_id)
            except AdBanner.DoesNotExist:
                return Response({'error': 'Banner not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Create click
            AdClick.objects.create(
                banner=banner,
                user_id=user_id,
                session_key=session_key,
                referrer=referrer,
                user_agent=user_agent,
                ip_address=ip_address
            )
            
            # Update banner click count
            banner.clicks += 1
            banner.save()
            
            return Response({'status': 'success'})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AdStatsAPIView(APIView):
    """APIView for ad statistics"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db.models import Count, Sum
        from datetime import timedelta
        
        stats = {
            'total_spaces': AdSpace.objects.count(),
            'total_banners': AdBanner.objects.count(),
            'active_banners': AdBanner.objects.filter(is_active=True).count(),
            'total_impressions': AdImpression.objects.count(),
            'total_clicks': AdClick.objects.count(),
            'overall_ctr': 0,
            'impressions_by_space': {},
            'clicks_by_space': {},
            'ctr_by_space': {},
            'impressions_by_date': {},
            'clicks_by_date': {},
            'top_banners': []
        }
        
        # Calculate overall CTR
        total_impressions = AdImpression.objects.count()
        total_clicks = AdClick.objects.count()
        if total_impressions > 0:
            stats['overall_ctr'] = (total_clicks / total_impressions) * 100
        
        # Stats by space
        for space in AdSpace.objects.filter(is_active=True):
            space_banners = AdBanner.objects.filter(ad_space=space)
            space_impressions = AdImpression.objects.filter(banner__in=space_banners).count()
            space_clicks = AdClick.objects.filter(banner__in=space_banners).count()
            
            stats['impressions_by_space'][space.name] = space_impressions
            stats['clicks_by_space'][space.name] = space_clicks
            stats['ctr_by_space'][space.name] = (space_clicks / space_impressions * 100) if space_impressions > 0 else 0
        
        # Stats by date (last 30 days)
        thirty_days_ago = self.request.date_today - timedelta(days=30)
        
        daily_impressions = AdImpression.objects.filter(created_at__gte=thirty_days_ago).values('created_at__date').annotate(
            count=Count('id')
        )
        for day in daily_impressions:
            stats['impressions_by_date'][str(day['created_at__date'])] = day['count']
        
        daily_clicks = AdClick.objects.filter(created_at__gte=thirty_days_ago).values('created_at__date').annotate(
            count=Count('id')
        )
        for day in daily_clicks:
            stats['clicks_by_date'][str(day['created_at__date'])] = day['count']
        
        # Top banners
        top_banners = AdBanner.objects.annotate(
            impression_count=Count('adimpression'),
            click_count=Count('adclick')
        ).order_by('-click_count')[:10]
        
        for banner in top_banners:
            stats['top_banners'].append({
                'id': banner.id,
                'title': banner.title,
                'impressions': banner.impressions,
                'clicks': banner.clicks,
                'ctr': (banner.clicks / banner.impressions * 100) if banner.impressions > 0 else 0
            })
        
        serializer = AdStatsSerializer(stats)
        return Response(serializer.data)
