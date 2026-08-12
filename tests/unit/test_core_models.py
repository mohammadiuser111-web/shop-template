"""
Unit tests for Core application models.
Tests SiteSetting, SocialLink, ContactInfo, Menu, MenuItem, Page models.
"""

import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db


class TestSiteSetting:
    """Tests for SiteSetting model"""
    
    def test_site_setting_creation(self, db):
        """Test creating a site setting"""
        from apps.core.models import SiteSetting
        setting = SiteSetting.objects.create(
            key='site_name',
            value='Shop Template',
            description='Site name setting'
        )
        
        assert setting.key == 'site_name'
        assert setting.value == 'Shop Template'
        assert setting.description == 'Site name setting'
        assert str(setting) == 'site_name: Shop Template'
    
    def test_site_setting_unique_key(self, db):
        """Test that site setting keys are unique"""
        from apps.core.models import SiteSetting
        SiteSetting.objects.create(key='test_key', value='value1')
        
        with pytest.raises(Exception):
            SiteSetting.objects.create(key='test_key', value='value2')
    
    def test_site_setting_str(self, db):
        """Test string representation of site setting"""
        from apps.core.models import SiteSetting
        setting = SiteSetting.objects.create(key='test', value='value')
        assert str(setting) == 'test: value'


class TestSocialLink:
    """Tests for SocialLink model"""
    
    def test_social_link_creation(self, db):
        """Test creating a social link"""
        from apps.core.models import SocialLink
        link = SocialLink.objects.create(
            platform='twitter',
            url='https://twitter.com/test',
            icon='fa-twitter',
            is_active=True,
            sort_order=0
        )
        
        assert link.platform == 'twitter'
        assert link.url == 'https://twitter.com/test'
        assert link.icon == 'fa-twitter'
        assert link.is_active is True
        assert link.sort_order == 0
        assert str(link) == 'Twitter - https://twitter.com/test'
    
    def test_social_link_str(self, db):
        """Test string representation of social link"""
        from apps.core.models import SocialLink
        link = SocialLink.objects.create(platform='facebook', url='https://fb.com')
        assert str(link) == 'Facebook - https://fb.com'
    
    def test_social_link_sort_order(self, db):
        """Test social link sort order"""
        from apps.core.models import SocialLink
        link1 = SocialLink.objects.create(platform='twitter', url='https://twitter.com', sort_order=1)
        link2 = SocialLink.objects.create(platform='facebook', url='https://fb.com', sort_order=0)
        
        links = SocialLink.objects.all().order_by('sort_order')
        assert links[0] == link2
        assert links[1] == link1


class TestContactInfo:
    """Tests for ContactInfo model"""
    
    def test_contact_info_creation(self, db):
        """Test creating contact info"""
        from apps.core.models import ContactInfo
        info = ContactInfo.objects.create(
            type='email',
            value='info@test.com',
            icon='fa-envelope',
            is_active=True,
            sort_order=0
        )
        
        assert info.type == 'email'
        assert info.value == 'info@test.com'
        assert info.icon == 'fa-envelope'
        assert info.is_active is True
        assert str(info) == 'Email - info@test.com'
    
    def test_contact_info_str(self, db):
        """Test string representation of contact info"""
        from apps.core.models import ContactInfo
        info = ContactInfo.objects.create(type='phone', value='+123456789')
        assert str(info) == 'Phone - +123456789'


class TestMenu:
    """Tests for Menu model"""
    
    def test_menu_creation(self, db):
        """Test creating a menu"""
        from apps.core.models import Menu
        menu = Menu.objects.create(
            name='Main Menu',
            slug='main-menu',
            description='Primary navigation',
            is_active=True,
            sort_order=0
        )
        
        assert menu.name == 'Main Menu'
        assert menu.slug == 'main-menu'
        assert menu.description == 'Primary navigation'
        assert menu.is_active is True
        assert str(menu) == 'Main Menu'
    
    def test_menu_str(self, db):
        """Test string representation of menu"""
        from apps.core.models import Menu
        menu = Menu.objects.create(name='Footer Menu', slug='footer-menu')
        assert str(menu) == 'Footer Menu'
    
    def test_menu_slug_generation(self, db):
        """Test menu slug generation"""
        from apps.core.models import Menu
        menu = Menu.objects.create(name='Test Menu')
        assert menu.slug == 'test-menu'


class TestMenuItem:
    """Tests for MenuItem model"""
    
    def test_menu_item_creation(self, db):
        """Test creating a menu item"""
        from apps.core.models import Menu, MenuItem
        menu = Menu.objects.create(name='Main Menu', slug='main-menu')
        item = MenuItem.objects.create(
            menu=menu,
            title='Home',
            url='/',
            is_active=True,
            sort_order=0
        )
        
        assert item.menu == menu
        assert item.title == 'Home'
        assert item.url == '/'
        assert item.is_active is True
        assert str(item) == 'Home (Main Menu)'
    
    def test_menu_item_str(self, db):
        """Test string representation of menu item"""
        from apps.core.models import Menu, MenuItem
        menu = Menu.objects.create(name='Main Menu', slug='main-menu')
        item = MenuItem.objects.create(menu=menu, title='About', url='/about/')
        assert str(item) == 'About (Main Menu)'
    
    def test_menu_item_parent_relationship(self, db):
        """Test menu item parent relationship"""
        from apps.core.models import Menu, MenuItem
        menu = Menu.objects.create(name='Main Menu', slug='main-menu')
        parent = MenuItem.objects.create(menu=menu, title='Products', url='/products/')
        child = MenuItem.objects.create(menu=menu, title='Electronics', url='/products/electronics/', parent=parent)
        
        assert child.parent == parent
        assert child in parent.children.all()


class TestPage:
    """Tests for Page model"""
    
    def test_page_creation(self, db):
        """Test creating a page"""
        from apps.core.models import Page
        page = Page.objects.create(
            title='About Us',
            slug='about-us',
            content='Page content',
            is_active=True,
            is_published=True,
            sort_order=0
        )
        
        assert page.title == 'About Us'
        assert page.slug == 'about-us'
        assert page.content == 'Page content'
        assert page.is_active is True
        assert page.is_published is True
        assert str(page) == 'About Us'
    
    def test_page_str(self, db):
        """Test string representation of page"""
        from apps.core.models import Page
        page = Page.objects.create(title='Contact', slug='contact')
        assert str(page) == 'Contact'
    
    def test_page_published_at(self, db):
        """Test page published_at field"""
        from apps.core.models import Page
        page = Page.objects.create(
            title='Test Page',
            slug='test-page',
            published_at=timezone.now()
        )
        assert page.published_at is not None


class TestPageManager:
    """Tests for Page manager"""
    
    def test_published_filter(self, db):
        """Test filtering published pages"""
        from apps.core.models import Page
        Page.objects.create(title='Draft', slug='draft', is_published=False)
        Page.objects.create(title='Published', slug='published', is_published=True)
        
        published = Page.objects.filter(is_published=True)
        assert published.count() == 1
        assert published[0].title == 'Published'
    
    def test_active_filter(self, db):
        """Test filtering active pages"""
        from apps.core.models import Page
        Page.objects.create(title='Inactive', slug='inactive', is_active=False)
        Page.objects.create(title='Active', slug='active', is_active=True)
        
        active = Page.objects.filter(is_active=True)
        assert active.count() == 1
        assert active[0].title == 'Active'
