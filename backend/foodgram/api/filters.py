from django_filters import CharFilter, FilterSet
from recipes.models import Recipe


class RecipeFilterSet(FilterSet):
    """Фильтр для рецептов"""
    tags = CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart', ]
        ordering = ['id']
