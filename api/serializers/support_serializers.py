"""
Support Serializers
Serializers for support models: Ticket, TicketMessage, TicketCategory, FAQ, FAQCategory
"""

from rest_framework import serializers
from apps.support.models import Ticket, TicketMessage, TicketCategory, FAQ, FAQCategory
from .accounts_serializers import UserPublicSerializer


class TicketCategorySerializer(serializers.ModelSerializer):
    """Serializer for TicketCategory model"""
    
    class Meta:
        model = TicketCategory
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug')


class FAQCategorySerializer(serializers.ModelSerializer):
    """Serializer for FAQCategory model"""
    
    class Meta:
        model = FAQCategory
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug')


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQ model"""
    
    category = FAQCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = FAQ
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'slug', 'views', 'is_published')


class FAQListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for FAQ lists"""
    
    category = serializers.StringField(source='category.name', read_only=True)
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'category', 'is_published', 'created_at']
        read_only_fields = fields


class TicketMessageSerializer(serializers.ModelSerializer):
    """Serializer for TicketMessage model"""
    
    sender = UserPublicSerializer(read_only=True)
    attachments = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = TicketMessage
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'ticket', 'sender', 'attachments')
    
    def get_attachments(self, obj):
        if obj.attachments:
            attachments = obj.attachments.all()
            return [
                self.context['request'].build_absolute_uri(a.file.url) 
                for a in attachments
            ]
        return []


class TicketMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ticket messages"""
    
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = TicketMessage
        fields = ['message', 'attachments', 'is_private']


class TicketSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for Ticket model"""
    
    user = UserPublicSerializer(read_only=True)
    category = TicketCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=True)
    assigned_to = UserPublicSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    messages = TicketMessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField(read_only=True)
    unread_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user', 'ticket_id', 'status', 'priority', 'assigned_to', 'messages', 'last_message', 'unread_count', 'is_resolved')
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'id': last_msg.id,
                'message': last_msg.message,
                'sender': last_msg.sender.email if last_msg.sender else None,
                'created_at': last_msg.created_at,
                'is_private': last_msg.is_private
            }
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(
                is_read=False,
                sender__isnull=False
            ).exclude(sender=request.user).count()
        return 0


class TicketListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ticket lists"""
    
    user = serializers.StringField(source='user.email', read_only=True)
    category = serializers.StringField(source='category.name', read_only=True)
    assigned_to = serializers.StringField(source='assigned_to.email', read_only=True)
    unread_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Ticket
        fields = ['id', 'ticket_id', 'subject', 'user', 'category', 'status', 'priority', 'assigned_to', 'unread_count', 'created_at', 'updated_at']
        read_only_fields = fields
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(
                is_read=False,
                sender__isnull=False
            ).exclude(sender=request.user).count()
        return 0


class TicketCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating support tickets"""
    
    category_id = serializers.IntegerField(required=True)
    
    class Meta:
        model = Ticket
        fields = ['subject', 'category_id', 'priority', 'message']


class TicketUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tickets"""
    
    assigned_to_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Ticket
        fields = ['subject', 'category_id', 'priority', 'status', 'assigned_to_id', 'is_resolved']


class TicketStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating ticket status"""
    
    status = serializers.ChoiceField(
        choices=['open', 'pending', 'resolved', 'closed', 'reopened'],
        required=True
    )
    reason = serializers.CharField(required=False, allow_blank=True)


class SupportStatsSerializer(serializers.Serializer):
    """Serializer for support statistics"""
    
    total_tickets = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    pending_tickets = serializers.IntegerField()
    resolved_tickets = serializers.IntegerField()
    average_response_time = serializers.FloatField()
    categories = serializers.DictField()
    recent_tickets = serializers.ListField(child=serializers.DictField())
