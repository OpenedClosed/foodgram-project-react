from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                    download_shoping_cart, favorite, shoping_cart)

app_name = 'api'

router = routers.DefaultRouter()

router.register(
    r'tags',
    TagViewSet,
    basename='tags'
)

router.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)

router.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)

urlpatterns = [
    path('recipes/<recipe_id>/shopping_cart/', shoping_cart),
    path('recipes/download_shopping_cart/', download_shoping_cart),
    path('recipes/<recipe_id>/favorite/', favorite),
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
