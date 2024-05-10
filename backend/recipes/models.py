from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from . import constants
from .validators import username_validator, hex_color_validator


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=settings.USERNAME_MAX_LENGTH,
        validators=(username_validator,),
        unique=True
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=settings.EMAIL_MAX_LENGTH
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=settings.PASSWORD_MAX_LENGTH
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.FIRST_NAME_MAX_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.LAST_NAME_MAX_LENGTH
    )
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'password',
        'last_name',
        'first_name'
    ]

    class Meta:
        ordering = ('email',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Подписан на автора'
    )
    subscribe_date = models.DateField(
        verbose_name='Дата подписки',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        ordering = ('subscribe_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.author}'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Имя тега',
        max_length=constants.NAME_MAX_LENGTH,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=constants.COLOR_MAX_LENGTH,
        unique=True,
        validators=[hex_color_validator, ]
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=constants.SLUG_MAX_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

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
        validators=[MinValueValidator(constants.MIN_MINUTE_VALUE), ],
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
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        verbose_name='Продукт',
        on_delete=models.CASCADE,
        related_name='ingredient_recipes'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(constants.MIN_AMOUNT_VALUE),
        ],
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Ингредиент и количество'
        verbose_name_plural = 'Ингредиенты и количество'
        ordering = ('recipe', 'ingredient', 'amount')

    def __str__(self):
        return (
            f'{self.ingredient.name} '
            f'{self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class BaseUserRecipeModel(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        default_related_name = '%(class)s'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name=f'{"%(class)s"}_unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'


class Favorite(BaseUserRecipeModel):

    class Meta(BaseUserRecipeModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('user__username',)
        default_related_name = 'favorites'


class ShoppingCart(BaseUserRecipeModel):

    add_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta(BaseUserRecipeModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('add_date',)
