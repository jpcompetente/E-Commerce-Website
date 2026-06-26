from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('<str:username>/', views.profile_view, name='profile'),
    path('edit/profile/', views.edit_profile_view, name='edit_profile'),
    path('account/settings/', views.settings_view, name='settings'),
    path('address/delete/<int:pk>/', views.delete_address_view, name='delete_address'),
    path('address/default/<int:pk>/', views.set_default_address_view, name='set_default_address'),
]
