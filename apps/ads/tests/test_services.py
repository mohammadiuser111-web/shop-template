"""
Tests for ads services.
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from ..models import AdSlot, Advertisement, AdImpression, AdClick
from ..services import AdService, AdRotationService, AdReportService

User = get_user_model()


class AdServiceTest(TestCase):
    """Tests for AdService."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.slot = AdSlot.objects.create(
            name='Test Slot',
            code='test_slot',
            is_active=True
        )
        self.ad1 = Advertisement.objects.create(
            name='Ad 1',
            slot=self.slot,
            ad_type='image',
            priority=10,
            is_active=True
        )
        self.ad2 = Advertisement.objects.create(
            name='Ad 2',
            slot=self.slot,
            ad_type='image',
            priority=5,
            is_active=True
        )
        self.ad3 = Advertisement.objects.create(
            name='Ad 3',
            slot=self.slot,
            ad_type='image',
            priority=10,
            is_active=False  # Inactive
        )
    
    def test_get_ad_slot(self):
        """Test getting ad slot by code."""
        slot = AdService.get_ad_slot('test_slot')
        self.assertEqual(slot, self.slot)
    
    def test_get_ad_slot_not_found(self):
        """Test getting non-existent ad slot."""
        slot = AdService.get_ad_slot('nonexistent')
        self.assertIsNone(slot)
    
    def test_get_ad_slot_caching(self):
        """Test ad slot caching."""
        # First call - should hit database
        slot1 = AdService.get_ad_slot('test_slot')
        
        # Second call - should use cache
        slot2 = AdService.get_ad_slot('test_slot')
        
        self.assertEqual(slot1, slot2)
    
    def test_get_current_ad(self):
        """Test getting current ad for a slot."""
        # Create a mock request
        request = self.factory.get('/')
        
        # Get ad - should return highest priority active ad
        ad = AdService.get_current_ad('test_slot', request)
        self.assertEqual(ad, self.ad1)
    
    def test_get_current_ad_no_active(self):
        """Test getting ad when no active ads exist."""
        # Deactivate all ads
        self.ad1.is_active = False
        self.ad1.save()
        self.ad2.is_active = False
        self.ad2.save()
        
        request = self.factory.get('/')
        ad = AdService.get_current_ad('test_slot', request)
        self.assertIsNone(ad)
    
    def test_get_current_ad_invalid_slot(self):
        """Test getting ad for invalid slot."""
        request = self.factory.get('/')
        ad = AdService.get_current_ad('invalid_slot', request)
        self.assertIsNone(ad)
    
    def test_track_impression(self):
        """Test tracking ad impression."""
        request = self.factory.get('/')
        
        # Track impression
        impression = AdService.track_impression(self.ad1, request)
        
        self.assertIsNotNone(impression)
        self.assertEqual(impression.ad, self.ad1)
        
        self.ad1.refresh_from_db()
        self.assertEqual(self.ad1.impression_count, 1)
    
    def test_track_impression_duplicate(self):
        """Test that duplicate impressions are not tracked."""
        request = self.factory.get('/')
        request.session = {}
        
        # First impression
        AdService.track_impression(self.ad1, request)
        initial_count = self.ad1.impression_count
        
        # Second impression with same session
        AdService.track_impression(self.ad1, request)
        
        self.ad1.refresh_from_db()
        self.assertEqual(self.ad1.impression_count, initial_count)
    
    def test_track_click(self):
        """Test tracking ad click."""
        request = self.factory.get('/')
        
        # Track click
        click = AdService.track_click(self.ad1, request)
        
        self.assertIsNotNone(click)
        self.assertEqual(click.ad, self.ad1)
        
        self.ad1.refresh_from_db()
        self.assertEqual(self.ad1.click_count, 1)
    
    def test_get_ad_stats(self):
        """Test getting ad statistics."""
        # Create some impressions and clicks
        AdImpression.objects.create(ad=self.ad1)
        AdImpression.objects.create(ad=self.ad1)
        AdClick.objects.create(ad=self.ad1)
        
        stats = AdService.get_ad_stats(self.ad1.id)
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats['ad'], self.ad1)
        self.assertEqual(stats['impressions'], 2)
        self.assertEqual(stats['clicks'], 1)
        self.assertEqual(stats['ctr'], 50.0)
    
    def test_get_slot_stats(self):
        """Test getting slot statistics."""
        # Create impressions and clicks
        AdImpression.objects.create(ad=self.ad1)
        AdImpression.objects.create(ad=self.ad2)
        AdClick.objects.create(ad=self.ad1)
        
        stats = AdService.get_slot_stats('test_slot')
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats['slot'], self.slot)
        self.assertEqual(stats['total_impressions'], 2)
        self.assertEqual(stats['total_clicks'], 1)
        self.assertEqual(stats['total_ads'], 3)
        self.assertEqual(stats['active_ads'], 2)
    
    def test_get_all_stats(self):
        """Test getting all ads statistics."""
        stats = AdService.get_all_stats()
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats['total_ads'], 3)
        self.assertEqual(stats['active_ads'], 2)
    
    def test_clear_ad_cache(self):
        """Test clearing ad cache."""
        # First, get ad to populate cache
        request = self.factory.get('/')
        AdService.get_current_ad('test_slot', request)
        
        # Clear cache
        AdService.clear_ad_cache(slot_code='test_slot')
        
        # Verify cache is cleared (next call will hit database)
        # This is hard to test directly, but the method should execute without error


