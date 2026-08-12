"""
API serializers for Blog app.
"""
from rest_framework import serializers
from ..models import BlogCategory, Tag, Article, ArticleImage, ArticleRelated, Comment, CommentRating


# Blog Category Serializers
class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for BlogCategory."""
    
    parent = serializers.PrimaryKeyRelatedField(allow_null=True, read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogCategory
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        if obj.children.exists():
            return BlogCategoryListSerializer(obj.children.all(), many=True, context=self.context).data
        return []


class BlogCategoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for blog category list."""
    
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug', 'description', 'parent', 'image', 'icon', 'is_active', 'sort_order']
        read_only_fields = ['id', 'slug']


class BlogCategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating blog category."""
    
    class Meta:
        model = BlogCategory
        fields = ['name', 'description', 'parent', 'image', 'icon', 'meta_title', 'meta_description', 'is_active', 'sort_order']


# Tag Serializers
class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag."""
    
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class TagListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for tag list."""
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'description', 'color']
        read_only_fields = ['id', 'slug']


class TagCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tag."""
    
    class Meta:
        model = Tag
        fields = ['name', 'description', 'color']


# Article Serializers
class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article."""
    
    author = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    categories = BlogCategoryListSerializer(many=True, read_only=True)
    tags = TagListSerializer(many=True, read_only=True)
    author_name = serializers.SerializerMethodField()
    category_names = serializers.SerializerMethodField()
    tag_names = serializers.SerializerMethodField()
    is_published = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'author', 'categories', 'tags', 'view_count', 
                           'published_at', 'created_at', 'updated_at']
    
    def get_author_name(self, obj):
        return obj.get_author_name()
    
    def get_category_names(self, obj):
        return obj.get_category_names()
    
    def get_tag_names(self, obj):
        return obj.get_tag_names()
    
    def get_is_published(self, obj):
        return obj.is_published()


class ArticleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for article list."""
    
    author = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    categories = BlogCategoryListSerializer(many=True, read_only=True)
    tags = TagListSerializer(many=True, read_only=True)
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'excerpt', 'featured_image', 'author', 'author_name',
                 'categories', 'tags', 'status', 'is_featured', 'is_popular', 'published_at',
                 'view_count', 'allow_comments']
        read_only_fields = ['id', 'slug', 'author', 'view_count', 'published_at']
    
    def get_author_name(self, obj):
        return obj.get_author_name()


class ArticleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating article."""
    
    class Meta:
        model = Article
        fields = ['title', 'excerpt', 'content', 'categories', 'tags', 'featured_image',
                 'featured_image_caption', 'status', 'is_featured', 'is_popular', 
                 'allow_comments', 'published_at', 'scheduled_at', 'meta_title',
                 'meta_description', 'meta_keywords', 'canonical_url']


class ArticleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating article."""
    
    class Meta:
        model = Article
        fields = ['title', 'excerpt', 'content', 'categories', 'tags', 'featured_image',
                 'featured_image_caption', 'status', 'is_featured', 'is_popular',
                 'allow_comments', 'published_at', 'scheduled_at', 'meta_title',
                 'meta_description', 'meta_keywords', 'canonical_url']


# Article Image Serializers
class ArticleImageSerializer(serializers.ModelSerializer):
    """Serializer for ArticleImage."""
    
    article = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = ArticleImage
        fields = '__all__'
        read_only_fields = ['id', 'article', 'created_at', 'updated_at']


class ArticleImageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for article image list."""
    
    class Meta:
        model = ArticleImage
        fields = ['id', 'image', 'caption', 'alt_text', 'sort_order']
        read_only_fields = ['id']


class ArticleImageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating article image."""
    
    class Meta:
        model = ArticleImage
        fields = ['image', 'caption', 'alt_text', 'sort_order']


# Article Related Serializers
class ArticleRelatedSerializer(serializers.ModelSerializer):
    """Serializer for ArticleRelated."""
    
    from_article = serializers.PrimaryKeyRelatedField(read_only=True)
    to_article = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = ArticleRelated
        fields = '__all__'
        read_only_fields = ['id', 'from_article', 'to_article', 'created_at']


class ArticleRelatedCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating article relationship."""
    
    class Meta:
        model = ArticleRelated
        fields = ['to_article', 'sort_order']


# Comment Serializers
class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment."""
    
    article = serializers.PrimaryKeyRelatedField(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    author_name = serializers.SerializerMethodField()
    has_replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['id', 'article', 'parent', 'user', 'author_name', 'author_email',
                           'author_website', 'author_ip', 'is_approved', 'is_spam', 
                           'created_at', 'updated_at', 'approved_at']
    
    def get_author_name(self, obj):
        return obj.get_author_name()
    
    def get_has_replies(self, obj):
        return obj.has_replies()


class CommentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for comment list."""
    
    article = serializers.PrimaryKeyRelatedField(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    author_name = serializers.SerializerMethodField()
    has_replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'article', 'parent', 'user', 'author_name', 'author_email',
                 'content', 'is_approved', 'is_spam', 'created_at', 'has_replies', 'replies_count']
        read_only_fields = ['id', 'article', 'parent', 'user', 'author_name', 'author_email',
                           'is_approved', 'is_spam', 'created_at', 'has_replies', 'replies_count']
    
    def get_author_name(self, obj):
        return obj.get_author_name()
    
    def get_has_replies(self, obj):
        return obj.has_replies()
    
    def get_replies_count(self, obj):
        return obj.replies.count()


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comment."""
    
    class Meta:
        model = Comment
        fields = ['article', 'parent', 'content', 'author_name', 'author_email', 'author_website']


class CommentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating comment."""
    
    class Meta:
        model = Comment
        fields = ['content', 'is_approved', 'is_spam']


# Comment Rating Serializers
class CommentRatingSerializer(serializers.ModelSerializer):
    """Serializer for CommentRating."""
    
    comment = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    
    class Meta:
        model = CommentRating
        fields = '__all__'
        read_only_fields = ['id', 'comment', 'user', 'created_at']


class CommentRatingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comment rating."""
    
    class Meta:
        model = CommentRating
        fields = ['comment', 'rating']


# Blog Statistics Serializer
class BlogStatisticsSerializer(serializers.Serializer):
    """Serializer for blog statistics."""
    
    total_articles = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_tags = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    published_articles = serializers.IntegerField()
    draft_articles = serializers.IntegerField()
    total_views = serializers.IntegerField()
    most_popular_articles = serializers.ListField(child=serializers.DictField())
