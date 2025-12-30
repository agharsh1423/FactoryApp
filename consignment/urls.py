from django.urls import path
from . import views

urlpatterns = [
    # Public URLs (no authentication required)
    path('', views.consignment_list, name='consignment_list'),
    path('consignment/<int:pk>/', views.consignment_detail, name='consignment_detail'),
    
    # Authentication URLs
    path('auth/login/', views.user_login, name='login'),
    path('auth/logout/', views.user_logout, name='logout'),
    
    # Admin Dashboard
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    
    # Field Template Management (Admin)
    path('admin-panel/field-templates/', views.field_template_list, name='field_template_list'),
    path('admin-panel/field-templates/create/', views.field_template_create, name='field_template_create'),
    path('admin-panel/field-templates/<int:pk>/edit/', views.field_template_edit, name='field_template_edit'),
    path('admin-panel/field-templates/<int:pk>/delete/', views.field_template_delete, name='field_template_delete'),
    
    # Consignment Management (Admin)
    path('admin-panel/consignments/', views.consignment_manage, name='consignment_manage'),
    path('admin-panel/consignments/create/', views.consignment_create, name='consignment_create'),
    path('admin-panel/consignments/<int:pk>/edit/', views.consignment_edit, name='consignment_edit'),
    path('admin-panel/consignments/<int:pk>/delete/', views.consignment_delete, name='consignment_delete'),
    
    # Measurement Management (Admin)
    path('admin-panel/consignments/<int:consignment_pk>/measurements/add/', views.measurement_add, name='measurement_add'),
    path('admin-panel/measurements/<int:pk>/edit/', views.measurement_edit, name='measurement_edit'),
    path('admin-panel/measurements/<int:pk>/delete/', views.measurement_delete, name='measurement_delete'),
    
    # HTMX Endpoints
    path('admin-panel/htmx/field-toggle/', views.field_toggle_htmx, name='field_toggle_htmx'),
]
