"""
Support API Views
ViewSets and APIViews for support models
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.support.models import Ticket, TicketMessage, TicketCategory, FAQ, FAQCategory
from api.serializers.support_serializers import (
    TicketCategorySerializer,
    FAQCategorySerializer,
    FAQSerializer,
    FAQListSerializer,
    TicketMessageSerializer,
    TicketMessageCreateSerializer,
    TicketSerializer,
    TicketListSerializer,
    TicketCreateSerializer,
    TicketUpdateSerializer,
    TicketStatusUpdateSerializer,
    SupportStatsSerializer,
)
from api.pagination import CustomPageNumberPagination


class TicketCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for TicketCategory model"""
    
    serializer_class = TicketCategorySerializer
    queryset = TicketCategory.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class FAQCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for FAQCategory model"""
    
    serializer_class = FAQCategorySerializer
    queryset = FAQCategory.objects.filter(is_active=True).order_by('position')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'position', 'created_at']
    pagination_class = CustomPageNumberPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class FAQViewSet(viewsets.ModelViewSet):
    """ViewSet for FAQ model"""
    
    serializer_class = FAQSerializer
    queryset = FAQ.objects.filter(is_published=True).order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_published', 'is_featured']
    search_fields = ['question', 'answer']
    ordering_fields = ['created_at', 'updated_at', 'position']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FAQListSerializer
        return FAQSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        faq = self.get_object()
        faq.views += 1
        faq.save()
        return Response({'status': 'success', 'views': faq.views})


class TicketViewSet(viewsets.ModelViewSet):
    """ViewSet for Ticket model"""
    
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'category', 'status', 'priority', 'assigned_to']
    search_fields = ['ticket_id', 'subject', 'user__email', 'category__name']
    ordering_fields = ['created_at', 'updated_at', 'status', 'priority']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TicketListSerializer
        return TicketSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        ticket = self.get_object()
        messages = TicketMessage.objects.filter(ticket=ticket).order_by('created_at')
        serializer = TicketMessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        ticket = self.get_object()
        ticket.messages.filter(is_read=False).update(is_read=True)
        return Response({'status': 'success'})


class TicketMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for TicketMessage model"""
    
    serializer_class = TicketMessageSerializer
    queryset = TicketMessage.objects.all().order_by('created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TicketMessageCreateSerializer
        return TicketMessageSerializer
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(ticket__user=self.request.user)
    
    def perform_create(self, serializer):
        ticket_id = self.request.data.get('ticket_id')
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            serializer.save(ticket=ticket, sender=self.request.user)
        except Ticket.DoesNotExist:
            raise serializers.ValidationError('Ticket not found')


class TicketCreateAPIView(APIView):
    """APIView for creating support tickets"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = TicketCreateSerializer
    
    def post(self, request):
        serializer = TicketCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            subject = serializer.validated_data['subject']
            category_id = serializer.validated_data['category_id']
            priority = serializer.validated_data.get('priority', 'medium')
            message = serializer.validated_data.get('message', '')
            
            # Get category
            try:
                category = TicketCategory.objects.get(id=category_id)
            except TicketCategory.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Create ticket
            ticket = Ticket.objects.create(
                user=request.user,
                subject=subject,
                category=category,
                priority=priority,
                status='open',
                ticket_id=Ticket.generate_ticket_id()
            )
            
            # Create first message
            TicketMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                message=message,
                is_private=False
            )
            
            serializer = TicketSerializer(ticket, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class TicketStatusUpdateAPIView(APIView):
    """APIView for updating ticket status"""
    
    permission_classes = [IsAdminUser]
    serializer_class = TicketStatusUpdateSerializer
    
    def post(self, request, pk):
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TicketStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            status = serializer.validated_data['status']
            reason = serializer.validated_data.get('reason', '')
            
            old_status = ticket.status
            ticket.status = status
            
            if status == 'resolved':
                ticket.is_resolved = True
            
            ticket.save()
            
            # Add message
            TicketMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                message=f'Status changed from {old_status} to {status}. Reason: {reason}',
                is_private=True
            )
            
            return Response({'status': 'success', 'ticket_id': ticket.id})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SupportStatsAPIView(APIView):
    """APIView for support statistics"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.db.models import Count
        
        stats = {
            'total_tickets': Ticket.objects.count(),
            'open_tickets': Ticket.objects.filter(status='open').count(),
            'pending_tickets': Ticket.objects.filter(status='pending').count(),
            'resolved_tickets': Ticket.objects.filter(status='resolved').count(),
            'average_response_time': 0,
            'categories': {},
            'recent_tickets': []
        }
        
        # Calculate average response time
        # This is a simplified calculation
        resolved_tickets = Ticket.objects.filter(status='resolved')
        if resolved_tickets.exists():
            total_time = sum(
                (ticket.updated_at - ticket.created_at).total_seconds()
                for ticket in resolved_tickets
            )
            stats['average_response_time'] = total_time / resolved_tickets.count()
        
        # Categories
        category_stats = Ticket.objects.values('category__name').annotate(
            count=Count('id')
        )
        for stat in category_stats:
            stats['categories'][stat['category__name']] = stat['count']
        
        # Recent tickets
        recent_tickets = Ticket.objects.order_by('-created_at')[:10]
        for ticket in recent_tickets:
            stats['recent_tickets'].append({
                'id': ticket.id,
                'ticket_id': ticket.ticket_id,
                'subject': ticket.subject,
                'user_email': ticket.user.email,
                'category': ticket.category.name,
                'status': ticket.status,
                'priority': ticket.priority,
                'created_at': ticket.created_at
            })
        
        serializer = SupportStatsSerializer(stats)
        return Response(serializer.data)
