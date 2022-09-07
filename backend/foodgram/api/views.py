from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (AmountOfIngredients, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view

from .filters import RecipeFilterSet
from .help_functions import extra_recipe, text_to_pdf
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, TagSerializer)
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
    def get_serializer_class(self):
        if self.request.method in ('GET', ):
            return RecipeSerializer
        return RecipeCreateSerializer
    queryset = Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    permission_classes = [IsAuthorOrReadOnly, ]
    filterset_class = RecipeFilterSet
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, ]


@api_view(['POST', 'DELETE', ])
def favorite(request, recipe_id):
    """Вью-функция для добавления рецепта в избранное"""
    obj = Favorite
    message1 = "Рецепт уже в избранном"
    message2 = "Рецепт успешно удален из избранного"
    message3 = "Рецепта нет в избранном"
    return extra_recipe(request, recipe_id, obj, message1, message2, message3)


@api_view(['POST', 'DELETE', ])
def shoping_cart(request, recipe_id):
    """Вью-функция для добавления рецепта в список покупок"""
    obj = ShoppingCart
    message1 = "Рецепт уже в спике покупок"
    message2 = "Рецепт успешно удален из спика покупок"
    message3 = "Рецепта нет в списке покупок"
    return extra_recipe(request, recipe_id, obj, message1, message2, message3)


@api_view(['GET', ])
def download_shoping_cart(request):
    """Вью-функция для загрузки списка покупок"""
    with open("media/recipes/files/shoping_cart.txt", "w") as file:
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        d = {}
        string = ''
        for obj in shopping_cart.values():
            recipe = get_object_or_404(Recipe, id=obj['recipe_id'])
            for ingredient in recipe.ingredients.all():
                name = ingredient.name
                amount = get_object_or_404(
                    AmountOfIngredients,
                    ingredient=ingredient,
                    recipe=recipe
                ).amount
                if name not in d.keys():
                    d[name] = 0
                d[name] += amount

        for item in d.keys():
            ingredient = get_object_or_404(Ingredient, name=item)
            measurement_unit = ingredient.measurement_unit
            string += f'{item} ({measurement_unit}) - {d[item]}\n'

        file.write(string)
    input_filename = 'media/recipes/files/shoping_cart.txt'
    output_filename = 'media/recipes/files/shoping_cart.pdf'
    file = open(input_filename)
    text = file.read()
    file.close()
    text_to_pdf(text, output_filename)
    file_pointer = open(input_filename, "r")
    response = HttpResponse(
        file_pointer,
        content_type='application/force-download'
    )
    response['Content-Disposition'] = 'attachment; filename=shoping_cart.pdf'
    return response
