from django.urls import path
from . import views

app_name = 'reviews'
urlpatterns = [
    path('add/<int:product_id>/', views.add_review, name='add_review'),
    path('delete/<int:pk>/', views.delete_review, name='delete_review'),
    path('reply/<int:pk>/', views.reply_review, name='reply_review'),
]
