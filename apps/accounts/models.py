"""
Account models for shop-template project.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import uuid


class UserManager(BaseUserManager):
    """Custom user manager for User model."""
    
    def create_user(self, phone_number=None, email=None, password=None, **extra_fields):
        """Create and save a regular user."""
        if not phone_number and not email:
            raise ValueError(_('Users must have a phone number or email address'))
        
        user = self.model(
            phone_number=phone_number,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number=None, email=None, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(phone_number, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with phone number and email support.
    """
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    USER_TYPES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
        ('operator', 'Operator'),
        ('writer', 'Writer'),
        ('support', 'Support'),
    ]
    
    id = models.AutoField(primary_key=True)
    username = models.CharField(_('Username'), max_length=100, unique=True, blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(
        _('Phone Number'),
        validators=[phone_regex],
        max_length=17,
        unique=True,
        null=True,
        blank=True
    )
    email = models.EmailField(_('Email Address'), unique=True, null=True, blank=True)
    first_name = models.CharField(_('First Name'), max_length=100, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=100, blank=True)
    full_name = models.CharField(_('Full Name'), max_length=200, blank=True)
    
    gender = models.CharField(_('Gender'), max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(_('Date of Birth'), null=True, blank=True)
    
    avatar = models.ImageField(upload_to='avatars/', verbose_name='Avatar', null=True, blank=True)
    
    # Address information
    address = models.TextField(_('Address'), blank=True)
    city = models.CharField(_('City'), max_length=100, blank=True)
    state = models.CharField(_('State'), max_length=100, blank=True)
    postal_code = models.CharField(_('Postal Code'), max_length=20, blank=True)
    country = models.CharField(_('Country'), max_length=100, default='Iran')
    
    # User type and status
    user_type = models.CharField(_('User Type'), max_length=20, choices=USER_TYPES, default='customer')
    is_active = models.BooleanField(_('Active'), default=True)
    is_staff = models.BooleanField(_('Staff'), default=False)
    is_verified = models.BooleanField(_('Verified'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    last_login = models.DateTimeField(verbose_name='Last Login', null=True, blank=True)
    
    # Social media
    facebook_url = models.URLField(verbose_name='Facebook URL', blank=True)
    twitter_url = models.URLField(verbose_name='Twitter URL', blank=True)
    instagram_url = models.URLField(verbose_name='Instagram URL', blank=True)
    
    # Preferences
    newsletter_subscribed = models.BooleanField(default=False, verbose_name='Newsletter Subscribed')
    preferred_language = models.CharField(max_length=10, default='fa', verbose_name='Preferred Language')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
        ]
    
    def __str__(self):
        if self.full_name:
            return self.full_name
        elif self.phone_number:
            return self.phone_number
        elif self.email:
            return self.email
        return f"User {self.id}"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name if self.first_name else str(self.id)
    
    def save(self, *args, **kwargs):
        """Save user and update full_name if first_name or last_name changed."""
        if self.first_name or self.last_name:
            self.full_name = self.get_full_name()
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate user data before saving."""
        if not self.phone_number and not self.email:
            raise ValidationError(_('Users must have a phone number or email address'))


class OTP(models.Model):
    """
    Model for storing One-Time Passwords for phone/email verification.
    """
    OTP_TYPES = [
        ('registration', 'Registration'),
        ('login', 'Login'),
        ('password_reset', 'Password Reset'),
        ('phone_verification', 'Phone Verification'),
        ('email_verification', 'Email Verification'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otps',
        verbose_name='User'
    )
    code = models.CharField(max_length=6, verbose_name='OTP Code')
    type = models.CharField(max_length=20, choices=OTP_TYPES, verbose_name='Type')
    phone_number = models.CharField(max_length=17, verbose_name='Phone Number', blank=True)
    email = models.EmailField(verbose_name='Email', blank=True)
    is_used = models.BooleanField(default=False, verbose_name='Is Used')
    expires_at = models.DateTimeField(verbose_name='Expires At')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['code']),
            models.Index(fields=['type']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.type} - {self.code} - {self.user}"
    
    def is_valid(self):
        """Check if OTP is still valid."""
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()


class UserAddress(models.Model):
    """
    Model for storing user addresses.
    """
    ADDRESS_TYPES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='User'
    )
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='home', verbose_name='Address Type')
    recipient_name = models.CharField(max_length=200, verbose_name='Recipient Name')
    phone_number = models.CharField(max_length=17, verbose_name='Phone Number')
    address_line_1 = models.CharField(max_length=255, verbose_name='Address Line 1')
    address_line_2 = models.CharField(max_length=255, verbose_name='Address Line 2', blank=True)
    city = models.CharField(max_length=100, verbose_name='City')
    state = models.CharField(max_length=100, verbose_name='State')
    postal_code = models.CharField(max_length=20, verbose_name='Postal Code')
    country = models.CharField(max_length=100, verbose_name='Country', default='Iran')
    is_default = models.BooleanField(default=False, verbose_name='Is Default')
    notes = models.TextField(verbose_name='Notes', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'User Address'
        verbose_name_plural = 'User Addresses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient_name} - {self.city}"
    
    def save(self, *args, **kwargs):
        """Ensure only one default address per user."""
        if self.is_default:
            UserAddress.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class UserWishlist(models.Model):
    """
    Model for storing user wishlist items.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        verbose_name='User'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        verbose_name='Product'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    
    class Meta:
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        ordering = ['-created_at']
        unique_together = [['user', 'product']]
    
    def __str__(self):
        return f"{self.user} - {self.product}"


class UserRole(models.Model):
    """
    Model for defining custom roles with permissions.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='Role Name')
    description = models.TextField(verbose_name='Description', blank=True)
    permissions = models.JSONField(verbose_name='Permissions', default=list)
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserPermission(models.Model):
    """
    Model for assigning custom permissions to users or roles.
    """
    PERMISSION_TYPES = [
        ('view', 'View'),
        ('add', 'Add'),
        ('change', 'Change'),
        ('delete', 'Delete'),
        ('manage', 'Manage'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name='Permission Name')
    codename = models.CharField(max_length=100, unique=True, verbose_name='Codename')
    model = models.CharField(max_length=100, verbose_name='Model', blank=True)
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES, verbose_name='Permission Type')
    description = models.TextField(verbose_name='Description', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    class Meta:
        verbose_name = 'User Permission'
        verbose_name_plural = 'User Permissions'
        ordering = ['codename']
    
    def __str__(self):
        return f"{self.name} ({self.codename})"
