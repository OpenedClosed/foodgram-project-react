from io import StringIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (AmountOfIngredient, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view

from .filters import RecipeFilterSet
from .help_functions import extra_recipe, generate_pdf
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, ShortViewOfRecipe, TagSerializer)
from .viewsets import ReadViewSet


class IngredientViewSet(ReadViewSet):
    """Вьюсет модели Ингредиент"""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None


class TagViewSet(ReadViewSet):
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
    ingredients_in_shopping_cart = {}
    text_in_shopping_cart = ''
    text_file = StringIO()
    for obj in shopping_cart.values():
        recipe = get_object_or_404(Recipe, id=obj['recipe_id'])
        for ingredient in recipe.ingredients.values_list('name', 'id'):
            name = ingredient[0]
            amount = get_object_or_404(
                AmountOfIngredient,
                ingredient=ingredient[1],
                recipe=recipe
            ).amount
            if name not in ingredients_in_shopping_cart:
                ingredients_in_shopping_cart[name] = 0
            ingredients_in_shopping_cart[name] += amount
    for item in ingredients_in_shopping_cart:
        ingredient = get_object_or_404(Ingredient, name=item)
        measurement_unit = ingredient.measurement_unit
        text_in_shopping_cart += (f'{item} ({measurement_unit}) - '
                                  f'{ingredients_in_shopping_cart[item]}\n')
    text_file.write(text_in_shopping_cart)

    input_file = text_file.getvalue()
    output_file = generate_pdf(input_file)
    response = HttpResponse(
        output_file.read(),
        content_type='application/force-download'
    )
    response['Content-Disposition'] = 'attachment; filename=shoping_cart.pdf'
    return response