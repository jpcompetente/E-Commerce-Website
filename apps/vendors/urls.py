from django.urls import path
from . import views

app_name = 'vendors'
urlpatterns = [
    path('store/<slug:slug>/', views.store_detail, name='store_detail'),
    path('apply/', views.apply_vendor, name='apply'),
    path('apply/status/', views.apply_vendor, name='application_status'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/products/', views.product_management, name='products'),
    path('dashboard/orders/', views.order_management, name='orders'),
    path('dashboard/earnings/', views.earnings, name='earnings'),
]