from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # API v1
    path('api/auth/', include('users.urls')),
    path('api/cotisations/', include('cotisations.urls')),
    path('api/paiements/', include('paiements.urls')),
    path('api/quickpay/', include('quickpay.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/agent-ia/', include('agent_ia.urls')),
    path('api/admin-panel/', include('admin_panel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)