from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models
from users.models import CustomUser

from .validators import cooking_time_validate

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента блюда"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['id']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тэга приема пищи"""
    BLUE = "#0076FF"
    ORANGE = "#FFCE26"
    VIOLET = "#9922C8"
    COLOR_PALETTE = [
        (BLUE, "blue"),
        (ORANGE, "orange"),
        (VIOLET, "violet")

    ]
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название'
    )
    color = ColorField(
        choices=COLOR_PALETTE,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['id']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта блюда"""
    ingredients = models.ManyToManyField(
        Ingredient,
        through='AmountOfIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes',
        verbose_name='Тэги'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    text = models.TextField(verbose_name='Текст')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[cooking_time_validate]
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='recipes',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['id']

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Модель избранного для пользователя"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_for_user'
            )
        ]

    def __str__(self):
        return f'{self.user} имеет {self.recipe} в избранном'


class AmountOfIngredient(models.Model):
    """Вспомогательная модель,
    связывающая ингредиент, его
    количество и рецепт"""
    amount = models.IntegerField(
        verbose_name='Количество'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amountofingredient',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amountofingredient',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return f'''
        {self.amount} {self.ingredient.measurement_unit}
        {self.ingredient} в {self.recipe}
        '''


class RecipeTag(models.Model):
    """Вспомогательная модель,
    связывающая рецепт и его тэги"""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipetag',
        verbose_name='Тэг',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipetag',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_tag_in_recipe'
            )
        ]

    def __str__(self):
        return f"""
        {self.tag} пренадлежит рецепту {self.recipe}
        """


class ShoppingCart(models.Model):
    """Вспомогательная модель,
    связывающая пользователя с
    рецптами из списка покупок"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Рецепты в списке покупок'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_in_users_shoping_cart'
            )
        ]

    def __str__(self):
        return f'''
        {self.recipe} у пользователя {self.user}
        в спике покупок
        '''
