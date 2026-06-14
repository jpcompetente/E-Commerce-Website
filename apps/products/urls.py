from django.urls import path
from . import views

app_name = 'products'
urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.product_list, name='list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
]