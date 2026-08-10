"""
Blog API Views
ViewSets and APIViews for blog models
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.blog.models import BlogCategory, BlogTag, BlogPost, BlogComment
from api.serializers.blog_serializers import (
    BlogCategorySerializer,
    BlogCategoryListSerializer,
    BlogTagSerializer,
    BlogCommentSerializer,
    BlogCommentListSerializer,
    BlogCommentCreateSerializer,
    BlogPostSerializer,
    BlogPostListSerializer,
    BlogPostCreateSerializer,
    BlogPostUpdateSerializer,
    BlogStatsSerializer,
)
from api.pagination import CustomPageNumberPagination


class BlogCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for BlogCategory model"""
    
    serializer_class = BlogCategorySerializer
    queryset = BlogCategory.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['parent', 'is_active', 'is_featured']
    search_fields = ['name', 'description', 'slug']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BlogCategoryListSerializer
        return BlogCategorySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        category = self.get_object()
        posts = BlogPost.objects.filter(
            category=category,
            is_published=True
        ).order_by('-published_at')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = BlogPostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class BlogTagViewSet(viewsets.ModelViewSet):
    """ViewSet for BlogTag model"""
    
    serializer_class = BlogTagSerializer
    queryset = BlogTag.objects.filter(is_active=True).order_by('name')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        tag = self.get_object()
        posts = BlogPost.objects.filter(
            tags=tag,
            is_published=True
        ).order_by('-published_at')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = BlogPostListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class BlogPostViewSet(viewsets.ModelViewSet):
    """ViewSet for BlogPost model"""
    
    serializer_class = BlogPostSerializer
    queryset = BlogPost.objects.filter(is_published=True).order_by('-published_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'tags', 'author', 'is_published', 'is_featured']
    search_fields = ['title', 'content', 'excerpt', 'meta_title', 'meta_keywords']
    ordering_fields = ['title', 'published_at', 'created_at', 'view_count']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BlogPostListSerializer
        elif self.action == 'create':
            return BlogPostCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return BlogPostUpdateSerializer
        return BlogPostSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category slug
        category_slug = self.request.query_params.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by tag slug
        tag_slug = self.request.query_params.get('tag_slug')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        return queryset.distinct()
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        post = self.get_object()
        post.view_count += 1
        post.save()
        return Response({'status': 'success', 'view_count': post.view_count})
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        post = self.get_object()
        comments = BlogComment.objects.filter(post=post, is_approved=True, parent__isnull=True).order_by('-created_at')
        
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = BlogCommentListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = BlogCommentListSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)


class BlogCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for BlogComment model"""
    
    serializer_class = BlogCommentSerializer
    queryset = BlogComment.objects.filter(is_approved=True).order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['post', 'user', 'is_approved']
    search_fields = ['comment', 'user__email', 'user__first_name', 'user__last_name']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BlogCommentListSerializer
        elif self.action == 'create':
            return BlogCommentCreateSerializer
        return BlogCommentSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return BlogComment.objects.all().order_by('-created_at')
        return self.queryset
    
    def perform_create(self, serializer):
        post_id = self.request.data.get('post_id')
        try:
            post = BlogPost.objects.get(id=post_id)
            serializer.save(post=post, user=self.request.user)
        except BlogPost.DoesNotExist:
            raise serializers.ValidationError('Post not found')


class BlogStatsAPIView(APIView):
    """APIView for blog statistics"""
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        from django.db.models import Count, Sum
        
        stats = {
            'total_posts': BlogPost.objects.count(),
            'published_posts': BlogPost.objects.filter(is_published=True).count(),
            'total_categories': BlogCategory.objects.count(),
            'total_tags': BlogTag.objects.count(),
            'total_comments': BlogComment.objects.filter(is_approved=True).count(),
            'total_views': sum(p.view_count for p in BlogPost.objects.all()) or 0,
            'most_popular_posts': [],
            'recent_posts': [],
            'posts_by_category': {},
            'posts_by_month': {}
        }
        
        # Most popular posts
        popular_posts = BlogPost.objects.filter(is_published=True).order_by('-view_count')[:10]
        for post in popular_posts:
            stats['most_popular_posts'].append({
                'id': post.id,
                'title': post.title,
                'slug': post.slug,
                'view_count': post.view_count
            })
        
        # Recent posts
        recent_posts = BlogPost.objects.filter(is_published=True).order_by('-published_at')[:10]
        for post in recent_posts:
            stats['recent_posts'].append({
                'id': post.id,
                'title': post.title,
                'slug': post.slug,
                'published_at': post.published_at
            })
        
        # Posts by category
        category_stats = BlogPost.objects.filter(is_published=True).values('category__name').annotate(
            count=Count('id')
        )
        for stat in category_stats:
            stats['posts_by_category'][stat['category__name']] = stat['count']
        
        # Posts by month
        from django.db.models.functions import TruncMonth
        from django.db.models import DateField
        month_stats = BlogPost.objects.filter(is_published=True).annotate(
            month=TruncMonth('published_at')
        ).values('month').annotate(count=Count('id')).order_by('month')
        
        for stat in month_stats:
            stats['posts_by_month'][str(stat['month'])] = stat['count']
        
        serializer = BlogStatsSerializer(stats)
        return Response(serializer.data)