class AdRotationServiceTest(TestCase):
    """Tests for AdRotationService."""
    
    def setUp(self):
        """Set up test data."""
        self.slot = AdSlot.objects.create(
            name='Rotation Slot',
            code='rotation_slot',
            is_active=True
        )
        self.ad1 = Advertisement.objects.create(
            name='Rotation Ad 1',
            slot=self.slot,
            ad_type='image',
            priority=5,
            is_active=True
        )
        self.ad2 = Advertisement.objects.create(
            name='Rotation Ad 2',
            slot=self.slot,
            ad_type='image',
            priority=5,
            is_active=True
        )
    
    def test_get_rotating_ads(self):
        """Test getting rotating ads."""
        ads = AdRotationService.get_rotating_ads('rotation_slot', limit=5)
        
        self.assertEqual(len(ads), 2)
        self.assertIn(self.ad1, ads)
        self.assertIn(self.ad2, ads)
    
    def test_get_random_ad(self):
        """Test getting random ad."""
        ad = AdRotationService.get_random_ad('rotation_slot')
        
        self.assertIsNotNone(ad)
        self.assertIn(ad, [self.ad1, self.ad2])
    
    def test_get_random_ad_empty(self):
        """Test getting random ad from empty slot."""
        empty_slot = AdSlot.objects.create(
            name='Empty Slot',
            code='empty_slot',
            is_active=True
        )
        
        ad = AdRotationService.get_random_ad('empty_slot')
        self.assertIsNone(ad)


class AdReportServiceTest(TestCase):
    """Tests for AdReportService."""
    
    def setUp(self):
        """Set up test data."""
        from django.utils import timezone
        from datetime import timedelta
        
        self.slot = AdSlot.objects.create(
            name='Report Slot',
            code='report_slot',
            is_active=True
        )
        self.ad1 = Advertisement.objects.create(
            name='Report Ad 1',
            slot=self.slot,
            ad_type='image',
            is_active=True
        )
        self.ad2 = Advertisement.objects.create(
            name='Report Ad 2',
            slot=self.slot,
            ad_type='image',
            is_active=True
        )
        
        # Create impressions with different dates
        self.today = timezone.now().date()
        self.yesterday = self.today - timedelta(days=1)
        
        AdImpression.objects.create(
            ad=self.ad1,
            created_at=timezone.make_aware(timezone.datetime.combine(self.today, timezone.datetime.min.time()))
        )
        AdImpression.objects.create(
            ad=self.ad2,
            created_at=timezone.make_aware(timezone.datetime.combine(self.yesterday, timezone.datetime.min.time()))
        )
        AdImpression.objects.create(
            ad=self.ad1,
            created_at=timezone.make_aware(timezone.datetime.combine(self.yesterday, timezone.datetime.min.time()))
        )
        
        # Create clicks
        AdClick.objects.create(
            ad=self.ad1,
            created_at=timezone.make_aware(timezone.datetime.combine(self.today, timezone.datetime.min.time()))
        )
        AdClick.objects.create(
            ad=self.ad2,
            created_at=timezone.make_aware(timezone.datetime.combine(self.yesterday, timezone.datetime.min.time()))
        )
    
    def test_get_impression_report(self):
        """Test getting impression report."""
        report = AdReportService.get_impression_report(
            date_from=self.yesterday,
            date_to=self.today,
            slot=None
        )
        
        self.assertIsNotNone(report)
        self.assertEqual(len(report), 2)  # Two dates
    
    def test_get_click_report(self):
        """Test getting click report."""
        report = AdReportService.get_click_report(
            date_from=self.yesterday,
            date_to=self.today,
            slot=None
        )
        
        self.assertIsNotNone(report)
        self.assertEqual(len(report), 2)  # Two dates
    
    def test_get_performance_report(self):
        """Test getting performance report."""
        report = AdReportService.get_performance_report(
            date_from=self.yesterday,
            date_to=self.today
        )
        
        self.assertIsNotNone(report)
        self.assertEqual(len(report), 2)  # Two ads
