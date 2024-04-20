from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

from pytils.translit import slugify

from . import constants
from .baseclasses import BaseWithNameFieldModel


User = get_user_model()


class Tag(BaseWithNameFieldModel):
    color = models.CharField(
        verbose_name='Цвет',
        max_length=constants.COLOR_MAX_LENGTH
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=constants.SLUG_MAX_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:constants.SLUG_MAX_LENGTH]

        super().save(*args, **kwargs)


class Ingredient(BaseWithNameFieldModel):
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=constants.MEASUREMENT_UNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(BaseWithNameFieldModel):
    author = models.ForeignKey(
        to=User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение'
    )
    tags = models.ManyToManyField(
        to=Tag,
        verbose_name='Теги'
    )

    ingredients = models.ManyToManyField(
        to=Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredientAmount'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(constants.MIN_MINUTE_VALUE),],
        verbose_name='Время приготовления'
    )
    pub_date = models.DateField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('pub_date',)


class RecipeIngredientAmount(models.Model):
    recipe = models.ForeignKey(
        to=Recipe, on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        to=Ingredient, on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(constants.MIN_MINUTE_VALUE),]
    )

    def __str__(self):
        return (f'{self.recipe.name}: '
                f'{self.ingredient.name} '
                f'{self.amount} '
                f'{self.ingredient.measurement_unit}')
