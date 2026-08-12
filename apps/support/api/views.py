"""
API views for Support app.
"""
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
import uuid

from ..models import (
    SupportCategory, TicketPriority, TicketStatus,
    Ticket, TicketMessage, TicketAttachment, TicketTag,
    TicketTemplate, FAQ, FAQCategory, CustomerSatisfaction
)
from .serializers import (
    SupportCategorySerializer, SupportCategoryListSerializer, SupportCategoryCreateSerializer,
    TicketPrioritySerializer, TicketPriorityListSerializer,
    TicketStatusSerializer, TicketStatusListSerializer,
    TicketTagSerializer, TicketTagListSerializer,
    TicketSerializer, TicketListSerializer, TicketCreateSerializer, TicketUpdateSerializer,
    TicketMessageSerializer, TicketMessageListSerializer, TicketMessageCreateSerializer,
    TicketAttachmentSerializer, TicketAttachmentListSerializer, TicketAttachmentCreateSerializer,
    TicketTemplateSerializer, TicketTemplateListSerializer, TicketTemplateCreateSerializer,
    FAQSerializer, FAQListSerializer, FAQCreateSerializer,
    FAQCategorySerializer, FAQCategoryListSerializer, FAQCategoryCreateSerializer,
    CustomerSatisfactionSerializer, CustomerSatisfactionListSerializer, CustomerSatisfactionCreateSerializer,
    SupportStatisticsSerializer
)


# Support Category Views
class SupportCategoryListAPIView(generics.ListAPIView):
    """List support categories."""
    
    serializer_class = SupportCategoryListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get support categories."""
        parent_id = self.kwargs.get('parent_id')
        
        if parent_id:
            parent = get_object_or_404(SupportCategory, pk=parent_id)
            return SupportCategory.objects.filter(parent=parent, is_active=True).order_by('sort_order', 'name')
        
        return SupportCategory.objects.filter(parent__isnull=True, is_active=True).order_by('sort_order', 'name')


class SupportCategoryRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve support category."""
    
    serializer_class = SupportCategorySerializer
    permission_classes = [permissions.AllowAny]
    queryset = SupportCategory.objects.all()


class SupportCategoryCreateAPIView(generics.CreateAPIView):
    """Create support category."""
    
    serializer_class = SupportCategoryCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class SupportCategoryUpdateAPIView(generics.UpdateAPIView):
    """Update support category."""
    
    serializer_class = SupportCategoryCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = SupportCategory.objects.all()


class SupportCategoryDestroyAPIView(generics.DestroyAPIView):
    """Delete support category."""
    
    serializer_class = SupportCategorySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = SupportCategory.objects.all()


# Ticket Priority Views
class TicketPriorityListAPIView(generics.ListAPIView):
    """List ticket priorities."""
    
    serializer_class = TicketPriorityListSerializer
    permission_classes = [permissions.AllowAny]
    queryset = TicketPriority.objects.all().order_by('level')


class TicketPriorityRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve ticket priority."""
    
    serializer_class = TicketPrioritySerializer
    permission_classes = [permissions.AllowAny]
    queryset = TicketPriority.objects.all()


class TicketPriorityCreateAPIView(generics.CreateAPIView):
    """Create ticket priority."""
    
    serializer_class = TicketPrioritySerializer
    permission_classes = [permissions.IsAdminUser]


class TicketPriorityUpdateAPIView(generics.UpdateAPIView):
    """Update ticket priority."""
    
    serializer_class = TicketPrioritySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = TicketPriority.objects.all()


# Ticket Status Views
class TicketStatusListAPIView(generics.ListAPIView):
    """List ticket statuses."""
    
    serializer_class = TicketStatusListSerializer
    permission_classes = [permissions.AllowAny]
    queryset = TicketStatus.objects.all().order_by('sort_order')


class TicketStatusRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve ticket status."""
    
    serializer_class = TicketStatusSerializer
    permission_classes = [permissions.AllowAny]
    queryset = TicketStatus.objects.all()


class TicketStatusCreateAPIView(generics.CreateAPIView):
    """Create ticket status."""
    
    serializer_class = TicketStatusSerializer
    permission_classes = [permissions.IsAdminUser]


# Ticket Tag Views
class TicketTagListAPIView(generics.ListAPIView):
    """List ticket tags."""
    
    serializer_class = TicketTagListSerializer
    permission_classes = [permissions.AllowAny]
    queryset = TicketTag.objects.all().order_by('name')


class TicketTagRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve ticket tag."""
    
    serializer_class = TicketTagSerializer
    permission_classes = [permissions.AllowAny]
    queryset = TicketTag.objects.all()


class TicketTagCreateAPIView(generics.CreateAPIView):
    """Create ticket tag."""
    
    serializer_class = TicketTagSerializer
    permission_classes = [permissions.IsAdminUser]


# Ticket Views
class TicketListAPIView(generics.ListAPIView):
    """List tickets."""
    
    serializer_class = TicketListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get tickets."""
        if self.request.user.is_superuser:
            return Ticket.objects.all().order_by('-priority__level', '-created_at')
        
        # For regular users, only return their own tickets
        return Ticket.objects.filter(customer=self.request.user).order_by('-created_at')


class TicketRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve ticket."""
    
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get tickets."""
        if self.request.user.is_superuser:
            return Ticket.objects.all()
        return Ticket.objects.filter(customer=self.request.user)


class TicketCreateAPIView(generics.CreateAPIView):
    """Create ticket."""
    
    serializer_class = TicketCreateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        """Generate ticket number and set customer."""
        ticket_number = f"TKT-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        
        if self.request.user.is_authenticated:
            serializer.save(
                ticket_number=ticket_number,
                customer=self.request.user,
                customer_name=self.request.user.get_full_name() or self.request.user.phone_number or self.request.user.email,
                customer_email=self.request.user.email or ''
            )
        else:
            serializer.save(ticket_number=ticket_number)


class TicketUpdateAPIView(generics.UpdateAPIView):
    """Update ticket."""
    
    serializer_class = TicketUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Ticket.objects.all()


class TicketDestroyAPIView(generics.DestroyAPIView):
    """Delete ticket."""
    
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Ticket.objects.all()


