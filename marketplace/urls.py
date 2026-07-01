from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('apps.products.urls', namespace='products')),
    path('vendors/', include('apps.vendors.urls', namespace='vendors')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('reviews/', include('apps.reviews.urls', namespace='reviews')),
    path('messages/', include('apps.messaging.urls', namespace='messaging')),
    path('profile/', include('apps.users.urls', namespace='users')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Marketplace Admin"
admin.site.site_title = "Marketplace"
admin.site.index_title = "Dashboard"
