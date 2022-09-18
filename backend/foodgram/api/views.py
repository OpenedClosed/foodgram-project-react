from io import StringIO

from django.db.models import Sum
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view

from recipes.models import (AmountOfIngredient, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from .filters import IngredientSearchFilter, RecipeFilterSet
from .help_functions import extra_recipe
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, ShortViewOfRecipe, TagSerializer)
from .viewsets import ReadViewSet


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Ингредиент"""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Тэг"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Рецепт"""
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly, ]
    filterset_class = RecipeFilterSet
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, ]

    def get_serializer_class(self):
        if self.request.method in ('GET', ):
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@api_view(['POST', 'DELETE', ])
def favorite(request, recipe_id):
    """Вью-функция для добавления рецепта в избранное"""
    obj = Favorite
    message_exists = "Рецепт уже в избранном"
    message_del = "Рецепт успешно удален из избранного"
    message_no = "Рецепта нет в избранном"
    return extra_recipe(request, recipe_id, obj, ShortViewOfRecipe,
                        message_exists, message_del, message_no)


@api_view(['POST', 'DELETE', ])
def shoping_cart(request, recipe_id):
    """Вью-функция для добавления рецепта в список покупок"""
    obj = ShoppingCart
    message_exists = "Рецепт уже в спике покупок"
    message_del = "Рецепт успешно удален из спика покупок"
    message_no = "Рецепта нет в списке покупок"
    return extra_recipe(request, recipe_id, obj, ShortViewOfRecipe,
                        message_exists, message_del, message_no)


@api_view(['GET', ])
def download_shoping_cart(request):
    """Вью-функция для загрузки списка покупок"""
    user = request.user
    shopping_cart = ShoppingCart.objects.filter(user=user)
    text_in_shopping_cart = ''
    text_file = StringIO()
    ingredients = AmountOfIngredient.objects.filter(
        recipe__id__in=shopping_cart.values_list('recipe_id')
    ).values(
        'ingredient__name'
    ).annotate(amount=Sum('amount')).order_by('ingredient__name')

    for item in ingredients:
        ingredient_name = item['ingredient__name']
        ingredient = get_object_or_404(Ingredient, name=ingredient_name)
        measurement_unit = ingredient.measurement_unit
        ingredient_amount = item['amount']
        text_in_shopping_cart += (f'{ingredient_name} ({measurement_unit}) - '
                                  f'{ingredient_amount}\n')
    text_file.write(text_in_shopping_cart)

    input_file = text_file.getvalue()
    response = HttpResponse( 
        input_file, 
        content_type='application/force-download' 
    ) 
    response['Content-Disposition'] = 'attachment; filename=shoping_cart.txt' 
    return response 
