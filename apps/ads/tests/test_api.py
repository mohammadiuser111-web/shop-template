"""
Tests for ads API.
"""
from django.test import TestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import AdSlot, Advertisement

User = get_user_model()


class AdSlotAPITest(TestCase):
    """Tests for ad slot API."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.force_authenticate(user=self.admin)
        
        self.slot = AdSlot.objects.create(
            name='API Test Slot',
            code='api_test_slot',
            description='API test description',
            width=300,
            height=250,
            is_active=True
        )
    
    def test_list_ad_slots(self):
        """Test listing ad slots."""
        url = reverse('ads_api:ad_slot_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'API Test Slot')
    
    def test_create_ad_slot(self):
        """Test creating ad slot."""
        url = reverse('ads_api:ad_slot_list_create')
        data = {
            'name': 'New API Slot',
            'code': 'new_api_slot',
            'description': 'New API description',
            'width': 400,
            'height': 300,
            'is_responsive': False,
            'is_active': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(AdSlot.objects.filter(code='new_api_slot').exists())
    
    def test_retrieve_ad_slot(self):
        """Test retrieving ad slot."""
        url = reverse('ads_api:ad_slot_detail', args=[self.slot.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'API Test Slot')
        self.assertEqual(response.data['code'], 'api_test_slot')
    
    def test_update_ad_slot(self):
        """Test updating ad slot."""
        url = reverse('ads_api:ad_slot_detail', args=[self.slot.id])
        data = {
            'name': 'Updated API Slot',
            'code': self.slot.code,
            'description': 'Updated description',
            'width': 500,
            'height': 400,
            'is_responsive': True,
            'is_active': True
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.name, 'Updated API Slot')
        self.assertEqual(self.slot.width, 500)
    
    def test_delete_ad_slot(self):
        """Test deleting ad slot."""
        url = reverse('ads_api:ad_slot_detail', args=[self.slot.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 204)
        self.assertFalse(AdSlot.objects.filter(id=self.slot.id).exists())


class AdvertisementAPITest(TestCase):
    """Tests for advertisement API."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.force_authenticate(user=self.admin)
        
        self.slot = AdSlot.objects.create(
            name='API Slot',
            code='api_slot',
            is_active=True
        )
        self.ad = Advertisement.objects.create(
            name='API Ad',
            slot=self.slot,
            ad_type='html',
            html_content='<div>API Content</div>',
            title='API Title',
            description='API description',
            priority=5,
            url='https://example.com/api',
            target='_blank',
            is_active=True,
            created_by=self.admin
        )
    
    def test_list_advertisements(self):
        """Test listing advertisements."""
        url = reverse('ads_api:advertisement_list_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'API Ad')
    
    def test_create_advertisement(self):
        """Test creating advertisement."""
        url = reverse('ads_api:advertisement_list_create')
        data = {
            'name': 'New API Ad',
            'slot_id': str(self.slot.id),
            'ad_type': 'image',
            'title': 'New API Title',
            'description': 'New API description',
            'priority': 10,
            'url': 'https://example.com/new-api',
            'target': '_blank',
            'is_active': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Advertisement.objects.filter(name='New API Ad').exists())
    
    def test_retrieve_advertisement(self):
        """Test retrieving advertisement."""
        url = reverse('ads_api:advertisement_detail', args=[self.ad.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'API Ad')
        self.assertEqual(response.data['title'], 'API Title')
    
    def test_update_advertisement(self):
        """Test updating advertisement."""
        url = reverse('ads_api:advertisement_detail', args=[self.ad.id])
        data = {
            'name': 'Updated API Ad',
            'slot_id': str(self.slot.id),
            'ad_type': self.ad.ad_type,
            'title': 'Updated API Title',
            'description': 'Updated API description',
            'priority': 10,
            'url': self.ad.url,
            'target': self.ad.target,
            'is_active': True
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.name, 'Updated API Ad')
        self.assertEqual(self.ad.title, 'Updated API Title')
    
    def test_delete_advertisement(self):
        """Test deleting advertisement."""
        url = reverse('ads_api:advertisement_detail', args=[self.ad.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Advertisement.objects.filter(id=self.ad.id).exists())


class AdDisplayAPITest(TestCase):
    """Tests for ad display API."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.slot = AdSlot.objects.create(
            name='Display Slot',
            code='display_slot',
            is_active=True
        )
        self.ad = Advertisement.objects.create(
            name='Display Ad',
            slot=self.slot,
            ad_type='html',
            html_content='<div>Display Content</div>',
            title='Display Title',
            is_active=True
        )
    
    def test_display_ad(self):
        """Test displaying ad."""
        url = reverse('ads_api:ad_display', args=['display_slot'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Display Ad')
        self.assertEqual(response.data['html_content'], '<div>Display Content</div>')
    
    def test_display_ad_not_found(self):
        """Test displaying ad from non-existent slot."""
        url = reverse('ads_api:ad_display', args=['nonexistent_slot'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)


class AdTrackingAPITest(TestCase):
    """Tests for ad tracking API."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.slot = AdSlot.objects.create(
            name='Tracking Slot',
            code='tracking_slot',
            is_active=True
        )
        self.ad = Advertisement.objects.create(
            name='Tracking Ad',
            slot=self.slot,
            ad_type='html',
            html_content='<div>Tracking Content</div>',
            is_active=True
        )
    
    def test_track_impression(self):
        """Test tracking impression."""
        url = reverse('ads_api:ad_impression_track', args=[self.ad.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 201)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.impression_count, 1)
    
    def test_track_click(self):
        """Test tracking click."""
        url = reverse('ads_api:ad_click_track', args=[self.ad.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 201)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.click_count, 1)


class AdStatsAPITest(TestCase):
    """Tests for ad statistics API."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.force_authenticate(user=self.admin)
        
        self.slot = AdSlot.objects.create(
            name='Stats Slot',
            code='stats_slot',
            is_active=True
        )
        self.ad = Advertisement.objects.create(
            name='Stats Ad',
            slot=self.slot,
            ad_type='html',
            html_content='<div>Stats Content</div>',
            is_active=True
        )
        
        # Create some impressions and clicks
        from ..models import AdImpression, AdClick
        AdImpression.objects.create(ad=self.ad)
        AdImpression.objects.create(ad=self.ad)
        AdClick.objects.create(ad=self.ad)
    
    def test_get_ad_stats(self):
        """Test getting ad stats."""
        url = reverse('ads_api:advertisement_stats', args=[self.ad.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Stats Ad')
        self.assertEqual(response.data['impression_count'], 2)
        self.assertEqual(response.data['click_count'], 1)
        self.assertEqual(response.data['ctr'], 50.0)
    
    def test_get_slot_stats(self):
        """Test getting slot stats."""
        url = reverse('ads_api:ad_slot_stats', args=['stats_slot'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Stats Slot')
        self.assertEqual(response.data['code'], 'stats_slot')
        self.assertEqual(response.data['total_impressions'], 2)
        self.assertEqual(response.data['total_clicks'], 1)
    
    def test_get_overall_stats(self):
        """Test getting overall stats."""
        url = reverse('ads_api:ads_overall_stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_ads'], 1)
        self.assertEqual(response.data['active_ads'], 1)
        self.assertEqual(response.data['total_impressions'], 2)
        self.assertEqual(response.data['total_clicks'], 1)


class AdReportAPITest(TestCase):
    """Tests for ad report API."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.force_authenticate(user=self.admin)
        
        self.slot = AdSlot.objects.create(
            name='Report Slot',
            code='report_slot',
            is_active=True
        )
        self.ad = Advertisement.objects.create(
            name='Report Ad',
            slot=self.slot,
            ad_type='html',
            is_active=True
        )
        
        # Create impressions and clicks
        from django.utils import timezone
        from datetime import timedelta
        from ..models import AdImpression, AdClick
        
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        AdImpression.objects.create(
            ad=self.ad,
            created_at=timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
        )
        AdImpression.objects.create(
            ad=self.ad,
            created_at=timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time()))
        )
        AdClick.objects.create(
            ad=self.ad,
            created_at=timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
        )
    
    def test_impression_report(self):
        """Test impression report."""
        url = reverse('ads_api:impression_report')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)  # Two dates
    
    def test_click_report(self):
        """Test click report."""
        url = reverse('ads_api:click_report')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # One date with clicks
    
    def test_performance_report(self):
        """Test performance report."""
        url = reverse('ads_api:performance_report')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # One ad
        self.assertEqual(response.data[0]['name'], 'Report Ad')
