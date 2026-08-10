"""
Blog Serializers
Serializers for blog models: BlogCategory, BlogTag, BlogPost, BlogComment
"""

from rest_framework import serializers
from apps.blog.models import BlogCategory, BlogTag, BlogPost, BlogComment
from .accounts_serializers import UserPublicSerializer


class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for BlogCategory model"""
    
    parent = serializers.StringField(source='parent.name', read_only=True, allow_null=True)
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    post_count = serializers.SerializerMethodField(read_only=True)
    children = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = BlogCategory
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug', 'parent', 'image_url', 'post_count', 'children')
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None
    
    def get_post_count(self, obj):
        return BlogPost.objects.filter(category=obj, is_published=True).count()
    
    def get_children(self, obj):
        children = BlogCategory.objects.filter(parent=obj, is_active=True)
        return BlogCategoryListSerializer(children, many=True, context=self.context).data


class BlogCategoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for blog category lists"""
    
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    post_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug', 'parent_name', 'image_url', 'post_count', 'position', 'is_active', 'is_featured']
        read_only_fields = fields
    
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None
    
    def get_post_count(self, obj):
        return BlogPost.objects.filter(category=obj, is_published=True).count()


class BlogTagSerializer(serializers.ModelSerializer):
    """Serializer for BlogTag model"""
    
    class Meta:
        model = BlogTag
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug')


class BlogCommentSerializer(serializers.ModelSerializer):
    """Serializer for BlogComment model"""
    
    user = UserPublicSerializer(read_only=True)
    post = serializers.StringField(source='post.title', read_only=True)
    
    class Meta:
        model = BlogComment
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user', 'post', 'is_approved')


class BlogCommentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for blog comment lists"""
    
    user = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = BlogComment
        fields = ['id', 'user', 'comment', 'is_approved', 'created_at']
        read_only_fields = fields


class BlogCommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating blog comments"""
    
    class Meta:
        model = BlogComment
        fields = ['comment', 'parent']


class BlogPostSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for BlogPost model"""
    
    author = UserPublicSerializer(read_only=True)
    category = BlogCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=True)
    tags = BlogTagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    comments = serializers.SerializerMethodField(read_only=True)
    comment_count = serializers.SerializerMethodField(read_only=True)
    featured_image_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = BlogPost
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug', 'post_id', 'author', 'category', 'tags', 'comments', 'comment_count', 'featured_image_url')
    
    def get_comments(self, obj):
        comments = BlogComment.objects.filter(post=obj, is_approved=True, parent__isnull=True).order_by('-created_at')[:10]
        return BlogCommentListSerializer(comments, many=True, context=self.context).data
    
    def get_comment_count(self, obj):
        return BlogComment.objects.filter(post=obj, is_approved=True).count()
    
    def get_featured_image_url(self, obj):
        if obj.featured_image:
            return self.context['request'].build_absolute_uri(obj.featured_image.url)
        return None


class BlogPostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for blog post lists"""
    
    author = UserPublicSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    tag_names = serializers.SerializerMethodField(read_only=True)
    featured_image_url = serializers.SerializerMethodField(read_only=True)
    comment_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = BlogPost
        fields = ['id', 'post_id', 'title', 'slug', 'author', 'category_name', 'category_slug', 'tag_names', 'excerpt', 'featured_image_url', 'comment_count', 'view_count', 'is_published', 'is_featured', 'published_at', 'created_at']
        read_only_fields = fields
    
    def get_tag_names(self, obj):
        return [tag.name for tag in obj.tags.all()]
    
    def get_featured_image_url(self, obj):
        if obj.featured_image:
            return self.context['request'].build_absolute_uri(obj.featured_image.url)
        return None
    
    def get_comment_count(self, obj):
        return BlogComment.objects.filter(post=obj, is_approved=True).count()


class BlogPostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating blog posts"""
    
    category_id = serializers.IntegerField(required=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'excerpt', 'category_id', 'tag_ids', 'featured_image', 'is_published', 'is_featured', 'meta_title', 'meta_description', 'meta_keywords']


class BlogPostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating blog posts"""
    
    category_id = serializers.IntegerField(required=False)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'excerpt', 'category_id', 'tag_ids', 'featured_image', 'is_published', 'is_featured', 'meta_title', 'meta_description', 'meta_keywords']


class BlogStatsSerializer(serializers.Serializer):
    """Serializer for blog statistics"""
    
    total_posts = serializers.IntegerField()
    published_posts = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_tags = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    total_views = serializers.IntegerField()
    most_popular_posts = serializers.ListField(child=serializers.DictField())
    recent_posts = serializers.ListField(child=serializers.DictField())
    posts_by_category = serializers.DictField()
    posts_by_month = serializers.DictField()
