from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (AmountOfIngredient, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from users.serializers import CustomUserSerializer
from .help_functions import create_amout_of_ingredients, create_recipe_tag


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
        model = AmountOfIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор показа списка рецептов"""
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientShowSerializer(
        source='amountofingredient',
        read_only=True,
        many=True
    )
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        request_user = self.context.get('request').user.id
        return Favorite.objects.filter(
            recipe=obj.id,
            user=request_user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request_user = self.context.get('request').user.id
        return ShoppingCart.objects.filter(
            recipe=obj.id,
            user=request_user
        ).exists()

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
        many=True,
    )
    image = Base64ImageField(use_url=True, )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(
            **validated_data
        )
        create_amout_of_ingredients(ingredients, recipe)
        create_recipe_tag(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        recipe = instance

        if ingredients is not None:
            instance.amountofingredient.all().delete()
            create_amout_of_ingredients(ingredients, recipe)

        if tags is not None:
            instance.recipetag.all().delete()
            create_recipe_tag(tags, recipe)

        return super(
            RecipeCreateSerializer, self
        ).update(instance, validated_data)

    def validate(self, data):
        ingredients = data['ingredients']
        id_of_input_ingredients = []
        for ingredient in ingredients:
            if ingredient['id'] in id_of_input_ingredients:
                raise serializers.ValidationError(
                    {'ingredients': ('Ингредиенты повторяются')}
                )
            id_of_input_ingredients.append(ingredient['id'])

        tags = data['tags']
        input_tags = []
        for tag in tags:
            if tag in input_tags:
                raise serializers.ValidationError(
                    {'tags': ('Тэги повторяются')}
                )
            input_tags.append(tag)
        return data

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
