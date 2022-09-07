from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from .views import (CustomUserViewSet, SubscriptionViewSet, delete_token,
                    get_token, subscribe)

router_v1 = routers.DefaultRouter()
router_v1.register(
    'subscriptions',
    SubscriptionViewSet,
    basename='subcriptions'
)
router_v1.register('', CustomUserViewSet, basename='users')

urlpatterns = [
    path('auth/token/login/', get_token),
    path('auth/token/logout/', delete_token),
    path('users/<user_id>/subscribe/', subscribe),
    path('users/', include(router_v1.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
