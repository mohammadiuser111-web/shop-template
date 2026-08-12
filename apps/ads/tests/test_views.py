"""
Tests for ads views.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import AdSlot, Advertisement

User = get_user_model()


class AdSlotViewsTest(TestCase):
    """Tests for ad slot views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.force_login(self.admin)
        
        self.slot = AdSlot.objects.create(
            name='Test Slot',
            code='test_slot',
            description='Test description',
            width=300,
            height=250,
            is_active=True
        )
    
    def test_ad_slot_list_view(self):
        """Test ad slot list view."""
        url = reverse('ads:ad_slot_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Slot')
        self.assertContains(response, 'test_slot')
    
    def test_ad_slot_create_view(self):
        """Test ad slot create view."""
        url = reverse('ads:ad_slot_create')
        data = {
            'name': 'New Slot',
            'code': 'new_slot',
            'description': 'New description',
            'width': 200,
            'height': 150,
            'is_responsive': False,
            'is_active': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(AdSlot.objects.filter(code='new_slot').exists())
    
    def test_ad_slot_edit_view(self):
        """Test ad slot edit view."""
        url = reverse('ads:ad_slot_edit', args=[self.slot.id])
        data = {
            'name': 'Updated Slot',
            'code': self.slot.code,
            'description': 'Updated description',
            'width': 400,
            'height': 300,
            'is_responsive': True,
            'is_active': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.name, 'Updated Slot')
        self.assertEqual(self.slot.description, 'Updated description')
        self.assertEqual(self.slot.width, 400)
        self.assertTrue(self.slot.is_responsive)
    
    def test_ad_slot_delete_view(self):
        """Test ad slot delete view."""
        # First create an ad in the slot
        ad = Advertisement.objects.create(
            name='Test Ad',
            slot=self.slot,
            ad_type='image',
            is_active=True
        )
        
        url = reverse('ads:ad_slot_delete', args=[self.slot.id])
        response = self.client.post(url)
        
        # Should not delete because slot has ads
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AdSlot.objects.filter(id=self.slot.id).exists())
        
        # Delete the ad first
        ad.delete()
        
        # Now delete the slot
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(AdSlot.objects.filter(id=self.slot.id).exists())


class AdvertisementViewsTest(TestCase):
    """Tests for advertisement views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.force_login(self.admin)
        
        self.slot = AdSlot.objects.create(
            name='Test Slot',
            code='test_slot',
            is_active=True
        )
        self.ad = Advertisement.objects.create(
            name='Test Ad',
            slot=self.slot,
            ad_type='image',
            title='Test Title',
            description='Test description',
            priority=5,
            url='https://example.com',
            is_active=True,
            created_by=self.admin
        )
    
    def test_ad_list_view(self):
        """Test ad list view."""
        url = reverse('ads:ad_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ad')
        self.assertContains(response, 'Test Slot')
    
    def test_ad_create_view(self):
        """Test ad create view."""
        url = reverse('ads:ad_create')
        data = {
            'name': 'New Ad',
            'slot': self.slot.id,
            'ad_type': 'html',
            'title': 'New Title',
            'description': 'New description',
            'html_content': '<div>Test HTML</div>',
            'priority': 10,
            'url': 'https://example.com/new',
            'target': '_blank',
            'is_active': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Advertisement.objects.filter(name='New Ad').exists())
    
    def test_ad_edit_view(self):
        """Test ad edit view."""
        url = reverse('ads:ad_edit', args=[self.ad.id])
        data = {
            'name': 'Updated Ad',
            'slot': self.slot.id,
            'ad_type': self.ad.ad_type,
            'title': 'Updated Title',
            'description': 'Updated description',
            'priority': 10,
            'url': self.ad.url,
            'target': self.ad.target,
            'is_active': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.name, 'Updated Ad')
        self.assertEqual(self.ad.title, 'Updated Title')
    
    def test_ad_delete_view(self):
        """Test ad delete view."""
        url = reverse('ads:ad_delete', args=[self.ad.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Advertisement.objects.filter(id=self.ad.id).exists())
    
    def test_ad_toggle_active_view(self):
        """Test ad toggle active view."""
        url = reverse('ads:ad_toggle_active', args=[self.ad.id])
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(data['is_active'])
        
        self.ad.refresh_from_db()
        self.assertFalse(self.ad.is_active)
    
    def test_ad_stats_view(self):
        """Test ad stats view."""
        url = reverse('ads:ad_stats', args=[self.ad.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ad')
        self.assertContains(response, 'آمار تبلیغ')


class AdDisplayViewsTest(TestCase):
    """Tests for ad display views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.slot = AdSlot.objects.create(
            name='Test Slot',
            code='test_slot',
            is_active=True
        )
        self.ad = Advertisement.objects.create(
            name='Test Ad',
            slot=self.slot,
            ad_type='html',
            html_content='<div>Test Ad Content</div>',
            is_active=True
        )
    
    def test_display_ad_view(self):
        """Test display ad view."""
        url = reverse('ads:display_ad', args=['test_slot'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ad Content')
    
    def test_display_ad_not_found(self):
        """Test display ad with non-existent slot."""
        url = reverse('ads:display_ad', args=['nonexistent_slot'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')
    
    def test_track_impression_view(self):
        """Test track impression view."""
        url = reverse('ads:track_impression', args=[self.ad.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'image/png')
        
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.impression_count, 1)
    
    def test_track_click_view(self):
        """Test track click view."""
        url = reverse('ads:track_click', args=[self.ad.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)  # Redirect
        
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.click_count, 1)


class PublicAdViewsTest(TestCase):
    """Tests for public ad views (without authentication)."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.slot = AdSlot.objects.create(
            name='Public Slot',
            code='public_slot',
            is_active=True
        )
        self.ad = Advertisement.objects.create(
            name='Public Ad',
            slot=self.slot,
            ad_type='html',
            html_content='<div>Public Ad Content</div>',
            is_active=True
        )
    
    def test_public_display_ad(self):
        """Test public display ad."""
        url = reverse('ads:display_ad', args=['public_slot'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public Ad Content')
    
    def test_public_track_impression(self):
        """Test public track impression."""
        url = reverse('ads:track_impression', args=[self.ad.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.impression_count, 1)
    
    def test_public_track_click(self):
        """Test public track click."""
        url = reverse('ads:track_click', args=[self.ad.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.click_count, 1)
