from django.forms import ValidationError


def cooking_time_validate(value):
    """Валидатор времени приготовления
    блюда по рецепту"""
    if value >= 1:
        return value
    raise ValidationError(
        'Введите время приготовления не меньше одной минуты'
    )
