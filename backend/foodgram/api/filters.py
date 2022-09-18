from django.db.models import Q
from django_filters import (AllValuesMultipleFilter, BooleanFilter,
                            FilterSet)

from rest_framework.filters import SearchFilter

from recipes.models import Recipe
from django_filters.widgets import BooleanWidget


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilterSet(FilterSet):
    """Фильтр для рецептов"""
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(
        method='get_is_in_shopping_cart'
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


class RecipeFilterSet2(FilterSet):
    """
    Фильтр для рецептов.
    """
    is_favorited = BooleanFilter(
        field_name='is_favorited',
        method='favorite_filter'
    )
    is_in_shopping_cart = BooleanFilter(
        field_name='is_in_shopping_cart',
        method='shopping_cart_filter'
    )
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    def favorite_filter(self, queryset, name, value):
        return Recipe.objects.filter(favorite__user=self.request.user)

    def shopping_cart_filter(self, queryset, name, value):
        return Recipe.objects.filter(shoppingcart__user=self.request.user)

    class Meta:
        model = Recipe
        fields = ['author']


class RecipeFilterSet3(FilterSet):
    is_in_shopping_cart = BooleanFilter(
        method="filter_is_in_shopping_cart", widget=BooleanWidget()
    )
    is_favorited = BooleanFilter(
        method="filter_is_favorited", widget=BooleanWidget()
    )
    tags = AllValuesMultipleFilter(field_name="tags__slug")

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(favorite__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(shoppingcart__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ["tags__slug", "is_favorited", "is_in_shopping_cart"]
