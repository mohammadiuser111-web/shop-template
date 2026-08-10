"""
Dashboard admin models for shop-template project.
"""
from django.db import models
from django.conf import settings
import uuid


class AdminDashboard(models.Model):
    """
    Model for customizing admin dashboard.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    code = models.CharField(max_length=100, unique=True, verbose_name='Code')
    description = models.TextField(verbose_name='Description', blank=True)
    
    # Layout
    layout = models.JSONField(
        verbose_name='Layout Configuration',
        default=dict,
        help_text='JSON configuration for dashboard layout (widgets, columns, etc.)'
    )
    
    # Default dashboard
    is_default = models.BooleanField(default=False, verbose_name='Is Default')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Admin Dashboard'
        verbose_name_plural = 'Admin Dashboards'
        ordering = ['is_default', '-created_at']
    
    def __str__(self):
        return self.name


class DashboardWidget(models.Model):
    """
    Model for dashboard widgets.
    """
    WIDGET_TYPES = [
        ('chart', 'Chart'),
        ('statistic', 'Statistic'),
        ('list', 'List'),
        ('card', 'Card'),
        ('custom', 'Custom'),
    ]
    
    CHART_TYPES = [
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('doughnut', 'Doughnut Chart'),
        ('polar', 'Polar Area Chart'),
        ('radar', 'Radar Chart'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    code = models.CharField(max_length=100, unique=True, verbose_name='Code')
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, verbose_name='Widget Type')
    
    # Chart-specific fields
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, blank=True, verbose_name='Chart Type')
    
    # Configuration
    config = models.JSONField(
        verbose_name='Configuration',
        default=dict,
        help_text='JSON configuration for the widget'
    )
    
    # Display
    title = models.CharField(max_length=200, verbose_name='Title')
    icon = models.CharField(max_length=50, verbose_name='Icon', blank=True)
    color = models.CharField(max_length=20, verbose_name='Color', blank=True)
    
    # Size
    width = models.CharField(
        max_length=10,
        choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('6', '6'), ('12', '12')],
        default='4',
        verbose_name='Width'
    )
    height = models.CharField(
        max_length=10,
        choices=[('auto', 'Auto'), ('100', '100px'), ('200', '200px'), ('300', '300px')],
        default='auto',
        verbose_name='Height'
    )
    
    # Position
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Dashboard Widget'
        verbose_name_plural = 'Dashboard Widgets'
        ordering = ['sort_order']
    
    def __str__(self):
        return self.name


class AdminMenu(models.Model):
    """
    Model for customizing admin menu.
    """
    MENU_TYPES = [
        ('sidebar', 'Sidebar'),
        ('topbar', 'Top Bar'),
        ('footer', 'Footer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    menu_type = models.CharField(max_length=20, choices=MENU_TYPES, verbose_name='Menu Type')
    
    # Menu items
    items = models.JSONField(
        verbose_name='Menu Items',
        default=list,
        help_text='JSON array of menu items with their properties'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Admin Menu'
        verbose_name_plural = 'Admin Menus'
        ordering = ['menu_type', 'sort_order']
    
    def __str__(self):
        return f"{self.name} ({self.get_menu_type_display()})"


class AdminMenuItem(models.Model):
    """
    Model for admin menu items.
    """
    ITEM_TYPES = [
        ('link', 'Link'),
        ('dropdown', 'Dropdown'),
        ('divider', 'Divider'),
        ('header', 'Header'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu = models.ForeignKey(
        AdminMenu,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Admin Menu'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
        verbose_name='Parent Item'
    )
    
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, verbose_name='Item Type')
    
    # Display
    title = models.CharField(max_length=200, verbose_name='Title')
    icon = models.CharField(max_length=50, verbose_name='Icon', blank=True)
    color = models.CharField(max_length=20, verbose_name='Color', blank=True)
    
    # Link
    url = models.CharField(max_length=500, verbose_name='URL', blank=True)
    target = models.CharField(max_length=10, verbose_name='Target', blank=True)
    
    # Permissions
    required_permission = models.CharField(max_length=100, verbose_name='Required Permission', blank=True)
    
    # Visibility
    is_visible = models.BooleanField(default=True, verbose_name='Is Visible')
    
    # Position
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Admin Menu Item'
        verbose_name_plural = 'Admin Menu Items'
        ordering = ['parent__sort_order', 'sort_order']
    
    def __str__(self):
        return self.title


class AdminQuickAction(models.Model):
    """
    Model for admin quick actions (shortcuts).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name='Name')
    code = models.CharField(max_length=100, unique=True, verbose_name='Code')
    
    # Action
    action_type = models.CharField(max_length=50, verbose_name='Action Type')
    action_config = models.JSONField(
        verbose_name='Action Configuration',
        default=dict,
        help_text='JSON configuration for the action'
    )
    
    # Display
    title = models.CharField(max_length=200, verbose_name='Title')
    icon = models.CharField(max_length=50, verbose_name='Icon', blank=True)
    color = models.CharField(max_length=20, verbose_name='Color', blank=True)
    
    # Permissions
    required_permission = models.CharField(max_length=100, verbose_name='Required Permission', blank=True)
    
    # Position
    sort_order = models.IntegerField(default=0, verbose_name='Sort Order')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Admin Quick Action'
        verbose_name_plural = 'Admin Quick Actions'
        ordering = ['sort_order']
    
    def __str__(self):
        return self.title


