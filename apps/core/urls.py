"""
URL Configuration for Core app.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # About page
    path('about/', views.about, name='about'),
    
    # Contact page
    path('contact/', views.contact, name='contact'),
    
    # Custom pages
    path('page/<slug:slug>/', views.custom_page, name='custom_page'),
    
    # Search
    path('search/', views.search, name='search'),
    
    # Robots.txt
    path('robots.txt', views.robots_txt, name='robots_txt'),
    
    # Sitemap
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]
