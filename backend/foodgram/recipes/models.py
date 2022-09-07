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
    COLOR_PALETTE = [
        ("#0076FF", "blue"),
        ("#FFCE26", "orange"),
        ("#9922C8", "violet")

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
        through='AmountOfIngredients',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipe',
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
        related_name='recipe',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
    is_favorited = models.BooleanField(
        verbose_name='В избранном'
    )
    is_in_shopping_cart = models.BooleanField(
        verbose_name='В списке покупок'
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

    def __str__(self):
        return f'{self.user} имеет {self.recipe} в избранном'


class AmountOfIngredients(models.Model):
    """Вспомогательная модель,
    связывающая ингредиент, его
    количество и рецепт"""
    amount = models.IntegerField()
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amountofingredients',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amountofingredients',
        verbose_name='Рецепт',
    )

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

    def __str__(self):
        return f'''
        {self.recipe} у пользователя {self.user}
        в спике покупок
        '''