class AdminSettings(models.Model):
    """
    Model for admin panel settings.
    """
    SINGLETONE = True
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Branding
    logo = models.ImageField(upload_to='admin/', verbose_name='Logo', null=True, blank=True)
    logo_small = models.ImageField(upload_to='admin/', verbose_name='Small Logo', null=True, blank=True)
    favicon = models.ImageField(upload_to='admin/', verbose_name='Favicon', null=True, blank=True)
    
    # Theme
    theme_color = models.CharField(max_length=20, default='#2563eb', verbose_name='Theme Color')
    sidebar_color = models.CharField(max_length=20, default='#1e293b', verbose_name='Sidebar Color')
    sidebar_text_color = models.CharField(max_length=20, default='#ffffff', verbose_name='Sidebar Text Color')
    
    # Layout
    sidebar_collapsed = models.BooleanField(default=False, verbose_name='Sidebar Collapsed')
    layout = models.CharField(
        max_length=20,
        choices=[('fixed', 'Fixed'), ('fluid', 'Fluid')],
        default='fluid',
        verbose_name='Layout'
    )
    
    # Language
    language = models.CharField(max_length=10, default='fa', verbose_name='Language')
    
    # Notifications
    show_notifications = models.BooleanField(default=True, verbose_name='Show Notifications')
    
    # Dashboard
    default_dashboard = models.ForeignKey(
        AdminDashboard,
        on_delete=models.SET_NULL,
        related_name='default_settings',
        null=True,
        blank=True,
        verbose_name='Default Dashboard'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Admin Settings'
        verbose_name_plural = 'Admin Settings'
    
    def __str__(self):
        return 'Admin Settings'
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)."""
        if self.SINGLETONE:
            self.pk = 1
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance."""
        return cls.objects.first()


class AdminUserSettings(models.Model):
    """
    Model for individual admin user settings.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_settings',
        verbose_name='User'
    )
    
    # Theme
    theme = models.CharField(
        max_length=20,
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='auto',
        verbose_name='Theme'
    )
    
    # Language
    language = models.CharField(max_length=10, default='fa', verbose_name='Language')
    
    # Layout
    sidebar_collapsed = models.BooleanField(default=False, verbose_name='Sidebar Collapsed')
    
    # Notifications
    email_notifications = models.BooleanField(default=True, verbose_name='Email Notifications')
    push_notifications = models.BooleanField(default=True, verbose_name='Push Notifications')
    
    # Dashboard
    dashboard = models.ForeignKey(
        AdminDashboard,
        on_delete=models.SET_NULL,
        related_name='user_settings',
        null=True,
        blank=True,
        verbose_name='Dashboard'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'Admin User Settings'
        verbose_name_plural = 'Admin User Settings'
    
    def __str__(self):
        return f"Settings for {self.user}"


class AdminActivity(models.Model):
    """
    Model for tracking admin user activities.
    """
    ACTION_TYPES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='admin_activities',
        null=True,
        blank=True,
        verbose_name='User'
    )
    action = models.CharField(max_length=20, choices=ACTION_TYPES, verbose_name='Action')
    model_name = models.CharField(max_length=100, verbose_name='Model Name', blank=True)
    object_id = models.PositiveIntegerField(verbose_name='Object ID', null=True, blank=True)
    object_repr = models.CharField(max_length=200, verbose_name='Object Representation', blank=True)
    
    # Details
    description = models.TextField(verbose_name='Description', blank=True)
    changes = models.JSONField(verbose_name='Changes', default=dict, blank=True)
    
    # Context
    ip_address = models.GenericIPAddressField(verbose_name='IP Address', null=True, blank=True)
    user_agent = models.TextField(verbose_name='User Agent', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Admin Activity'
        verbose_name_plural = 'Admin Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['model_name']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.model_name} - {self.created_at}"
