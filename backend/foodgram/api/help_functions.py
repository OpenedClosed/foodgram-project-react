"""Вспомогательные функции, сокращающие код"""
import textwrap

from django.shortcuts import get_object_or_404
from fpdf import FPDF
from recipes.models import Recipe
from rest_framework import status
from rest_framework.response import Response

from .serializers import ShortViewOfRecipe


def extra_recipe(request, recipe_id, obj, message1, message2, message3):
    """Вспомогательная функция для view-функций:
    shoping_cart и favorite"""
    user = request.user
    recipe = get_object_or_404(Recipe, id=recipe_id)
    thing = obj.objects.filter(user=user, recipe=recipe)
    print(thing)
    if request.method == 'POST':
        if thing.exists():
            return Response(f"{message1}", status=status.HTTP_400_BAD_REQUEST)
        obj.objects.get_or_create(user=user, recipe=recipe)
        serializer = ShortViewOfRecipe(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if thing.exists():
        thing.delete()
        return Response(f"{message2}", status=status.HTTP_200_OK)
    return Response(f"{message3}", status=status.HTTP_400_BAD_REQUEST)


def text_to_pdf(text, filename):
    """Вспомогательная функция для конвертирования
    файла с расширением .txt в .pdf"""
    a4_width_mm = 210
    pt_to_mm = 0.35
    fontsize_pt = 10
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'fonts/DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 14)
    splitted = text.split('\n')

    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)

    pdf.output(filename, 'F')
