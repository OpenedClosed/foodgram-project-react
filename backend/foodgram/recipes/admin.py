from django.contrib import admin

from .models import AmountOfIngredient, Ingredient, Recipe, RecipeTag, Tag


class AmountOfIngredientInLine(admin.TabularInline):
    model = AmountOfIngredient
    extra = 0


class RecipeTagInLine(admin.TabularInline):
    model = RecipeTag
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (AmountOfIngredientInLine, RecipeTagInLine, )
    list_display = ('name', 'author', )
    list_filter = ('author', 'tags__name', 'name', )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', )
    list_filter = ('name', )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', )
    list_filter = ('name', )
