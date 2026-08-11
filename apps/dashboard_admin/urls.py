"""
URL configuration for dashboard_admin app.
"""
from django.urls import path
from . import views

app_name = 'dashboard_admin'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Settings
    path('settings/', views.DashboardSettingsView.as_view(), name='settings'),
    path('menu-management/', views.MenuManagementView.as_view(), name='menu_management'),
    
    # Activity Logs
    path('activities/', views.ActivityLogView.as_view(), name='activity_logs'),
    
    # API Endpoints (AJAX)
    path('api/dashboard-data/', views.GetDashboardDataView.as_view(), name='api_dashboard_data'),
    path('api/widget/<uuid:widget_id>/data/', views.WidgetDataView.as_view(), name='api_widget_data'),
    path('api/update-widget-order/', views.UpdateWidgetOrderView.as_view(), name='api_update_widget_order'),
    path('api/toggle-sidebar/', views.ToggleSidebarView.as_view(), name='api_toggle_sidebar'),
]
