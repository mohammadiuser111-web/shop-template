"""
Reviews API Views
ViewSets and APIViews for review models
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.reviews.models import Review, ReviewImage, ReviewHelpfulness
from api.serializers.reviews_serializers import (
    ReviewImageSerializer,
    ReviewHelpfulnessSerializer,
    ReviewSerializer,
    ReviewListSerializer,
    ReviewCreateSerializer,
    ReviewUpdateSerializer,
    ReviewHelpfulnessCreateSerializer,
    ReviewModerationSerializer,
    ReviewStatsSerializer,
)
from api.pagination import CustomPageNumberPagination


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Review model"""
    
    serializer_class = ReviewSerializer
    queryset = Review.objects.filter(is_approved=True).order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'user', 'rating', 'is_approved']
    search_fields = ['comment', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'updated_at', 'rating']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReviewListSerializer
        elif self.action == 'create':
            return ReviewCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ReviewUpdateSerializer
        return ReviewSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create', 'update', 'partial_update']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        return queryset
    
    def perform_create(self, serializer):
        product_id = self.request.data.get('product_id')
        rating = self.request.data.get('rating')
        comment = self.request.data.get('comment', '')
        images = self.request.FILES.getlist('images')
        is_anonymous = self.request.data.get('is_anonymous', False)
        
        # Check if user already reviewed this product
        if Review.objects.filter(user=self.request.user, product_id=product_id).exists():
            raise serializers.ValidationError('You have already reviewed this product')
        
        review = serializer.save(
            user=self.request.user,
            product_id=product_id,
            rating=rating,
            comment=comment,
            is_anonymous=is_anonymous
        )
        
        # Create review images
        for image in images:
            ReviewImage.objects.create(review=review, image=image)
        
        return review
    
    @action(detail=True, methods=['post'])
    def helpful(self, request, pk=None):
        review = self.get_object()
        serializer = ReviewHelpfulnessCreateSerializer(data={
            'review_id': review.id,
            'is_helpful': True
        })
        if serializer.is_valid():
            # Check if user already voted
            if ReviewHelpfulness.objects.filter(review=review, user=request.user).exists():
                return Response({'error': 'You have already voted on this review'}, status=status.HTTP_400_BAD_REQUEST)
            
            ReviewHelpfulness.objects.create(
                review=review,
                user=request.user,
                is_helpful=True
            )
            
            return Response({'status': 'success', 'helpful': True})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def unhelpful(self, request, pk=None):
        review = self.get_object()
        
        # Check if user already voted
        if ReviewHelpfulness.objects.filter(review=review, user=request.user).exists():
            return Response({'error': 'You have already voted on this review'}, status=status.HTTP_400_BAD_REQUEST)
        
        ReviewHelpfulness.objects.create(
            review=review,
            user=request.user,
            is_helpful=False
        )
        
        return Response({'status': 'success', 'helpful': False})


class ReviewImageViewSet(viewsets.ModelViewSet):
    """ViewSet for ReviewImage model"""
    
    serializer_class = ReviewImageSerializer
    queryset = ReviewImage.objects.all()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class ReviewHelpfulnessViewSet(viewsets.ModelViewSet):
    """ViewSet for ReviewHelpfulness model"""
    
    serializer_class = ReviewHelpfulnessSerializer
    queryset = ReviewHelpfulness.objects.all()
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)


class ReviewCreateAPIView(APIView):
    """APIView for creating reviews"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewCreateSerializer
    
    def post(self, request):
        serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            
            # Check if user already reviewed this product
            if Review.objects.filter(user=request.user, product_id=product_id).exists():
                return Response({'error': 'You have already reviewed this product'}, status=status.HTTP_400_BAD_REQUEST)
            
            review = serializer.save(user=request.user)
            
            # Handle images
            images = request.FILES.getlist('images')
            for image in images:
                ReviewImage.objects.create(review=review, image=image)
            
            serializer = ReviewSerializer(review, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ReviewUpdateAPIView(APIView):
    """APIView for updating reviews"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewUpdateSerializer
    
    def post(self, request, pk):
        try:
            review = Review.objects.get(pk=pk, user=request.user)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ReviewUpdateSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ReviewModerationAPIView(APIView):
    """APIView for moderating reviews"""
    
    permission_classes = [IsAdminUser]
    serializer_class = ReviewModerationSerializer
    
    def post(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ReviewModerationSerializer(data=request.data)
        if serializer.is_valid():
            action = serializer.validated_data['action']
            reason = serializer.validated_data.get('reason', '')
            
            if action == 'approve':
                review.is_approved = True
                review.is_rejected = False
            elif action == 'reject':
                review.is_approved = False
                review.is_rejected = True
            elif action == 'spam':
                review.is_approved = False
                review.is_rejected = True
                review.is_spam = True
            
            review.save()
            
            return Response({'status': 'success', 'action': action, 'review_id': review.id})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ReviewStatsAPIView(APIView):
    """APIView for review statistics"""
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        from django.db.models import Count, Avg
        from apps.products.models import Product
        
        stats = {
            'total_reviews': Review.objects.filter(is_approved=True).count(),
            'average_rating': Review.objects.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0,
            'rating_distribution': {},
            'featured_reviews': [],
            'recent_reviews': [],
        }
        
        # Rating distribution
        for rating in range(1, 6):
            count = Review.objects.filter(is_approved=True, rating=rating).count()
            stats['rating_distribution'][str(rating)] = count
        
        # Featured reviews
        featured_reviews = Review.objects.filter(is_approved=True, is_featured=True).order_by('-created_at')[:5]
        for review in featured_reviews:
            stats['featured_reviews'].append({
                'id': review.id,
                'user': review.user.get_full_name() if review.user else 'Anonymous',
                'product': review.product.name,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at
            })
        
        # Recent reviews
        recent_reviews = Review.objects.filter(is_approved=True).order_by('-created_at')[:10]
        for review in recent_reviews:
            stats['recent_reviews'].append({
                'id': review.id,
                'user': review.user.get_full_name() if review.user else 'Anonymous',
                'product': review.product.name,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at
            })
        
        serializer = ReviewStatsSerializer(stats)
        return Response(serializer.data)
