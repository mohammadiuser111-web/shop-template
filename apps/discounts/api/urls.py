"""
API URLs for Discounts app.
"""
from django.urls import path
from .views import (
    # Discount views
    DiscountListAPIView, DiscountRetrieveAPIView,
    # Coupon views
    CouponListAPIView, CouponRetrieveAPIView,
    CouponCreateAPIView, CouponUpdateAPIView,
    CouponDestroyAPIView, CouponValidateAPIView,
    CouponApplyAPIView,
    # Campaign views
    CampaignListAPIView, CampaignRetrieveAPIView,
    CampaignCreateAPIView, CampaignUpdateAPIView,
    CampaignDestroyAPIView,
    # Coupon Usage views
    CouponUsageListAPIView, CouponUsageRetrieveAPIView,
    # Statistics and available discounts
    DiscountStatisticsAPIView, AvailableCouponsAPIView,
    ActiveCampaignsAPIView
)

urlpatterns = [
    # Discounts (base)
    path('discounts/', DiscountListAPIView.as_view(), name='api-discounts-list'),
    path('discounts/<uuid:pk>/', DiscountRetrieveAPIView.as_view(), name='api-discounts-retrieve'),
    
    # Coupons
    path('coupons/', CouponListAPIView.as_view(), name='api-coupons-list'),
    path('coupons/available/', AvailableCouponsAPIView.as_view(), name='api-coupons-available'),
    path('coupons/validate/', CouponValidateAPIView.as_view(), name='api-coupons-validate'),
    path('coupons/apply/', CouponApplyAPIView.as_view(), name='api-coupons-apply'),
    path('coupons/create/', CouponCreateAPIView.as_view(), name='api-coupons-create'),
    path('coupons/<uuid:pk>/', CouponRetrieveAPIView.as_view(), name='api-coupons-retrieve'),
    path('coupons/<uuid:pk>/update/', CouponUpdateAPIView.as_view(), name='api-coupons-update'),
    path('coupons/<uuid:pk>/delete/', CouponDestroyAPIView.as_view(), name='api-coupons-delete'),
    
    # Campaigns
    path('campaigns/', CampaignListAPIView.as_view(), name='api-campaigns-list'),
    path('campaigns/active/', ActiveCampaignsAPIView.as_view(), name='api-campaigns-active'),
    path('campaigns/create/', CampaignCreateAPIView.as_view(), name='api-campaigns-create'),
    path('campaigns/<uuid:pk>/', CampaignRetrieveAPIView.as_view(), name='api-campaigns-retrieve'),
    path('campaigns/<uuid:pk>/update/', CampaignUpdateAPIView.as_view(), name='api-campaigns-update'),
    path('campaigns/<uuid:pk>/delete/', CampaignDestroyAPIView.as_view(), name='api-campaigns-delete'),
    
    # Coupon Usages
    path('coupons/<uuid:coupon_id>/usages/', CouponUsageListAPIView.as_view(), name='api-coupon-usages-list'),
    path('usages/<uuid:pk>/', CouponUsageRetrieveAPIView.as_view(), name='api-coupon-usages-retrieve'),
    
    # Statistics
    path('statistics/', DiscountStatisticsAPIView.as_view(), name='api-discounts-statistics'),
]
