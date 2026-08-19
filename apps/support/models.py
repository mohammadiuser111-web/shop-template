"""
Support models for shop-template project.
"""
from django.db import models
from django.conf import settings
import uuid


class SupportCategory(models.Model):
    """
    Model for support ticket categories.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Description', blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
        verbose_name='Parent Category'
    )
    icon = models.CharField(max_length=50, verbose_name='Icon', blank=True)
    color = models.CharField(max_length=20, verbose_name='Color', blank=True)
    
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Support Category'
        verbose_name_plural = 'Support Categories'
        ordering = ['parent__sort_order', 'sort_order', 'name']
    
    def __str__(self):
        return self.name


class TicketPriority(models.Model):
    """
    Model for ticket priorities.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Name')
    level = models.PositiveSmallIntegerField(verbose_name='Level', unique=True)
    color = models.CharField(max_length=20, verbose_name='Color')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Ticket Priority'
        verbose_name_plural = 'Ticket Priorities'
        ordering = ['level']
    
    def __str__(self):
        return self.name


class TicketStatus(models.Model):
    """
    Model for ticket statuses.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Name')
    code = models.CharField(max_length=50, unique=True, verbose_name='Code')
    description = models.TextField(verbose_name='Description', blank=True)
    color = models.CharField(max_length=20, verbose_name='Color', blank=True)
    
    is_default = models.BooleanField(default=False, verbose_name='Is Default')
    is_closed = models.BooleanField(default=False, verbose_name='Is Closed')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Ticket Status'
        verbose_name_plural = 'Ticket Statuses'
        ordering = ['sort_order']
    
    def __str__(self):
        return self.name


class Ticket(models.Model):
    """
    Model for support tickets.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_id = models.CharField(max_length=20, unique=True, verbose_name='Ticket ID')
    ticket_number = models.CharField(max_length=20, unique=True, verbose_name='Ticket Number')
    
    @classmethod
    def generate_ticket_id(cls):
        """Generate a unique ticket ID."""
        import random
        import string
        while True:
            ticket_id = 'TKT-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not cls.objects.filter(ticket_id=ticket_id).exists():
                return ticket_id
    
    # Subject and content
    subject = models.CharField(max_length=300, verbose_name='Subject')
    content = models.TextField(verbose_name='Content')
    
    # Category and priority
    category = models.ForeignKey(
        SupportCategory,
        on_delete=models.SET_NULL,
        related_name='tickets',
        null=True,
        blank=True,
        verbose_name='Category'
    )
    priority = models.ForeignKey(
        TicketPriority,
        on_delete=models.SET_NULL,
        related_name='tickets',
        null=True,
        blank=True,
        verbose_name='Priority'
    )
    
    # Status
    status = models.ForeignKey(
        TicketStatus,
        on_delete=models.SET_NULL,
        related_name='tickets',
        null=True,
        blank=True,
        verbose_name='Status'
    )
    
    # Customer
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='tickets',
        null=True,
        blank=True,
        verbose_name='Customer'
    )
    customer_name = models.CharField(max_length=200, verbose_name='Customer Name')
    customer_email = models.EmailField(verbose_name='Customer Email')
    customer_phone = models.CharField(max_length=20, verbose_name='Customer Phone', blank=True)
    
    # Related order
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        related_name='tickets',
        null=True,
        blank=True,
        verbose_name='Order'
    )
    
    # Related product
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        related_name='tickets',
        null=True,
        blank=True,
        verbose_name='Product'
    )
    
    # Agent
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_tickets',
        null=True,
        blank=True,
        verbose_name='Agent'
    )
    
    # Attachments
    attachments = models.ManyToManyField(
        'TicketAttachment',
        related_name='tickets',
        verbose_name='Attachments',
        blank=True
    )
    
    # Metadata
    tags = models.ManyToManyField(
        'TicketTag',
        related_name='tickets',
        verbose_name='Tags',
        blank=True
    )
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    first_response_at = models.DateTimeField(verbose_name='First Response At', null=True, blank=True)
    resolved_at = models.DateTimeField(verbose_name='Resolved At', null=True, blank=True)
    closed_at = models.DateTimeField(verbose_name='Closed At', null=True, blank=True)
    
    # SLA
    sla_deadline = models.DateTimeField(verbose_name='SLA Deadline', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-priority__level', '-created_at']
        indexes = [
            models.Index(fields=['ticket_number']),
            models.Index(fields=['customer']),
            models.Index(fields=['agent']),
            models.Index(fields=['category']),
            models.Index(fields=['priority']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"#{self.ticket_number} - {self.subject}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('support:ticket_detail', kwargs={'ticket_number': self.ticket_number})
    
    def is_open(self):
        """Check if ticket is open."""
        return self.status and not self.status.is_closed
    
    def is_resolved(self):
        """Check if ticket is resolved."""
        return self.resolved_at is not None
    
    def is_closed(self):
        """Check if ticket is closed."""
        return self.closed_at is not None
    
    def get_customer_name(self):
        """Get customer display name."""
        if self.customer:
            return self.customer.get_full_name() or self.customer.phone_number or self.customer.email
        return self.customer_name
    
    def get_last_message(self):
        """Get the last message in the ticket."""
        return self.messages.order_by('-created_at').first()
    
    def get_message_count(self):
        """Get total number of messages."""
        return self.messages.count()
    
    def get_unread_count(self, user):
        """Get number of unread messages for a user."""
        return self.messages.filter(is_read=False, user__isnull=True).exclude(created_by=user).count()
    
    def mark_as_read(self, user):
        """Mark all messages as read for a user."""
        self.messages.filter(is_read=False, user__isnull=True).exclude(created_by=user).update(is_read=True)


class TicketMessage(models.Model):
    """
    Model for ticket messages.
    """
    MESSAGE_TYPES = [
        ('customer', 'Customer'),
        ('agent', 'Agent'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Ticket'
    )
    
    # Content
    content = models.TextField(verbose_name='Content')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, verbose_name='Message Type')
    
    # Author
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='ticket_messages',
        null=True,
        blank=True,
        verbose_name='Created By'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='user_messages',
        null=True,
        blank=True,
        verbose_name='User'
    )
    
    # Attachments
    attachments = models.ManyToManyField(
        'TicketAttachment',
        related_name='messages',
        verbose_name='Attachments',
        blank=True
    )
    
    # Status
    is_read = models.BooleanField(default=False, verbose_name='Is Read')
    is_internal = models.BooleanField(default=False, verbose_name='Is Internal')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Ticket Message'
        verbose_name_plural = 'Ticket Messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message #{self.id} - {self.ticket}"
    
    def get_author_name(self):
        """Get author display name."""
        if self.created_by:
            return self.created_by.get_full_name() or self.created_by.phone_number or self.created_by.email
        return 'System'


class TicketAttachment(models.Model):
    """
    Model for ticket attachments.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='support/attachments/', verbose_name='File')
    original_filename = models.CharField(max_length=255, verbose_name='Original Filename')
    file_size = models.PositiveIntegerField(verbose_name='File Size (bytes)')
    mime_type = models.CharField(max_length=100, verbose_name='MIME Type')
    
    # Security
    is_virus_checked = models.BooleanField(default=False, verbose_name='Is Virus Checked')
    is_safe = models.BooleanField(default=True, verbose_name='Is Safe')
    
    # User
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='uploaded_attachments',
        null=True,
        blank=True,
        verbose_name='Uploaded By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Ticket Attachment'
        verbose_name_plural = 'Ticket Attachments'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.original_filename
    
    def get_file_size_display(self):
        """Get human-readable file size."""
        from django.utils.humanize import natural_size
        return natural_size(self.file_size)


class TicketTag(models.Model):
    """
    Model for ticket tags.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='Name')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Slug')
    color = models.CharField(max_length=20, verbose_name='Color', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Ticket Tag'
        verbose_name_plural = 'Ticket Tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TicketTemplate(models.Model):
    """
    Model for ticket response templates.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    code = models.CharField(max_length=100, unique=True, verbose_name='Code')
    
    # Content
    subject = models.CharField(max_length=300, verbose_name='Subject', blank=True)
    content = models.TextField(verbose_name='Content')
    
    # Category
    category = models.ForeignKey(
        SupportCategory,
        on_delete=models.SET_NULL,
        related_name='templates',
        null=True,
        blank=True,
        verbose_name='Category'
    )
    
    # Variables
    variables = models.JSONField(
        verbose_name='Variables',
        default=list,
        blank=True,
        help_text='List of variables that can be used in the template (e.g., ["customer_name", "ticket_number"])'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Ticket Template'
        verbose_name_plural = 'Ticket Templates'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def render(self, context):
        """Render template with context."""
        from django.template import Template, Context
        
        subject_template = Template(self.subject) if self.subject else None
        content_template = Template(self.content)
        
        django_context = Context(context)
        
        subject = subject_template.render(django_context) if subject_template else ''
        content = content_template.render(django_context)
        
        return {
            'subject': subject,
            'content': content,
        }


class FAQ(models.Model):
    """
    Model for Frequently Asked Questions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=300, verbose_name='Question')
    answer = models.TextField(verbose_name='Answer')
    
    # Category
    category = models.ForeignKey(
        SupportCategory,
        on_delete=models.SET_NULL,
        related_name='faqs',
        null=True,
        blank=True,
        verbose_name='Category'
    )
    
    # Tags
    tags = models.ManyToManyField(
        TicketTag,
        related_name='faqs',
        verbose_name='Tags',
        blank=True
    )
    
    # SEO
    slug = models.SlugField(max_length=300, unique=True, verbose_name='Slug', blank=True)
    meta_title = models.CharField(max_length=200, verbose_name='Meta Title', blank=True)
    meta_description = models.TextField(verbose_name='Meta Description', blank=True)
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    is_featured = models.BooleanField(default=False, verbose_name='Is Featured')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    # View count
    view_count = models.PositiveIntegerField(default=0, verbose_name='View Count')
    helpful_count = models.PositiveIntegerField(default=0, verbose_name='Helpful Count')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['sort_order', '-created_at']
    
    def __str__(self):
        return self.question
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('support:faq_detail', kwargs={'pk': self.id})
    
    def increment_view_count(self):
        """Increment view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_helpful_count(self):
        """Increment helpful count."""
        self.helpful_count += 1
        self.save(update_fields=['helpful_count'])


class FAQCategory(models.Model):
    """
    Model for FAQ categories (separate from support categories).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Description', blank=True)
    icon = models.CharField(max_length=50, verbose_name='Icon', blank=True)
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='faq_children',
        null=True,
        blank=True,
        verbose_name='Parent Category'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'FAQ Category'
        verbose_name_plural = 'FAQ Categories'
        ordering = ['parent__sort_order', 'sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('support:faq_category', kwargs={'slug': self.slug})


class CustomerSatisfaction(models.Model):
    """
    Model for customer satisfaction surveys.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='satisfaction_surveys',
        verbose_name='Ticket'
    )
    
    # Rating
    rating = models.PositiveSmallIntegerField(
        verbose_name='Rating',
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        null=True,
        blank=True
    )
    
    # Feedback
    feedback = models.TextField(verbose_name='Feedback', blank=True)
    
    # Agent rating
    agent_rating = models.PositiveSmallIntegerField(
        verbose_name='Agent Rating',
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        null=True,
        blank=True
    )
    
    # Resolution
    resolution_rating = models.PositiveSmallIntegerField(
        verbose_name='Resolution Rating',
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        null=True,
        blank=True
    )
    
    # Response time
    response_time_rating = models.PositiveSmallIntegerField(
        verbose_name='Response Time Rating',
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        null=True,
        blank=True
    )
    
    # Customer
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='satisfaction_surveys',
        null=True,
        blank=True,
        verbose_name='Customer'
    )
    
    # Status
    is_completed = models.BooleanField(default=False, verbose_name='Is Completed')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    completed_at = models.DateTimeField(verbose_name='Completed At', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Customer Satisfaction'
        verbose_name_plural = 'Customer Satisfaction Surveys'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Survey for ticket #{self.ticket.ticket_number}"
    
    def get_average_rating(self):
        """Calculate average rating."""
        ratings = [r for r in [self.rating, self.agent_rating, self.resolution_rating, self.response_time_rating] if r]
        if not ratings:
            return 0
        return sum(ratings) / len(ratings)


class ContactMessage(models.Model):
    """
    Model for contact form messages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Contact information
    name = models.CharField(max_length=200, verbose_name='Name')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Phone', blank=True)
    
    # Message content
    subject = models.CharField(max_length=300, verbose_name='Subject')
    message = models.TextField(verbose_name='Message')
    department = models.CharField(max_length=100, verbose_name='Department', blank=True)
    
    # User association
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='contact_messages',
        null=True,
        blank=True,
        verbose_name='User'
    )
    
    # Tracking
    ip_address = models.GenericIPAddressField(verbose_name='IP Address', null=True, blank=True)
    is_read = models.BooleanField(default=False, verbose_name='Is Read')
    is_archived = models.BooleanField(default=False, verbose_name='Is Archived')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.name}"


