"""
API URL configuration for ads app.
"""
from django.urls import path
from . import views

app_name = 'ads_api'

urlpatterns = [
    # Ad Slot endpoints
    path('slots/', views.AdSlotListCreateAPIView.as_view(), name='ad_slot_list_create'),
    path('slots/<uuid:pk>/', views.AdSlotRetrieveUpdateDestroyAPIView.as_view(), name='ad_slot_detail'),
    
    # Advertisement endpoints
    path('advertisements/', views.AdvertisementListCreateAPIView.as_view(), name='advertisement_list_create'),
    path('advertisements/<uuid:pk>/', views.AdvertisementRetrieveUpdateDestroyAPIView.as_view(), name='advertisement_detail'),
    
    # Ad display endpoints
    path('display/<str:slot_code>/', views.AdDisplayAPIView.as_view(), name='ad_display'),
    path('display/<str:slot_code>/<int:width>/<int:height>/', views.AdDisplayResponsiveAPIView.as_view(), name='ad_display_responsive'),
    
    # Tracking endpoints
    path('track/impression/<uuid:ad_id>/', views.AdImpressionCreateAPIView.as_view(), name='ad_impression_track'),
    path('track/click/<uuid:ad_id>/', views.AdClickCreateAPIView.as_view(), name='ad_click_track'),
    
    # Statistics endpoints
    path('stats/<uuid:ad_id>/', views.AdvertisementStatsAPIView.as_view(), name='advertisement_stats'),
    path('stats/slot/<str:slot_code>/', views.AdSlotStatsAPIView.as_view(), name='ad_slot_stats'),
    path('stats/', views.AdsOverallStatsAPIView.as_view(), name='ads_overall_stats'),
    
    # Report endpoints
    path('reports/impressions/', views.ImpressionReportAPIView.as_view(), name='impression_report'),
    path('reports/clicks/', views.ClickReportAPIView.as_view(), name='click_report'),
    path('reports/performance/', views.PerformanceReportAPIView.as_view(), name='performance_report'),
]
