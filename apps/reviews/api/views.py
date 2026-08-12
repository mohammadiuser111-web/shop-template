"""
API views for Reviews app.
"""
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from ..models import Review, ReviewImage, ReviewVideo, ReviewComment, ReviewHelpfulness
from apps.products.models import Product, ProductVariant
from apps.orders.models import Order, OrderItem
from .serializers import (
    ReviewSerializer, ReviewListSerializer, ReviewCreateSerializer, ReviewUpdateSerializer,
    ReviewImageSerializer, ReviewImageListSerializer,
    ReviewVideoSerializer, ReviewVideoListSerializer,
    ReviewCommentSerializer, ReviewCommentListSerializer, ReviewCommentCreateSerializer,
    ReviewHelpfulnessSerializer, ReviewHelpfulnessCreateSerializer,
    ReviewStatisticsSerializer
)


# Review Views
class ReviewListAPIView(generics.ListAPIView):
    """List reviews."""
    
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get reviews."""
        product_id = self.kwargs.get('product_id')
        rating = self.request.query_params.get('rating')
        is_verified = self.request.query_params.get('verified')
        is_recommended = self.request.query_params.get('recommended')
        
        queryset = Review.objects.filter(is_approved=True)
        
        if product_id:
            product = get_object_or_404(Product, pk=product_id)
            queryset = queryset.filter(product=product)
        
        if rating:
            queryset = queryset.filter(rating=int(rating))
        
        if is_verified:
            queryset = queryset.filter(is_verified_purchase=True)
        
        if is_recommended:
            queryset = queryset.filter(is_recommended=True)
        
        return queryset.select_related('product', 'variant', 'user').order_by('-created_at')


class ReviewRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve review."""
    
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Review.objects.all()


class ReviewCreateAPIView(generics.CreateAPIView):
    """Create review."""
    
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        """Set user information."""
        user = self.request.user if self.request.user.is_authenticated else None
        
        # Check if user has purchased the product (for verified reviews)
        product = serializer.validated_data.get('product')
        order = serializer.validated_data.get('order')
        
        if user and product and order:
            # Check if order contains the product
            order_items = OrderItem.objects.filter(order=order, product=product)
            if order_items.exists():
                serializer.save(
                    user=user,
                    author_name=user.get_full_name() or user.phone_number or user.email,
                    author_email=user.email or '',
                    is_verified_purchase=True
                )
            else:
                serializer.save(
                    user=user,
                    author_name=user.get_full_name() or user.phone_number or user.email,
                    author_email=user.email or ''
                )
        elif user:
            serializer.save(
                user=user,
                author_name=user.get_full_name() or user.phone_number or user.email,
                author_email=user.email or ''
            )
        else:
            serializer.save()


class ReviewUpdateAPIView(generics.UpdateAPIView):
    """Update review."""
    
    serializer_class = ReviewUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Review.objects.all()


class ReviewDestroyAPIView(generics.DestroyAPIView):
    """Delete review."""
    
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Review.objects.all()


