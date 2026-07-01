from django.urls import path
from . import views

app_name = 'messaging'
urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:pk>/', views.conversation_detail, name='conversation'),
    path('conversation/<int:pk>/send/', views.send_message, name='send_message'),
    path('conversation/<int:pk>/delete/', views.delete_conversation, name='delete_conversation'),
    path('start/<slug:store_slug>/', views.start_conversation, name='start_conversation'),
]

