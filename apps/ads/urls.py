"""
URL configuration for ads app.
"""
from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    # Ad display
    path('display/<str:slot_code>/', views.display_ad, name='display_ad'),
    path('display/<str:slot_code>/<int:width>/<int:height>/', views.display_ad_responsive, name='display_ad_responsive'),
    
    # Track impressions and clicks
    path('track/impression/<uuid:ad_id>/', views.track_impression, name='track_impression'),
    path('track/click/<uuid:ad_id>/', views.track_click, name='track_click'),
    
    # Ad management (admin views)
    path('slots/', views.ad_slot_list, name='ad_slot_list'),
    path('slots/create/', views.ad_slot_create, name='ad_slot_create'),
    path('slots/<uuid:pk>/edit/', views.ad_slot_edit, name='ad_slot_edit'),
    path('slots/<uuid:pk>/delete/', views.ad_slot_delete, name='ad_slot_delete'),
    
    path('ads/', views.ad_list, name='ad_list'),
    path('ads/create/', views.ad_create, name='ad_create'),
    path('ads/<uuid:pk>/edit/', views.ad_edit, name='ad_edit'),
    path('ads/<uuid:pk>/delete/', views.ad_delete, name='ad_delete'),
    path('ads/<uuid:pk>/toggle/', views.ad_toggle_active, name='ad_toggle_active'),
    path('ads/<uuid:pk>/stats/', views.ad_stats, name='ad_stats'),
    
    # Reports
    path('reports/', views.ads_report, name='ads_report'),
    path('reports/impressions/', views.impression_report, name='impression_report'),
    path('reports/clicks/', views.click_report, name='click_report'),
    path('reports/performance/', views.performance_report, name='performance_report'),
    
    # AJAX endpoints
    path('api/ad/<str:slot_code>/', views.get_ad_json, name='api_get_ad'),
    path('api/stats/<uuid:ad_id>/', views.get_ad_stats_json, name='api_get_ad_stats'),
]
