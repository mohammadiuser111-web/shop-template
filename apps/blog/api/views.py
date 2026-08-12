"""
API views for Blog app.
"""
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from ..models import BlogCategory, Tag, Article, ArticleImage, ArticleRelated, Comment, CommentRating
from .serializers import (
    BlogCategorySerializer, BlogCategoryListSerializer, BlogCategoryCreateSerializer,
    TagSerializer, TagListSerializer, TagCreateSerializer,
    ArticleSerializer, ArticleListSerializer, ArticleCreateSerializer, ArticleUpdateSerializer,
    ArticleImageSerializer, ArticleImageListSerializer, ArticleImageCreateSerializer,
    ArticleRelatedSerializer, ArticleRelatedCreateSerializer,
    CommentSerializer, CommentListSerializer, CommentCreateSerializer, CommentUpdateSerializer,
    CommentRatingSerializer, CommentRatingCreateSerializer,
    BlogStatisticsSerializer
)


# Blog Category Views
class BlogCategoryListAPIView(generics.ListAPIView):
    """List blog categories."""
    
    serializer_class = BlogCategoryListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get blog categories."""
        parent_id = self.kwargs.get('parent_id')
        
        if parent_id:
            parent = get_object_or_404(BlogCategory, pk=parent_id)
            return BlogCategory.objects.filter(parent=parent, is_active=True).order_by('sort_order', 'name')
        
        return BlogCategory.objects.filter(parent__isnull=True, is_active=True).order_by('sort_order', 'name')


class BlogCategoryRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve blog category."""
    
    serializer_class = BlogCategorySerializer
    permission_classes = [permissions.AllowAny]
    queryset = BlogCategory.objects.all()


class BlogCategoryCreateAPIView(generics.CreateAPIView):
    """Create blog category."""
    
    serializer_class = BlogCategoryCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class BlogCategoryUpdateAPIView(generics.UpdateAPIView):
    """Update blog category."""
    
    serializer_class = BlogCategoryCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = BlogCategory.objects.all()


class BlogCategoryDestroyAPIView(generics.DestroyAPIView):
    """Delete blog category."""
    
    serializer_class = BlogCategorySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = BlogCategory.objects.all()


# Tag Views
class TagListAPIView(generics.ListAPIView):
    """List tags."""
    
    serializer_class = TagListSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Tag.objects.all().order_by('name')


class TagRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve tag."""
    
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Tag.objects.all()


class TagCreateAPIView(generics.CreateAPIView):
    """Create tag."""
    
    serializer_class = TagCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class TagUpdateAPIView(generics.UpdateAPIView):
    """Update tag."""
    
    serializer_class = TagCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Tag.objects.all()


class TagDestroyAPIView(generics.DestroyAPIView):
    """Delete tag."""
    
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Tag.objects.all()


# Article Views
class ArticleListAPIView(generics.ListAPIView):
    """List articles."""
    
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get articles."""
        category_id = self.kwargs.get('category_id')
        tag_id = self.kwargs.get('tag_id')
        is_featured = self.request.query_params.get('featured')
        is_popular = self.request.query_params.get('popular')
        
        queryset = Article.objects.filter(status='published')
        
        if category_id:
            category = get_object_or_404(BlogCategory, pk=category_id)
            queryset = queryset.filter(categories=category)
        
        if tag_id:
            tag = get_object_or_404(Tag, pk=tag_id)
            queryset = queryset.filter(tags=tag)
        
        if is_featured:
            queryset = queryset.filter(is_featured=True)
        
        if is_popular:
            queryset = queryset.filter(is_popular=True)
        
        return queryset.select_related('author').prefetch_related('categories', 'tags').order_by('-published_at')


class ArticleRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve article."""
    
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_object(self):
        """Get article and increment view count."""
        article = super().get_object()
        article.increment_view_count()
        return article
    
    def get_queryset(self):
        """Get articles."""
        return Article.objects.all()


class ArticleCreateAPIView(generics.CreateAPIView):
    """Create article."""
    
    serializer_class = ArticleCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        """Set author and published date."""
        serializer.save(
            author=self.request.user,
            published_at=timezone.now() if serializer.validated_data.get('status') == 'published' else None
        )


class ArticleUpdateAPIView(generics.UpdateAPIView):
    """Update article."""
    
    serializer_class = ArticleUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Article.objects.all()
    
    def perform_update(self, serializer):
        """Update published date if status changed to published."""
        if serializer.validated_data.get('status') == 'published' and not serializer.instance.published_at:
            serializer.save(published_at=timezone.now())
        else:
            serializer.save()


class ArticleDestroyAPIView(generics.DestroyAPIView):
    """Delete article."""
    
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Article.objects.all()


class ArticleSearchAPIView(views.APIView):
    """Search articles."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Search articles."""
        query = request.query_params.get('q', '')
        category_id = request.query_params.get('category_id')
        tag_id = request.query_params.get('tag_id')
        
        from django.db.models import Q
        
        queryset = Article.objects.filter(status='published')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(excerpt__icontains=query) | 
                Q(content__icontains=query) |
                Q(meta_keywords__icontains=query)
            )
        
        if category_id:
            category = get_object_or_404(BlogCategory, pk=category_id)
            queryset = queryset.filter(categories=category)
        
        if tag_id:
            tag = get_object_or_404(Tag, pk=tag_id)
            queryset = queryset.filter(tags=tag)
        
        queryset = queryset.select_related('author').prefetch_related('categories', 'tags').order_by('-published_at')
        
        serializer = ArticleListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Article Image Views
class ArticleImageListAPIView(generics.ListAPIView):
    """List article images."""
    
    serializer_class = ArticleImageListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get article images."""
        article_id = self.kwargs.get('article_id')
        article = get_object_or_404(Article, pk=article_id)
        return ArticleImage.objects.filter(article=article).order_by('sort_order')


class ArticleImageRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve article image."""
    
    serializer_class = ArticleImageSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ArticleImage.objects.all()


class ArticleImageCreateAPIView(generics.CreateAPIView):
    """Create article image."""
    
    serializer_class = ArticleImageCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        """Set article."""
        article_id = self.kwargs.get('article_id')
        article = get_object_or_404(Article, pk=article_id)
        serializer.save(article=article)


class ArticleImageUpdateAPIView(generics.UpdateAPIView):
    """Update article image."""
    
    serializer_class = ArticleImageCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ArticleImage.objects.all()


class ArticleImageDestroyAPIView(generics.DestroyAPIView):
    """Delete article image."""
    
    serializer_class = ArticleImageSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ArticleImage.objects.all()


# Article Related Views
class ArticleRelatedListAPIView(generics.ListAPIView):
    """List related articles."""
    
    serializer_class = ArticleRelatedSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get related articles."""
        article_id = self.kwargs.get('article_id')
        article = get_object_or_404(Article, pk=article_id)
        return ArticleRelated.objects.filter(from_article=article).order_by('sort_order')


class ArticleRelatedCreateAPIView(generics.CreateAPIView):
    """Create article relationship."""
    
    serializer_class = ArticleRelatedCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def perform_create(self, serializer):
        """Set from_article."""
        article_id = self.kwargs.get('article_id')
        from_article = get_object_or_404(Article, pk=article_id)
        serializer.save(from_article=from_article)


class ArticleRelatedDestroyAPIView(generics.DestroyAPIView):
    """Delete article relationship."""
    
    serializer_class = ArticleRelatedSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ArticleRelated.objects.all()


# Comment Views
class CommentListAPIView(generics.ListAPIView):
    """List comments."""
    
    serializer_class = CommentListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get comments."""
        article_id = self.kwargs.get('article_id')
        
        if article_id:
            article = get_object_or_404(Article, pk=article_id)
            return Comment.objects.filter(article=article, parent__isnull=True, is_approved=True).order_by('-created_at')
        
        return Comment.objects.filter(is_approved=True).order_by('-created_at')


class CommentRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve comment."""
    
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Comment.objects.all()


class CommentCreateAPIView(generics.CreateAPIView):
    """Create comment."""
    
    serializer_class = CommentCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        """Set user and IP address."""
        article = serializer.validated_data.get('article')
        
        # Check if article allows comments
        if article and not article.allow_comments:
            raise serializers.ValidationError('Comments are not allowed for this article')
        
        # Set user if authenticated
        if self.request.user.is_authenticated:
            serializer.save(
                user=self.request.user,
                author_name=self.request.user.get_full_name() or self.request.user.phone_number or self.request.user.email,
                author_email=self.request.user.email or '',
                author_ip=self.get_client_ip(self.request)
            )
        else:
            serializer.save(
                author_ip=self.get_client_ip(self.request)
            )
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CommentUpdateAPIView(generics.UpdateAPIView):
    """Update comment."""
    
    serializer_class = CommentUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Comment.objects.all()


class CommentDestroyAPIView(generics.DestroyAPIView):
    """Delete comment."""
    
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Comment.objects.all()


class CommentApproveAPIView(views.APIView):
    """Approve a comment."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, pk):
        """Approve comment."""
        comment = get_object_or_404(Comment, pk=pk)
        comment.approve()
        
        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentRepliesAPIView(generics.ListAPIView):
    """List comment replies."""
    
    serializer_class = CommentListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get comment replies."""
        comment_id = self.kwargs.get('comment_id')
        comment = get_object_or_404(Comment, pk=comment_id)
        return Comment.objects.filter(parent=comment, is_approved=True).order_by('created_at')


# Comment Rating Views
class CommentRatingCreateAPIView(generics.CreateAPIView):
    """Create comment rating."""
    
    serializer_class = CommentRatingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class CommentRatingDestroyAPIView(generics.DestroyAPIView):
    """Delete comment rating."""
    
    serializer_class = CommentRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CommentRating.objects.all()


# Blog Statistics View
class BlogStatisticsAPIView(views.APIView):
    """Get blog statistics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Return blog statistics."""
        from django.db.models import Count, Sum
        
        # Total articles
        total_articles = Article.objects.count()
        
        # Total categories
        total_categories = BlogCategory.objects.count()
        
        # Total tags
        total_tags = Tag.objects.count()
        
        # Total comments
        total_comments = Comment.objects.count()
        
        # Published articles
        published_articles = Article.objects.filter(status='published').count()
        
        # Draft articles
        draft_articles = Article.objects.filter(status='draft').count()
        
        # Total views
        total_views = Article.objects.aggregate(total=Sum('view_count'))['total'] or 0
        
        # Most popular articles
        popular_articles = Article.objects.filter(status='published').order_by('-view_count')[:5]
        most_popular = []
        for article in popular_articles:
            most_popular.append({
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'view_count': article.view_count
            })
        
        data = {
            'total_articles': total_articles,
            'total_categories': total_categories,
            'total_tags': total_tags,
            'total_comments': total_comments,
            'published_articles': published_articles,
            'draft_articles': draft_articles,
            'total_views': total_views,
            'most_popular_articles': most_popular
        }
        
        serializer = BlogStatisticsSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_200_OK)


# Recent Articles View
class RecentArticlesAPIView(views.APIView):
    """Get recent articles."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return recent articles."""
        limit = int(request.query_params.get('limit', 5))
        
        articles = Article.objects.filter(status='published').order_by('-published_at')[:limit]
        serializer = ArticleListSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Featured Articles View
class FeaturedArticlesAPIView(views.APIView):
    """Get featured articles."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return featured articles."""
        limit = int(request.query_params.get('limit', 5))
        
        articles = Article.objects.filter(status='published', is_featured=True).order_by('-published_at')[:limit]
        serializer = ArticleListSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Popular Articles View
class PopularArticlesAPIView(views.APIView):
    """Get popular articles."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Return popular articles."""
        limit = int(request.query_params.get('limit', 5))
        
        articles = Article.objects.filter(status='published', is_popular=True).order_by('-view_count')[:limit]
        serializer = ArticleListSerializer(articles, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
