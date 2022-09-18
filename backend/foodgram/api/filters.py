from django.db.models import Q
from django_filters import AllValuesMultipleFilter, BooleanFilter, FilterSet
from django_filters.widgets import BooleanWidget
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilterSet(FilterSet):
    """Фильтр для рецептов"""
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = BooleanFilter(
        method='get_is_favorited',
        widget=BooleanWidget()
    )
    is_in_shopping_cart = BooleanFilter(
        method='get_is_in_shopping_cart',
        widget=BooleanWidget()
    )

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite__user=user)
        return queryset.filter(~Q(favorite__user=user))

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shoppingcart__user=user)
        return queryset.filter(~Q(shoppingcart__user=user))

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart', ]
        ordering = ['id']