class LiveChatSession(models.Model):
    """
    Model for live chat sessions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Session information
    session_id = models.CharField(max_length=100, unique=True, verbose_name='Session ID')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='live_chat_sessions',
        verbose_name='User'
    )
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='Last Activity')
    ended_at = models.DateTimeField(verbose_name='Ended At', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Live Chat Session'
        verbose_name_plural = 'Live Chat Sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"Session {self.session_id}"
    
    def get_message_count(self):
        """Get total number of messages in this session."""
        return self.messages.count()
    
    def get_unread_count(self, user):
        """Get number of unread messages for a user."""
        return self.messages.filter(is_read=False).exclude(user=user).count()


class LiveChatMessage(models.Model):
    """
    Model for live chat messages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Session
    session = models.ForeignKey(
        LiveChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Session'
    )
    
    # Content
    content = models.TextField(verbose_name='Content')
    
    # Senders
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='live_chat_messages',
        null=True,
        blank=True,
        verbose_name='User'
    )
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='admin_chat_messages',
        null=True,
        blank=True,
        verbose_name='Admin User'
    )
    
    # Flags
    is_admin = models.BooleanField(default=False, verbose_name='Is Admin')
    is_read = models.BooleanField(default=False, verbose_name='Is Read')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Live Chat Message'
        verbose_name_plural = 'Live Chat Messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message in {self.session.session_id}"
    
    def get_sender_name(self):
        """Get sender display name."""
        if self.is_admin and self.admin_user:
            return self.admin_user.get_full_name() or self.admin_user.username
        elif self.user:
            return self.user.get_full_name() or self.user.username
        return 'Unknown'
