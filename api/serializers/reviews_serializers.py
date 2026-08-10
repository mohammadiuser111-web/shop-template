"""
Reviews Serializers
Serializers for reviews models: Review, ReviewImage, ReviewHelpfulness
"""

from rest_framework import serializers
from apps.reviews.models import Review, ReviewImage, ReviewHelpfulness
from .products_serializers import ProductListSerializer
from .accounts_serializers import UserPublicSerializer


class ReviewImageSerializer(serializers.ModelSerializer):
    """Serializer for ReviewImage model"""
    
    image_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ReviewImage
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'review')
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None


class ReviewHelpfulnessSerializer(serializers.ModelSerializer):
    """Serializer for ReviewHelpfulness model"""
    
    user = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = ReviewHelpfulness
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'review', 'user')


class ReviewSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for Review model"""
    
    user = UserPublicSerializer(read_only=True)
    product = ProductListSerializer(read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    helpful_votes = serializers.SerializerMethodField(read_only=True)
    is_helpful = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user', 'product', 'is_approved', 'is_rejected', 'helpful_votes', 'is_helpful')
    
    def get_helpful_votes(self, obj):
        return ReviewHelpfulness.objects.filter(review=obj, is_helpful=True).count()
    
    def get_is_helpful(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ReviewHelpfulness.objects.filter(
                review=obj, user=request.user, is_helpful=True
            ).exists()
        return False


class ReviewListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for review lists"""
    
    user = UserPublicSerializer(read_only=True)
    product = serializers.StringField(source='product.name', read_only=True)
    rating = serializers.IntegerField()
    helpful_votes = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'comment', 'helpful_votes', 'is_approved', 'created_at']
        read_only_fields = fields
    
    def get_helpful_votes(self, obj):
        return ReviewHelpfulness.objects.filter(review=obj, is_helpful=True).count()


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews"""
    
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Review
        fields = ['product', 'rating', 'comment', 'images', 'is_anonymous']
    
    def create(self, validated_data):
        images = validated_data.pop('images', [])
        review = Review.objects.create(**validated_data)
        
        for image in images:
            ReviewImage.objects.create(review=review, image=image)
        
        return review


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating reviews"""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'is_anonymous']


class ReviewHelpfulnessCreateSerializer(serializers.Serializer):
    """Serializer for creating review helpfulness votes"""
    
    review_id = serializers.IntegerField(required=True)
    is_helpful = serializers.BooleanField(required=True)


class ReviewModerationSerializer(serializers.Serializer):
    """Serializer for moderating reviews"""
    
    review_id = serializers.IntegerField(required=True)
    action = serializers.ChoiceField(choices=['approve', 'reject', 'spam'], required=True)
    reason = serializers.CharField(required=False, allow_blank=True)


class ReviewStatsSerializer(serializers.Serializer):
    """Serializer for review statistics"""
    
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    rating_distribution = serializers.DictField()
    featured_reviews = serializers.ListField(child=serializers.DictField())
    recent_reviews = serializers.ListField(child=serializers.DictField())
