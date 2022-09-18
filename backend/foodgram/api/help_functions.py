"""Вспомогательные функции, сокращающие код"""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import AmountOfIngredient, Ingredient, Recipe, RecipeTag


def extra_recipe(request, recipe_id, obj, serializer_short, message_exists,
                 message_del, message_no):
    """Вспомогательная функция для view-функций:
    shoping_cart и favorite"""
    user = request.user
    recipe = get_object_or_404(Recipe, id=recipe_id)
    thing = obj.objects.filter(user=user, recipe=recipe)
    if request.method == 'POST':
        if thing.exists():
            return Response(
                f"{message_exists}",
                status=status.HTTP_400_BAD_REQUEST
            )
        obj.objects.get_or_create(user=user, recipe=recipe)
        serializer = serializer_short(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if thing.exists():
        thing.delete()
        return Response(f"{message_del}", status=status.HTTP_200_OK)
    return Response(f"{message_no}", status=status.HTTP_400_BAD_REQUEST)


def create_amout_of_ingredients(ingredients, recipe):
    """Вспомогательная функция для создание связи
    между рецептом, его ингредиентами и их количеством"""
    ingredients_in_recipe = [
        AmountOfIngredient(recipe=recipe, ingredient=get_object_or_404(
            Ingredient,
            id=ingredient['id']
        ), amount=ingredient['amount']) for ingredient in ingredients
    ]
    AmountOfIngredient.objects.bulk_create(ingredients_in_recipe)


def create_recipe_tag(tags, recipe):
    """Вспомогательная функция для создание связи
    между рецептом и его тэгами"""
    for tag in tags:
        RecipeTag.objects.bulk_create([
            RecipeTag(
                recipe=recipe,
                tag=tag
            )
        ])
