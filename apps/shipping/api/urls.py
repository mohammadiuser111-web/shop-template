"""
API URLs for Shipping app.
"""
from django.urls import path
from .views import (
    # Shipping Zone views
    ShippingZoneListAPIView, ShippingZoneRetrieveAPIView,
    ShippingZoneCreateAPIView, ShippingZoneUpdateAPIView,
    ShippingZoneDestroyAPIView,
    # Shipping Zone Location views
    ShippingZoneLocationListAPIView, ShippingZoneLocationCreateAPIView,
    ShippingZoneLocationDestroyAPIView,
    # Shipping Method views
    ShippingMethodListAPIView, ShippingMethodRetrieveAPIView,
    ShippingMethodCreateAPIView, ShippingMethodUpdateAPIView,
    ShippingMethodDestroyAPIView, ShippingMethodCostAPIView,
    # Shipping Class views
    ShippingClassListAPIView, ShippingClassRetrieveAPIView,
    ShippingClassCreateAPIView, ShippingClassUpdateAPIView,
    ShippingClassDestroyAPIView,
    # Pickup Location views
    PickupLocationListAPIView, PickupLocationRetrieveAPIView,
    PickupLocationCreateAPIView, PickupLocationUpdateAPIView,
    PickupLocationDestroyAPIView,
    # Statistics and available methods
    ShippingStatisticsAPIView, AvailableShippingMethodsAPIView
)

urlpatterns = [
    # Shipping Zones
    path('zones/', ShippingZoneListAPIView.as_view(), name='api-shipping-zones-list'),
    path('zones/create/', ShippingZoneCreateAPIView.as_view(), name='api-shipping-zones-create'),
    path('zones/<uuid:pk>/', ShippingZoneRetrieveAPIView.as_view(), name='api-shipping-zones-retrieve'),
    path('zones/<uuid:pk>/update/', ShippingZoneUpdateAPIView.as_view(), name='api-shipping-zones-update'),
    path('zones/<uuid:pk>/delete/', ShippingZoneDestroyAPIView.as_view(), name='api-shipping-zones-delete'),
    
    # Shipping Zone Locations
    path('zones/<uuid:zone_id>/locations/', ShippingZoneLocationListAPIView.as_view(), name='api-shipping-zone-locations-list'),
    path('zones/<uuid:zone_id>/locations/create/', ShippingZoneLocationCreateAPIView.as_view(), name='api-shipping-zone-locations-create'),
    path('locations/<uuid:pk>/delete/', ShippingZoneLocationDestroyAPIView.as_view(), name='api-shipping-zone-locations-delete'),
    
    # Shipping Methods
    path('methods/', ShippingMethodListAPIView.as_view(), name='api-shipping-methods-list'),
    path('methods/available/', AvailableShippingMethodsAPIView.as_view(), name='api-shipping-methods-available'),
    path('methods/cost/', ShippingMethodCostAPIView.as_view(), name='api-shipping-methods-cost'),
    path('methods/create/', ShippingMethodCreateAPIView.as_view(), name='api-shipping-methods-create'),
    path('methods/<uuid:pk>/', ShippingMethodRetrieveAPIView.as_view(), name='api-shipping-methods-retrieve'),
    path('methods/<uuid:pk>/update/', ShippingMethodUpdateAPIView.as_view(), name='api-shipping-methods-update'),
    path('methods/<uuid:pk>/delete/', ShippingMethodDestroyAPIView.as_view(), name='api-shipping-methods-delete'),
    
    # Zone-specific shipping methods
    path('zones/<uuid:zone_id>/methods/', ShippingMethodListAPIView.as_view(), name='api-zone-shipping-methods-list'),
    
    # Shipping Classes
    path('classes/', ShippingClassListAPIView.as_view(), name='api-shipping-classes-list'),
    path('classes/create/', ShippingClassCreateAPIView.as_view(), name='api-shipping-classes-create'),
    path('classes/<uuid:pk>/', ShippingClassRetrieveAPIView.as_view(), name='api-shipping-classes-retrieve'),
    path('classes/<uuid:pk>/update/', ShippingClassUpdateAPIView.as_view(), name='api-shipping-classes-update'),
    path('classes/<uuid:pk>/delete/', ShippingClassDestroyAPIView.as_view(), name='api-shipping-classes-delete'),
    
    # Pickup Locations
    path('pickup-locations/', PickupLocationListAPIView.as_view(), name='api-pickup-locations-list'),
    path('pickup-locations/create/', PickupLocationCreateAPIView.as_view(), name='api-pickup-locations-create'),
    path('pickup-locations/<uuid:pk>/', PickupLocationRetrieveAPIView.as_view(), name='api-pickup-locations-retrieve'),
    path('pickup-locations/<uuid:pk>/update/', PickupLocationUpdateAPIView.as_view(), name='api-pickup-locations-update'),
    path('pickup-locations/<uuid:pk>/delete/', PickupLocationDestroyAPIView.as_view(), name='api-pickup-locations-delete'),
    
    # Statistics
    path('statistics/', ShippingStatisticsAPIView.as_view(), name='api-shipping-statistics'),
]
