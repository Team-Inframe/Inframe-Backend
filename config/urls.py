from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.static import static
from django.conf import settings

import logging
from django_redis import get_redis_connection

logger = logging.getLogger("inframe")
redis_conn = get_redis_connection("default")


schema_view = get_schema_view(
    openapi.Info(
        title="Inframe API",
        default_version='v1',
        description="Inframe API Description",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url=f"{settings.SERVER_URL}/api/v1"
)

urlpatterns = [
    path('swagger.<format>', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("api/v1/", include([
        path('stickers/', include('sticker.urls')),
        path('users/', include('user.urls')),
        path('frames/', include('frame.urls')),
        path('custom-frames/', include('custom_frame.urls')),
        path('photos/', include('photo.urls')),

    ])),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
