from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (AmountOfIngredients, Favorite, Ingredient, Recipe,
                            RecipeTag, ShoppingCart, Tag)
from rest_framework import serializers
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор создания и показа списка тэгов"""

    class Meta:
        fields = '__all__'
        model = Tag

        extra_kwargs = {
            'color': {'required': True},
        }


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор показа списка ингредиентов"""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientCreateSerializer(serializers.Serializer):
    """Сериализатор создания списка ингредиентов"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class IngredientShowSerializer(serializers.ModelSerializer):
    """Сериализатор показа списка ингредиентов в рецепте"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = AmountOfIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор показа списка рецептов"""
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients = AmountOfIngredients.objects.filter(recipe=obj)
        return IngredientShowSerializer(ingredients, many=True).data

    def get_tags(self, obj):
        tags = Tag.objects.filter(recipe=obj)
        return TagSerializer(tags, many=True).data

    def get_is_favorited(self, obj):
        request_user = self.context.get('request').user.id
        queryset = Favorite.objects.filter(
            recipe=obj.id,
            user=request_user
        ).exists()
        obj.is_favorited = queryset
        obj.save()
        return obj.is_favorited

    def get_is_in_shopping_cart(self, obj):
        request_user = self.context.get('request').user.id
        queryset = ShoppingCart.objects.filter(
            recipe=obj.id,
            user=request_user
        ).exists()
        obj.is_in_shopping_cart = queryset
        obj.save()
        return obj.is_in_shopping_cart

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов"""
    ingredients = IngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(max_length=None)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(
            **validated_data,
            is_favorited=False,
            is_in_shopping_cart=False
        )

        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient,
                id=ingredient['id']
            )
            amount = ingredient['amount']
            AmountOfIngredients.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )

        for tag in tags:
            RecipeTag.objects.create(
                recipe=recipe,
                tag=tag
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        if ingredients is not None:
            instance.amountofingredients.all().delete()
            for ingredient in ingredients:
                current_ingredient = get_object_or_404(
                    Ingredient,
                    id=ingredient['id']
                )
                amount = ingredient['amount']
                AmountOfIngredients.objects.create(
                    recipe=instance,
                    ingredient=current_ingredient,
                    amount=amount
                )
        if tags is not None:
            instance.recipetag.all().delete()
            for tag in tags:
                RecipeTag.objects.create(
                    recipe=instance,
                    tag=tag
                )

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def to_representation(self, value):
        return RecipeSerializer(
            value,
            context=self.context
        ).data

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'name',
            'image',
            'tags',
            'text',
            'cooking_time',
        )


class ShortViewOfRecipe(serializers.ModelSerializer):
    """Сериализатор показа рецептов
    при добавлении в избранное и список
    покупок"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
