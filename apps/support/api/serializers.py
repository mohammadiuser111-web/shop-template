"""
API serializers for Support app.
"""
from rest_framework import serializers
from ..models import (
    SupportCategory, TicketPriority, TicketStatus,
    Ticket, TicketMessage, TicketAttachment, TicketTag,
    TicketTemplate, FAQ, FAQCategory, CustomerSatisfaction
)


# Support Category Serializers
class SupportCategorySerializer(serializers.ModelSerializer):
    """Serializer for SupportCategory."""
    
    parent = serializers.PrimaryKeyRelatedField(allow_null=True, read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportCategory
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        if obj.children.exists():
            return SupportCategoryListSerializer(obj.children.all(), many=True, context=self.context).data
        return []


class SupportCategoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for support category list."""
    
    class Meta:
        model = SupportCategory
        fields = ['id', 'name', 'slug', 'description', 'parent', 'icon', 'color', 'is_active', 'sort_order']
        read_only_fields = ['id', 'slug']


class SupportCategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating support category."""
    
    class Meta:
        model = SupportCategory
        fields = ['name', 'description', 'parent', 'icon', 'color', 'is_active', 'sort_order']


# Ticket Priority Serializers
class TicketPrioritySerializer(serializers.ModelSerializer):
    """Serializer for TicketPriority."""
    
    class Meta:
        model = TicketPriority
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class TicketPriorityListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ticket priority list."""
    
    class Meta:
        model = TicketPriority
        fields = ['id', 'name', 'level', 'color']
        read_only_fields = ['id', 'level']


# Ticket Status Serializers
class TicketStatusSerializer(serializers.ModelSerializer):
    """Serializer for TicketStatus."""
    
    class Meta:
        model = TicketStatus
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class TicketStatusListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ticket status list."""
    
    class Meta:
        model = TicketStatus
        fields = ['id', 'name', 'code', 'description', 'color', 'is_default', 'is_closed', 'sort_order']
        read_only_fields = ['id', 'code']


# Ticket Tag Serializers
class TicketTagSerializer(serializers.ModelSerializer):
    """Serializer for TicketTag."""
    
    class Meta:
        model = TicketTag
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'created_at']


class TicketTagListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ticket tag list."""
    
    class Meta:
        model = TicketTag
        fields = ['id', 'name', 'slug', 'color']
        read_only_fields = ['id', 'slug']


# Ticket Serializers
class TicketSerializer(serializers.ModelSerializer):
    """Serializer for Ticket."""
    
    category = SupportCategoryListSerializer(read_only=True, allow_null=True)
    priority = TicketPriorityListSerializer(read_only=True, allow_null=True)
    status = TicketStatusListSerializer(read_only=True, allow_null=True)
    customer = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    agent = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    order = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    product = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    tags = TicketTagListSerializer(many=True, read_only=True)
    customer_name = serializers.SerializerMethodField()
    is_open = serializers.SerializerMethodField()
    is_resolved = serializers.SerializerMethodField()
    is_closed = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['id', 'ticket_number', 'category', 'priority', 'status', 'customer',
                           'agent', 'order', 'product', 'tags', 'customer_name', 'is_open',
                           'is_resolved', 'is_closed', 'created_at', 'updated_at', 
                           'first_response_at', 'resolved_at', 'closed_at', 'sla_deadline']
    
    def get_customer_name(self, obj):
        return obj.get_customer_name()
    
    def get_is_open(self, obj):
        return obj.is_open()
    
    def get_is_resolved(self, obj):
        return obj.is_resolved()
    
    def get_is_closed(self, obj):
        return obj.is_closed()
    
    def get_message_count(self, obj):
        return obj.get_message_count()


class TicketListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ticket list."""
    
    category = SupportCategoryListSerializer(read_only=True, allow_null=True)
    priority = TicketPriorityListSerializer(read_only=True, allow_null=True)
    status = TicketStatusListSerializer(read_only=True, allow_null=True)
    customer = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    agent = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    customer_name = serializers.SerializerMethodField()
    is_open = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = ['id', 'ticket_number', 'subject', 'category', 'priority', 'status',
                 'customer', 'customer_name', 'agent', 'is_open', 'message_count',
                 'created_at', 'updated_at', 'first_response_at', 'sla_deadline']
        read_only_fields = ['id', 'ticket_number', 'category', 'priority', 'status',
                           'customer', 'customer_name', 'agent', 'is_open', 'message_count',
                           'created_at', 'updated_at', 'first_response_at', 'sla_deadline']
    
    def get_customer_name(self, obj):
        return obj.get_customer_name()
    
    def get_is_open(self, obj):
        return obj.is_open()
    
    def get_message_count(self, obj):
        return obj.get_message_count()


class TicketCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ticket."""
    
    class Meta:
        model = Ticket
        fields = ['subject', 'content', 'category', 'priority', 'order', 'product', 
                 'customer_name', 'customer_email', 'customer_phone']


class TicketUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating ticket."""
    
    class Meta:
        model = Ticket
        fields = ['subject', 'content', 'category', 'priority', 'status', 'agent', 'order', 'product', 'tags']


# Ticket Message Serializers
class TicketMessageSerializer(serializers.ModelSerializer):
    """Serializer for TicketMessage."""
    
    ticket = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TicketMessage
        fields = '__all__'
        read_only_fields = ['id', 'ticket', 'created_by', 'user', 'author_name', 'message_type',
                           'is_read', 'is_internal', 'created_at', 'updated_at']
    
    def get_author_name(self, obj):
        return obj.get_author_name()


class TicketMessageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ticket message list."""
    
    ticket = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TicketMessage
        fields = ['id', 'ticket', 'content', 'message_type', 'created_by', 'user', 
                 'author_name', 'is_read', 'is_internal', 'created_at']
        read_only_fields = ['id', 'ticket', 'message_type', 'created_by', 'user', 
                           'author_name', 'is_read', 'is_internal', 'created_at']
    
    def get_author_name(self, obj):
        return obj.get_author_name()


class TicketMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ticket message."""
    
    class Meta:
        model = TicketMessage
        fields = ['ticket', 'content', 'message_type', 'is_internal']


# Ticket Attachment Serializers
class TicketAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for TicketAttachment."""
    
    uploaded_by = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = TicketAttachment
        fields = '__all__'
        read_only_fields = ['id', 'uploaded_by', 'created_at']
    
    def get_file_size_display(self, obj):
        return obj.get_file_size_display()


class TicketAttachmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ticket attachment list."""
    
    uploaded_by = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = TicketAttachment
        fields = ['id', 'file', 'original_filename', 'file_size', 'file_size_display', 'mime_type', 'uploaded_by']
        read_only_fields = ['id', 'uploaded_by']
    
    def get_file_size_display(self, obj):
        return obj.get_file_size_display()


class TicketAttachmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ticket attachment."""
    
    class Meta:
        model = TicketAttachment
        fields = ['file', 'original_filename', 'file_size', 'mime_type']


# Ticket Template Serializers
class TicketTemplateSerializer(serializers.ModelSerializer):
    """Serializer for TicketTemplate."""
    
    category = SupportCategoryListSerializer(read_only=True, allow_null=True)
    
    class Meta:
        model = TicketTemplate
        fields = '__all__'
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']


class TicketTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ticket template list."""
    
    category = SupportCategoryListSerializer(read_only=True, allow_null=True)
    
    class Meta:
        model = TicketTemplate
        fields = ['id', 'name', 'code', 'subject', 'category', 'is_active', 'sort_order']
        read_only_fields = ['id', 'code']


class TicketTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ticket template."""
    
    class Meta:
        model = TicketTemplate
        fields = ['name', 'code', 'subject', 'content', 'category', 'variables', 'is_active', 'sort_order']


# FAQ Serializers
class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQ."""
    
    category = SupportCategoryListSerializer(read_only=True, allow_null=True)
    tags = TicketTagListSerializer(many=True, read_only=True)
    
    class Meta:
        model = FAQ
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'view_count', 'helpful_count', 'created_at', 'updated_at']


class FAQListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for FAQ list."""
    
    category = SupportCategoryListSerializer(read_only=True, allow_null=True)
    tags = TicketTagListSerializer(many=True, read_only=True)
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'slug', 'answer', 'category', 'tags', 'is_active', 
                 'is_featured', 'sort_order', 'view_count', 'helpful_count']
        read_only_fields = ['id', 'slug', 'view_count', 'helpful_count']


class FAQCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating FAQ."""
    
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'category', 'tags', 'meta_title', 'meta_description',
                 'is_active', 'is_featured', 'sort_order']


# FAQ Category Serializers
class FAQCategorySerializer(serializers.ModelSerializer):
    """Serializer for FAQCategory."""
    
    parent = serializers.PrimaryKeyRelatedField(allow_null=True, read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = FAQCategory
        fields = '__all__'
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        if obj.faq_children.exists():
            return FAQCategoryListSerializer(obj.faq_children.all(), many=True, context=self.context).data
        return []


class FAQCategoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for FAQ category list."""
    
    class Meta:
        model = FAQCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'parent', 'is_active', 'sort_order']
        read_only_fields = ['id', 'slug']


class FAQCategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating FAQ category."""
    
    class Meta:
        model = FAQCategory
        fields = ['name', 'description', 'icon', 'parent', 'is_active', 'sort_order']


# Customer Satisfaction Serializers
class CustomerSatisfactionSerializer(serializers.ModelSerializer):
    """Serializer for CustomerSatisfaction."""
    
    ticket = serializers.PrimaryKeyRelatedField(read_only=True)
    customer = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerSatisfaction
        fields = '__all__'
        read_only_fields = ['id', 'ticket', 'customer', 'average_rating', 'is_completed', 'created_at', 'updated_at', 'completed_at']
    
    def get_average_rating(self, obj):
        return obj.get_average_rating()


class CustomerSatisfactionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for customer satisfaction list."""
    
    ticket = serializers.PrimaryKeyRelatedField(read_only=True)
    customer = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerSatisfaction
        fields = ['id', 'ticket', 'customer', 'rating', 'feedback', 'agent_rating',
                 'resolution_rating', 'response_time_rating', 'average_rating',
                 'is_completed', 'created_at']
        read_only_fields = ['id', 'ticket', 'customer', 'average_rating', 'is_completed', 'created_at']
    
    def get_average_rating(self, obj):
        return obj.get_average_rating()


class CustomerSatisfactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating customer satisfaction survey."""
    
    class Meta:
        model = CustomerSatisfaction
        fields = ['ticket', 'rating', 'feedback', 'agent_rating', 'resolution_rating', 'response_time_rating']


# Support Statistics Serializer
class SupportStatisticsSerializer(serializers.Serializer):
    """Serializer for support statistics."""
    
    total_tickets = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    resolved_tickets = serializers.IntegerField()
    closed_tickets = serializers.IntegerField()
    average_response_time = serializers.FloatField()
    average_resolution_time = serializers.FloatField()
    customer_satisfaction = serializers.FloatField()
    total_faqs = serializers.IntegerField()
