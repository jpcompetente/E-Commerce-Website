from django.urls import path
from . import views

app_name = 'vendors'
urlpatterns = [
    path('store/<slug:slug>/', views.store_detail, name='store_detail'),
    path('apply/', views.apply_vendor, name='apply'),
    path('apply/status/', views.apply_vendor, name='application_status'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/products/', views.product_management, name='products'),
    path('dashboard/products/add/', views.add_product, name='add_product'),
    path('dashboard/products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('dashboard/products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('dashboard/orders/', views.order_management, name='orders'),
    path('dashboard/orders/update/<int:pk>/', views.update_order_status, name='update_order_status'),
    path('dashboard/earnings/', views.earnings, name='earnings'),
    path('superadmin/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('superadmin/users/', views.superadmin_users, name='superadmin_users'),
    path('superadmin/users/toggle/<int:pk>/', views.superadmin_toggle_user, name='superadmin_toggle_user'),
    path('superadmin/applications/', views.superadmin_applications, name='superadmin_applications'),
    path('superadmin/applications/approve/<int:pk>/', views.superadmin_approve_vendor, name='superadmin_approve_vendor'),
    path('superadmin/applications/reject/<int:pk>/', views.superadmin_reject_vendor, name='superadmin_reject_vendor'),
    path('superadmin/products/', views.superadmin_products, name='superadmin_products'),
    path('superadmin/orders/', views.superadmin_orders, name='superadmin_orders'),
]