class TicketCloseAPIView(views.APIView):
    """Close a ticket."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, pk):
        """Close ticket."""
        ticket = get_object_or_404(Ticket, pk=pk)
        closed_status = TicketStatus.objects.filter(is_closed=True).first()
        
        if closed_status:
            ticket.status = closed_status
        ticket.closed_at = timezone.now()
        ticket.save()
        
        serializer = TicketSerializer(ticket, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class TicketReopenAPIView(views.APIView):
    """Reopen a ticket."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, pk):
        """Reopen ticket."""
        ticket = get_object_or_404(Ticket, pk=pk)
        open_status = TicketStatus.objects.filter(is_closed=False).first()
        
        if open_status:
            ticket.status = open_status
        ticket.closed_at = None
        ticket.save()
        
        serializer = TicketSerializer(ticket, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserTicketsAPIView(generics.ListAPIView):
    """List user's tickets."""
    
    serializer_class = TicketListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's tickets."""
        return Ticket.objects.filter(customer=self.request.user).order_by('-created_at')


class UserTicketRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve user's ticket."""
    
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's tickets."""
        return Ticket.objects.filter(customer=self.request.user)


# Ticket Message Views
class TicketMessageListAPIView(generics.ListAPIView):
    """List ticket messages."""
    
    serializer_class = TicketMessageListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get ticket messages."""
        ticket_id = self.kwargs.get('ticket_id')
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        
        # Check if user has access to this ticket
        if not self.request.user.is_superuser and ticket.customer != self.request.user:
            return TicketMessage.objects.none()
        
        return TicketMessage.objects.filter(ticket=ticket).order_by('created_at')


class TicketMessageRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve ticket message."""
    
    serializer_class = TicketMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = TicketMessage.objects.all()


class TicketMessageCreateAPIView(generics.CreateAPIView):
    """Create ticket message."""
    
    serializer_class = TicketMessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Set created_by and user."""
        ticket = serializer.validated_data.get('ticket')
        
        # Check if user has access to this ticket
        if not self.request.user.is_superuser and ticket.customer != self.request.user:
            raise permissions.PermissionDenied('Permission denied')
        
        # Determine message type
        if self.request.user.is_superuser:
            message_type = 'agent'
        else:
            message_type = 'customer'
        
        serializer.save(
            created_by=self.request.user,
            user=self.request.user,
            message_type=message_type
        )
        
        # Update first_response_at if this is the first response
        if ticket.first_response_at is None and message_type == 'agent':
            ticket.first_response_at = timezone.now()
            ticket.save()


class TicketMessageDestroyAPIView(generics.DestroyAPIView):
    """Delete ticket message."""
    
    serializer_class = TicketMessageSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = TicketMessage.objects.all()


# Ticket Attachment Views
class TicketAttachmentListAPIView(generics.ListAPIView):
    """List ticket attachments."""
    
    serializer_class = TicketAttachmentListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get ticket attachments."""
        ticket_id = self.kwargs.get('ticket_id')
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        
        # Check if user has access to this ticket
        if not self.request.user.is_superuser and ticket.customer != self.request.user:
            return TicketAttachment.objects.none()
        
        return ticket.attachments.all()


class TicketAttachmentRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve ticket attachment."""
    
    serializer_class = TicketAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = TicketAttachment.objects.all()


class TicketAttachmentCreateAPIView(generics.CreateAPIView):
    """Create ticket attachment."""
    
    serializer_class = TicketAttachmentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Set uploaded_by."""
        serializer.save(uploaded_by=self.request.user)


class TicketAttachmentDestroyAPIView(generics.DestroyAPIView):
    """Delete ticket attachment."""
    
    serializer_class = TicketAttachmentSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = TicketAttachment.objects.all()


# Ticket Template Views
class TicketTemplateListAPIView(generics.ListAPIView):
    """List ticket templates."""
    
    serializer_class = TicketTemplateListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get ticket templates."""
        category_id = self.kwargs.get('category_id')
        
        if category_id:
            category = get_object_or_404(SupportCategory, pk=category_id)
            return TicketTemplate.objects.filter(category=category, is_active=True).order_by('sort_order', 'name')
        
        return TicketTemplate.objects.filter(is_active=True).order_by('sort_order', 'name')


class TicketTemplateRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve ticket template."""
    
    serializer_class = TicketTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = TicketTemplate.objects.all()


class TicketTemplateCreateAPIView(generics.CreateAPIView):
    """Create ticket template."""
    
    serializer_class = TicketTemplateCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class TicketTemplateDestroyAPIView(generics.DestroyAPIView):
    """Delete ticket template."""
    
    serializer_class = TicketTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = TicketTemplate.objects.all()


# FAQ Views
class FAQListAPIView(generics.ListAPIView):
    """List FAQs."""
    
    serializer_class = FAQListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get FAQs."""
        category_id = self.kwargs.get('category_id')
        tag_id = self.kwargs.get('tag_id')
        
        queryset = FAQ.objects.filter(is_active=True)
        
        if category_id:
            category = get_object_or_404(SupportCategory, pk=category_id)
            queryset = queryset.filter(category=category)
        
        if tag_id:
            tag = get_object_or_404(TicketTag, pk=tag_id)
            queryset = queryset.filter(tags=tag)
        
        return queryset.order_by('-is_featured', 'sort_order', '-created_at')


class FAQRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve FAQ."""
    
    serializer_class = FAQSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_object(self):
        """Get FAQ and increment view count."""
        faq = super().get_object()
        faq.increment_view_count()
        return faq
    
    def get_queryset(self):
        """Get FAQs."""
        return FAQ.objects.all()


class FAQCreateAPIView(generics.CreateAPIView):
    """Create FAQ."""
    
    serializer_class = FAQCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class FAQUpdateAPIView(generics.UpdateAPIView):
    """Update FAQ."""
    
    serializer_class = FAQSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = FAQ.objects.all()


class FAQDestroyAPIView(generics.DestroyAPIView):
    """Delete FAQ."""
    
    serializer_class = FAQSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = FAQ.objects.all()


class FAQSearchAPIView(views.APIView):
    """Search FAQs."""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Search FAQs."""
        query = request.query_params.get('q', '')
        
        from django.db.models import Q
        
        queryset = FAQ.objects.filter(is_active=True)
        
        if query:
            queryset = queryset.filter(
                Q(question__icontains=query) | 
                Q(answer__icontains=query)
            )
        
        queryset = queryset.order_by('-is_featured', 'sort_order')
        
        serializer = FAQListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class FAQHelpfulAPIView(views.APIView):
    """Mark FAQ as helpful."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Mark FAQ as helpful."""
        faq = get_object_or_404(FAQ, pk=pk)
        faq.increment_helpful_count()
        
        return Response({
            'detail': 'Thank you for your feedback',
            'helpful_count': faq.helpful_count
        }, status=status.HTTP_200_OK)


# FAQ Category Views
class FAQCategoryListAPIView(generics.ListAPIView):
    """List FAQ categories."""
    
    serializer_class = FAQCategoryListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get FAQ categories."""
        parent_id = self.kwargs.get('parent_id')
        
        if parent_id:
            parent = get_object_or_404(FAQCategory, pk=parent_id)
            return FAQCategory.objects.filter(parent=parent, is_active=True).order_by('sort_order', 'name')
        
        return FAQCategory.objects.filter(parent__isnull=True, is_active=True).order_by('sort_order', 'name')


class FAQCategoryRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve FAQ category."""
    
    serializer_class = FAQCategorySerializer
    permission_classes = [permissions.AllowAny]
    queryset = FAQCategory.objects.all()


class FAQCategoryCreateAPIView(generics.CreateAPIView):
    """Create FAQ category."""
    
    serializer_class = FAQCategoryCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class FAQCategoryUpdateAPIView(generics.UpdateAPIView):
    """Update FAQ category."""
    
    serializer_class = FAQCategoryCreateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = FAQCategory.objects.all()


class FAQCategoryDestroyAPIView(generics.DestroyAPIView):
    """Delete FAQ category."""
    
    serializer_class = FAQCategorySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = FAQCategory.objects.all()


# Customer Satisfaction Views
class CustomerSatisfactionListAPIView(generics.ListAPIView):
    """List customer satisfaction surveys."""
    
    serializer_class = CustomerSatisfactionListSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = CustomerSatisfaction.objects.all().order_by('-created_at')


class CustomerSatisfactionRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve customer satisfaction survey."""
    
    serializer_class = CustomerSatisfactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get customer satisfaction surveys."""
        if self.request.user.is_superuser:
            return CustomerSatisfaction.objects.all()
        return CustomerSatisfaction.objects.filter(customer=self.request.user)


class CustomerSatisfactionCreateAPIView(generics.CreateAPIView):
    """Create customer satisfaction survey."""
    
    serializer_class = CustomerSatisfactionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Set customer and mark as completed."""
        serializer.save(
            customer=self.request.user,
            is_completed=True,
            completed_at=timezone.now()
        )


# Support Statistics View
class SupportStatisticsAPIView(views.APIView):
    """Get support statistics."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """Return support statistics."""
        from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
        from django.db.models.functions import Now
        
        # Total tickets
        total_tickets = Ticket.objects.count()
        
        # Open tickets
        open_tickets = Ticket.objects.filter(status__is_closed=False).count()
        
        # Resolved tickets
        resolved_tickets = Ticket.objects.filter(resolved_at__isnull=False).count()
        
        # Closed tickets
        closed_tickets = Ticket.objects.filter(closed_at__isnull=False).count()
        
        # Average response time
        open_tickets_with_response = Ticket.objects.filter(
            first_response_at__isnull=False,
            status__is_closed=False
        )
        if open_tickets_with_response.exists():
            avg_response_time = open_tickets_with_response.aggregate(
                avg_time=Avg(
                    ExpressionWrapper(
                        F('first_response_at') - F('created_at'),
                        output_field=DurationField()
                    )
                )
            )['avg_time']
            # Convert to hours
            avg_response_time_hours = avg_response_time.total_seconds() / 3600 if avg_response_time else 0
        else:
            avg_response_time_hours = 0
        
        # Average resolution time
        resolved_tickets_with_times = Ticket.objects.filter(
            resolved_at__isnull=False,
            first_response_at__isnull=False
        )
        if resolved_tickets_with_times.exists():
            avg_resolution_time = resolved_tickets_with_times.aggregate(
                avg_time=Avg(
                    ExpressionWrapper(
                        F('resolved_at') - F('first_response_at'),
                        output_field=DurationField()
                    )
                )
            )['avg_time']
            # Convert to hours
            avg_resolution_time_hours = avg_resolution_time.total_seconds() / 3600 if avg_resolution_time else 0
        else:
            avg_resolution_time_hours = 0
        
        # Customer satisfaction
        satisfaction_surveys = CustomerSatisfaction.objects.filter(is_completed=True)
        if satisfaction_surveys.exists():
            avg_satisfaction = satisfaction_surveys.aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0
        else:
            avg_satisfaction = 0
        
        # Total FAQs
        total_faqs = FAQ.objects.count()
        
        data = {
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'resolved_tickets': resolved_tickets,
            'closed_tickets': closed_tickets,
            'average_response_time': round(avg_response_time_hours, 2),
            'average_resolution_time': round(avg_resolution_time_hours, 2),
            'customer_satisfaction': round(avg_satisfaction, 2),
            'total_faqs': total_faqs
        }
        
        serializer = SupportStatisticsSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_200_OK)


# Recent Tickets View
class RecentTicketsAPIView(views.APIView):
    """Get recent tickets."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Return recent tickets."""
        limit = int(request.query_params.get('limit', 5))
        
        if request.user.is_superuser:
            tickets = Ticket.objects.all().order_by('-created_at')[:limit]
        else:
            tickets = Ticket.objects.filter(customer=request.user).order_by('-created_at')[:limit]
        
        serializer = TicketListSerializer(tickets, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
