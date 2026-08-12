"""
Tests for ads models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import AdSlot, Advertisement, AdImpression, AdClick
import uuid

User = get_user_model()


class AdSlotModelTest(TestCase):
    """Tests for AdSlot model."""
    
    def setUp(self):
        """Set up test data."""
        self.slot = AdSlot.objects.create(
            name='Test Slot',
            code='test_slot',
            description='Test description',
            width=300,
            height=250,
            is_responsive=False,
            is_active=True
        )
    
    def test_ad_slot_creation(self):
        """Test ad slot creation."""
        self.assertEqual(self.slot.name, 'Test Slot')
        self.assertEqual(self.slot.code, 'test_slot')
        self.assertEqual(self.slot.description, 'Test description')
        self.assertEqual(self.slot.width, 300)
        self.assertEqual(self.slot.height, 250)
        self.assertFalse(self.slot.is_responsive)
        self.assertTrue(self.slot.is_active)
        self.assertIsNotNone(self.slot.id)
        self.assertIsInstance(self.slot.id, uuid.UUID)
    
    def test_ad_slot_str(self):
        """Test ad slot string representation."""
        self.assertEqual(str(self.slot), 'Test Slot (test_slot)')
    
    def test_ad_slot_unique_code(self):
        """Test that ad slot code must be unique."""
        with self.assertRaises(Exception):
            AdSlot.objects.create(
                name='Another Slot',
                code='test_slot',  # Same code as self.slot
                is_active=True
            )
    
    def test_ad_slot_responsive(self):
        """Test responsive ad slot."""
        responsive_slot = AdSlot.objects.create(
            name='Responsive Slot',
            code='responsive_slot',
            is_responsive=True
        )
        self.assertTrue(responsive_slot.is_responsive)


class AdvertisementModelTest(TestCase):
    """Tests for Advertisement model."""
    
    def setUp(self):
        """Set up test data."""
        self.slot = AdSlot.objects.create(
            name='Test Slot',
            code='test_slot',
            is_active=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.ad = Advertisement.objects.create(
            name='Test Ad',
            slot=self.slot,
            ad_type='image',
            title='Test Title',
            description='Test description',
            priority=5,
            url='https://example.com',
            target='_blank',
            is_active=True,
            created_by=self.user
        )
    
    def test_advertisement_creation(self):
        """Test advertisement creation."""
        self.assertEqual(self.ad.name, 'Test Ad')
        self.assertEqual(self.ad.slot, self.slot)
        self.assertEqual(self.ad.ad_type, 'image')
        self.assertEqual(self.ad.title, 'Test Title')
        self.assertEqual(self.ad.description, 'Test description')
        self.assertEqual(self.ad.priority, 5)
        self.assertEqual(self.ad.url, 'https://example.com')
        self.assertEqual(self.ad.target, '_blank')
        self.assertTrue(self.ad.is_active)
        self.assertEqual(self.ad.created_by, self.user)
        self.assertEqual(self.ad.impression_count, 0)
        self.assertEqual(self.ad.click_count, 0)
    
    def test_advertisement_str(self):
        """Test advertisement string representation."""
        self.assertEqual(str(self.ad), 'Test Ad')
    
    def test_advertisement_get_ctr(self):
        """Test CTR calculation."""
        # Initially 0
        self.assertEqual(self.ad.get_ctr(), 0)
        
        # Update counts
        self.ad.impression_count = 100
        self.ad.click_count = 10
        self.ad.save()
        
        self.assertEqual(self.ad.get_ctr(), 10.0)
    
    def test_advertisement_is_valid(self):
        """Test validity check."""
        # Active ad with no date constraints
        self.assertTrue(self.ad.is_valid())
        
        # Inactive ad
        self.ad.is_active = False
        self.ad.save()
        self.assertFalse(self.ad.is_valid())
        
        # Active ad with future start date
        from django.utils import timezone
        from datetime import timedelta
        
        self.ad.is_active = True
        self.ad.start_date = timezone.now() + timedelta(days=1)
        self.ad.save()
        self.assertFalse(self.ad.is_valid())
        
        # Active ad with past end date
        self.ad.start_date = None
        self.ad.end_date = timezone.now() - timedelta(days=1)
        self.ad.save()
        self.assertFalse(self.ad.is_valid())
    
    def test_advertisement_increment_impressions(self):
        """Test impression increment."""
        self.ad.increment_impressions()
        self.assertEqual(self.ad.impression_count, 1)
        
        self.ad.increment_impressions()
        self.assertEqual(self.ad.impression_count, 2)
    
    def test_advertisement_increment_clicks(self):
        """Test click increment."""
        self.ad.increment_clicks()
        self.assertEqual(self.ad.click_count, 1)
        
        self.ad.increment_clicks()
        self.assertEqual(self.ad.click_count, 2)
    
    def test_advertisement_get_ad_type_display(self):
        """Test ad type display."""
        self.assertEqual(self.ad.get_ad_type_display(), 'Image')
        
        self.ad.ad_type = 'html'
        self.assertEqual(self.ad.get_ad_type_display(), 'HTML')
        
        self.ad.ad_type = 'script'
        self.assertEqual(self.ad.get_ad_type_display(), 'JavaScript')
        
        self.ad.ad_type = 'video'
        self.assertEqual(self.ad.get_ad_type_display(), 'Video')


class AdImpressionModelTest(TestCase):
    """Tests for AdImpression model."""
    
    def setUp(self):
        """Set up test data."""
        self.slot = AdSlot.objects.create(
            name='Test Slot',
            code='test_slot',
            is_active=True
        )
        self.ad = Advertisement.objects.create(
            name='Test Ad',
            slot=self.slot,
            ad_type='image',
            is_active=True
        )
        self.impression = AdImpression.objects.create(
            ad=self.ad,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            referrer='https://example.com'
        )
    
    def test_ad_impression_creation(self):
        """Test ad impression creation."""
        self.assertEqual(self.impression.ad, self.ad)
        self.assertEqual(self.impression.ip_address, '192.168.1.1')
        self.assertEqual(self.impression.user_agent, 'Mozilla/5.0')
        self.assertEqual(self.impression.referrer, 'https://example.com')
        self.assertIsNotNone(self.impression.id)
        self.assertIsInstance(self.impression.id, uuid.UUID)
    
    def test_ad_impression_str(self):
        """Test ad impression string representation."""
        self.assertEqual(str(self.impression), f"Impression for {self.ad.name}")


class AdClickModelTest(TestCase):
    """Tests for AdClick model."""
    
    def setUp(self):
        """Set up test data."""
        self.slot = AdSlot.objects.create(
            name='Test Slot',
            code='test_slot',
            is_active=True
        )
        self.ad = Advertisement.objects.create(
            name='Test Ad',
            slot=self.slot,
            ad_type='image',
            is_active=True
        )
        self.impression = AdImpression.objects.create(
            ad=self.ad,
            ip_address='192.168.1.1'
        )
        self.click = AdClick.objects.create(
            ad=self.ad,
            impression=self.impression,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            referrer='https://example.com'
        )
    
    def test_ad_click_creation(self):
        """Test ad click creation."""
        self.assertEqual(self.click.ad, self.ad)
        self.assertEqual(self.click.impression, self.impression)
        self.assertEqual(self.click.ip_address, '192.168.1.1')
        self.assertEqual(self.click.user_agent, 'Mozilla/5.0')
        self.assertEqual(self.click.referrer, 'https://example.com')
        self.assertIsNotNone(self.click.id)
        self.assertIsInstance(self.click.id, uuid.UUID)
    
    def test_ad_click_str(self):
        """Test ad click string representation."""
        self.assertEqual(str(self.click), f"Click for {self.ad.name}")
    
    def test_ad_click_without_impression(self):
        """Test ad click without impression."""
        click = AdClick.objects.create(
            ad=self.ad,
            ip_address='192.168.1.2',
            user_agent='Mozilla/5.0'
        )
        self.assertEqual(click.ad, self.ad)
        self.assertIsNone(click.impression)
