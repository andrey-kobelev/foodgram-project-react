from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

from pytils.translit import slugify

from . import constants


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Имя тега',
        max_length=constants.NAME_MAX_LENGTH
    )
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
            self.slug = (
                slugify(self.name)
                [:constants.SLUG_MAX_LENGTH]
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=constants.NAME_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=constants.MEASUREMENT_UNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название блюда',
        max_length=constants.NAME_MAX_LENGTH
    )
    author = models.ForeignKey(
        to=User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    image = models.ImageField(
        upload_to=constants.RECIPE_IMAGE_UPLOAD_TO,
        verbose_name='Изображение'
    )
    tags = models.ManyToManyField(
        to=Tag,
        verbose_name='Теги'
    )

    ingredients = models.ManyToManyField(
        to=Ingredient,
        through='RecipeIngredientAmount',
        verbose_name='Ингредиенты',
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
        ordering = constants.RECIPE_ORDERING
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_name_author'
            )
        ]

    def __str__(self):
        return self.name


class RecipeIngredientAmount(models.Model):
    recipe = models.ForeignKey(
        to=Recipe, on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        to=Ingredient, on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(constants.MIN_MINUTE_VALUE),],
        blank=True,
        null=True
    )

    def __str__(self):
        return (
            f'{self.recipe.name}: '
            f'{self.ingredient.name} '
            f'{self.amount} '
        )


class BaseUserRecipeModel(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        default_related_name = '%(class)s'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name=f'{default_related_name}_unique_user_recipe'
            )
        ]


class Favorite(BaseUserRecipeModel):

    class Meta(BaseUserRecipeModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('user__username',)


class ShoppingCart(BaseUserRecipeModel):

    add_date = models.DateField(
        auto_now_add=True
    )

    class Meta(BaseUserRecipeModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('add_date',)
