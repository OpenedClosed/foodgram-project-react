from django.contrib.auth import password_validation
from rest_framework import serializers

from recipes.models import Recipe
from .models import CustomUser, Subscription


class SubscribeMixin(serializers.Serializer):
    """Класс, добавляющий поле is_subscribed"""
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        author_id = obj.id if isinstance(obj, CustomUser) else obj.author.id
        user_id = self.context['request'].user.id if (
            isinstance(obj, CustomUser)
        ) else obj.user.id
        obj.is_subscribed = Subscription.objects.filter(
            author=author_id,
            user=user_id
        ).exists()
        return obj.is_subscribed


class CustomUserSerializer(SubscribeMixin):
    """Сериализатор показа пользователей"""
    email = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователей"""

    class Meta:
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'password',
        )
        model = CustomUser
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True}
        }

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def to_representation(self, value):
        return CustomUserSerializer(
            value,
            context=self.context
        ).data


class TokenSerializer(serializers.Serializer):
    """Сериализатор получения токена"""
    password = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля для текущего пользователя"""
    new_password = serializers.CharField(max_length=150)
    current_password = serializers.CharField(max_length=150)


class RecipeInSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор показа рецептов, выложенных
    авторами из подписок"""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'cooking_time'
        )


class SubscriptionSerializer(SubscribeMixin):
    """Сериализатор вывода данных пользователей
    из подписок"""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = RecipeInSubscriptionSerializer(
        source='author.recipes',
        read_only=True,
        many=True
    )
    recipes_count = serializers.SerializerMethodField()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author.id).count()