class ReviewApproveAPIView(views.APIView):
    """Approve a review."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, pk):
        """Approve review."""
        review = get_object_or_404(Review, pk=pk)
        review.approve()
        
        serializer = ReviewSerializer(review, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewVerifyAPIView(views.APIView):
    """Mark review as verified purchase."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, pk):
        """Mark review as verified."""
        review = get_object_or_404(Review, pk=pk)
        review.mark_as_verified()
        
        serializer = ReviewSerializer(review, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewHelpfulAPIView(views.APIView):
    """Mark review as helpful."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Mark review as helpful."""
        review = get_object_or_404(Review, pk=pk)
        user = request.user
        
        # Check if user has already voted
        existing_vote = ReviewHelpfulness.objects.filter(review=review, user=user).first()
        
        if existing_vote:
            return Response({'detail': 'You have already voted on this review'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create vote
        ReviewHelpfulness.objects.create(
            review=review,
            user=user,
            is_helpful=True
        )
        
        # Update review counts
        review.helpful_count += 1
        review.save()
        
        return Response({
            'detail': 'Thank you for your feedback',
            'helpful_count': review.helpful_count,
            'not_helpful_count': review.not_helpful_count
        }, status=status.HTTP_201_CREATED)


class ReviewNotHelpfulAPIView(views.APIView):
    """Mark review as not helpful."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Mark review as not helpful."""
        review = get_object_or_404(Review, pk=pk)
        user = request.user
        
        # Check if user has already voted
        existing_vote = ReviewHelpfulness.objects.filter(review=review, user=user).first()
        
        if existing_vote:
            return Response({'detail': 'You have already voted on this review'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create vote
        ReviewHelpfulness.objects.create(
            review=review,
            user=user,
            is_helpful=False
        )
        
        # Update review counts
        review.not_helpful_count += 1
        review.save()
        
        return Response({
            'detail': 'Thank you for your feedback',
            'helpful_count': review.helpful_count,
            'not_helpful_count': review.not_helpful_count
        }, status=status.HTTP_201_CREATED)


# Review Image Views
class ReviewImageListAPIView(generics.ListAPIView):
    """List review images."""
    
    serializer_class = ReviewImageListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get review images."""
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        return review.images.all().order_by('sort_order')


class ReviewImageRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve review image."""
    
    serializer_class = ReviewImageSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ReviewImage.objects.all()


class ReviewImageCreateAPIView(generics.CreateAPIView):
    """Create review image."""
    
    serializer_class = ReviewImageSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReviewImageUpdateAPIView(generics.UpdateAPIView):
    """Update review image."""
    
    serializer_class = ReviewImageSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ReviewImage.objects.all()


class ReviewImageDestroyAPIView(generics.DestroyAPIView):
    """Delete review image."""
    
    serializer_class = ReviewImageSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ReviewImage.objects.all()


# Review Video Views
class ReviewVideoListAPIView(generics.ListAPIView):
    """List review videos."""
    
    serializer_class = ReviewVideoListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get review videos."""
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        return review.videos.all().order_by('sort_order')


class ReviewVideoRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve review video."""
    
    serializer_class = ReviewVideoSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ReviewVideo.objects.all()


class ReviewVideoCreateAPIView(generics.CreateAPIView):
    """Create review video."""
    
    serializer_class = ReviewVideoSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReviewVideoUpdateAPIView(generics.UpdateAPIView):
    """Update review video."""
    
    serializer_class = ReviewVideoSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ReviewVideo.objects.all()


class ReviewVideoDestroyAPIView(generics.DestroyAPIView):
    """Delete review video."""
    
    serializer_class = ReviewVideoSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ReviewVideo.objects.all()


# Review Comment Views
class ReviewCommentListAPIView(generics.ListAPIView):
    """List review comments."""
    
    serializer_class = ReviewCommentListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get review comments."""
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        return ReviewComment.objects.filter(review=review).order_by('created_at')


class ReviewCommentRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve review comment."""
    
    serializer_class = ReviewCommentSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ReviewComment.objects.all()


class ReviewCommentCreateAPIView(generics.CreateAPIView):
    """Create review comment."""
    
    serializer_class = ReviewCommentCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        """Set user."""
        serializer.save(user=self.request.user)


class ReviewCommentDestroyAPIView(generics.DestroyAPIView):
    """Delete review comment."""
    
    serializer_class = ReviewCommentSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ReviewComment.objects.all()


# Review Helpfulness Views
class ReviewHelpfulnessListAPIView(generics.ListAPIView):
    """List review helpfulness votes."""
    
    serializer_class = ReviewHelpfulnessSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Get review helpfulness votes."""
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        return ReviewHelpfulness.objects.filter(review=review)


class ReviewHelpfulnessCreateAPIView(generics.CreateAPIView):
    """Create review helpfulness vote."""
    
    serializer_class = ReviewHelpfulnessCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReviewHelpfulnessDestroyAPIView(generics.DestroyAPIView):
    """Delete review helpfulness vote."""
    
    serializer_class = ReviewHelpfulnessSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ReviewHelpfulness.objects.all()


# Review Statistics View
class ReviewStatisticsAPIView(views.APIView):
    """Get review statistics."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return review statistics."""
        product_id = self.kwargs.get('product_id')
        
        if product_id:
            product = get_object_or_404(Product, pk=product_id)
            reviews = Review.objects.filter(product=product, is_approved=True)
        else:
            reviews = Review.objects.filter(is_approved=True)
        
        # Total reviews
        total_reviews = reviews.count()
        
        # Average rating
        if total_reviews > 0:
            total_rating = sum(review.rating for review in reviews)
            average_rating = total_rating / total_reviews
        else:
            average_rating = 0
        
        # Rating distribution
        rating_distribution = {}
        for i in range(1, 6):
            count = reviews.filter(rating=i).count()
            rating_distribution[str(i)] = {
                'count': count,
                'percentage': (count / total_reviews * 100) if total_reviews > 0 else 0
            }
        
        # Verified reviews
        verified_reviews = reviews.filter(is_verified_purchase=True).count()
        
        # Recommended reviews
        recommended_reviews = reviews.filter(is_recommended=True).count()
        
        # Reviews with media
        reviews_with_media = reviews.filter(models.Q(images__isnull=False) | models.Q(videos__isnull=False)).distinct().count()
        
        data = {
            'total_reviews': total_reviews,
            'average_rating': round(average_rating, 2),
            'rating_distribution': rating_distribution,
            'verified_reviews': verified_reviews,
            'recommended_reviews': recommended_reviews,
            'reviews_with_media': reviews_with_media
        }
        
        serializer = ReviewStatisticsSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_200_OK)


# Product Reviews View
class ProductReviewsAPIView(views.APIView):
    """Get reviews for a product."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, product_id):
        """Return reviews for a product."""
        product = get_object_or_404(Product, pk=product_id)
        
        # Get reviews
        reviews = Review.objects.filter(product=product, is_approved=True).select_related(
            'user', 'variant', 'order'
        ).order_by('-created_at')
        
        # Get statistics
        total_reviews = reviews.count()
        if total_reviews > 0:
            total_rating = sum(review.rating for review in reviews)
            average_rating = total_rating / total_reviews
        else:
            average_rating = 0
        
        # Rating distribution
        rating_distribution = {}
        for i in range(1, 6):
            count = reviews.filter(rating=i).count()
            rating_distribution[str(i)] = count
        
        data = {
            'product_id': product.id,
            'product_name': product.name,
            'total_reviews': total_reviews,
            'average_rating': round(average_rating, 2),
            'rating_distribution': rating_distribution,
            'reviews': ReviewListSerializer(reviews, many=True, context={'request': request}).data
        }
        
        return Response(data, status=status.HTTP_200_OK)


# Recent Reviews View
class RecentReviewsAPIView(views.APIView):
    """Get recent reviews."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return recent reviews."""
        limit = int(request.query_params.get('limit', 5))
        
        reviews = Review.objects.filter(is_approved=True).select_related(
            'product', 'user', 'variant'
        ).order_by('-created_at')[:limit]
        
        serializer = ReviewListSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
