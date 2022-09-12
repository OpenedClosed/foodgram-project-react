"""Вспомогательные функции, сокращающие код"""
from io import BytesIO

from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import serializers, status
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
    for ingredient in ingredients:
        current_ingredient = get_object_or_404(
            Ingredient,
            id=ingredient['id']
        )
        if AmountOfIngredient.objects.filter(
            recipe=recipe,
            ingredient=current_ingredient,
        ).exists():
            raise serializers.ValidationError('Ингредиенты повторяются')
        amount = ingredient['amount']
        AmountOfIngredient.objects.bulk_create([
            AmountOfIngredient(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )
        ])


def create_recipe_tag(tags, recipe):
    for tag in tags:
        if RecipeTag.objects.filter(
            recipe=recipe,
            tag=tag,
        ).exists():
            raise serializers.ValidationError('Тэги повторяются')
        RecipeTag.objects.bulk_create([
            RecipeTag(
                recipe=recipe,
                tag=tag
            )
        ])


def generate_pdf(text):
    pdf_output = BytesIO()
    pdf = canvas.Canvas(pdf_output, pagesize=letter)
    pdfmetrics.registerFont(TTFont('DejaVu', 'fonts/DejaVuSansCondensed.ttf'))
    pdf.setFont('DejaVu', '', 14)
    pdf.drawString(220, 700, text)
    pdf.showPage()
    pdf.save()
    return pdf_output
