from django.urls import path
from . import views

app_name = 'payments'
urlpatterns = [
    path('checkout/<int:order_id>/', views.payment_checkout, name='checkout'),
    path('success/<int:order_id>/', views.payment_success, name='success'),
    path('webhook/', views.stripe_webhook, name='webhook'),
]