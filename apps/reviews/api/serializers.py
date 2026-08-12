"""
API serializers for Reviews app.
"""
from rest_framework import serializers
from ..models import Review, ReviewImage, ReviewVideo, ReviewComment, ReviewHelpfulness


# Review Serializers
class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review."""
    
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    variant = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    order = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    order_item = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    author_name = serializers.SerializerMethodField()
    rating_display = serializers.SerializerMethodField()
    helpfulness_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['id', 'product', 'variant', 'user', 'order', 'order_item',
                           'author_name', 'is_approved', 'is_verified_purchase', 'is_recommended',
                           'helpful_count', 'not_helpful_count', 'created_at', 'updated_at', 'approved_at']
    
    def get_author_name(self, obj):
        return obj.get_author_name()
    
    def get_rating_display(self, obj):
        return obj.get_rating_display()
    
    def get_helpfulness_percentage(self, obj):
        return obj.get_helpfulness_percentage()


class ReviewListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for review list."""
    
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    variant = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    author_name = serializers.SerializerMethodField()
    rating_display = serializers.SerializerMethodField()
    helpfulness_percentage = serializers.SerializerMethodField()
    images_count = serializers.SerializerMethodField()
    videos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'variant', 'user', 'author_name', 'title', 'content',
                 'rating', 'rating_display', 'is_approved', 'is_verified_purchase', 'is_recommended',
                 'helpful_count', 'not_helpful_count', 'helpfulness_percentage',
                 'created_at', 'images_count', 'videos_count']
        read_only_fields = ['id', 'product', 'variant', 'user', 'author_name', 'rating_display',
                           'is_approved', 'is_verified_purchase', 'is_recommended',
                           'helpful_count', 'not_helpful_count', 'helpfulness_percentage',
                           'created_at', 'images_count', 'videos_count']
    
    def get_author_name(self, obj):
        return obj.get_author_name()
    
    def get_rating_display(self, obj):
        return obj.get_rating_display()
    
    def get_helpfulness_percentage(self, obj):
        return obj.get_helpfulness_percentage()
    
    def get_images_count(self, obj):
        return obj.images.count()
    
    def get_videos_count(self, obj):
        return obj.videos.count()


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating review."""
    
    class Meta:
        model = Review
        fields = ['product', 'variant', 'order', 'order_item', 'rating', 'title', 
                 'content', 'pros', 'cons', 'author_name', 'author_email', 'is_recommended']


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating review."""
    
    class Meta:
        model = Review
        fields = ['title', 'content', 'pros', 'cons', 'is_approved', 'is_verified_purchase', 'is_recommended']


# Review Image Serializers
class ReviewImageSerializer(serializers.ModelSerializer):
    """Serializer for ReviewImage."""
    
    class Meta:
        model = ReviewImage
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ReviewImageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for review image list."""
    
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'caption', 'sort_order']
        read_only_fields = ['id']


# Review Video Serializers
class ReviewVideoSerializer(serializers.ModelSerializer):
    """Serializer for ReviewVideo."""
    
    class Meta:
        model = ReviewVideo
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ReviewVideoListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for review video list."""
    
    class Meta:
        model = ReviewVideo
        fields = ['id', 'video', 'thumbnail', 'caption', 'sort_order']
        read_only_fields = ['id']


# Review Comment Serializers
class ReviewCommentSerializer(serializers.ModelSerializer):
    """Serializer for ReviewComment."""
    
    review = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    
    class Meta:
        model = ReviewComment
        fields = '__all__'
        read_only_fields = ['id', 'review', 'user', 'created_at', 'updated_at']


class ReviewCommentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for review comment list."""
    
    review = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    
    class Meta:
        model = ReviewComment
        fields = ['id', 'review', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'review', 'user', 'created_at']


class ReviewCommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating review comment."""
    
    class Meta:
        model = ReviewComment
        fields = ['review', 'content']


# Review Helpfulness Serializers
class ReviewHelpfulnessSerializer(serializers.ModelSerializer):
    """Serializer for ReviewHelpfulness."""
    
    review = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    
    class Meta:
        model = ReviewHelpfulness
        fields = '__all__'
        read_only_fields = ['id', 'review', 'user', 'created_at']


class ReviewHelpfulnessCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating review helpfulness vote."""
    
    class Meta:
        model = ReviewHelpfulness
        fields = ['review', 'is_helpful']


# Review Statistics Serializer
class ReviewStatisticsSerializer(serializers.Serializer):
    """Serializer for review statistics."""
    
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    rating_distribution = serializers.DictField()
    verified_reviews = serializers.IntegerField()
    recommended_reviews = serializers.IntegerField()
    reviews_with_media = serializers.IntegerField()
