from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.contrib.auth.models import Group

from . import constants
from . import models
from . import filters


User = get_user_model()


admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'recipes',
        'subscriptions',
        'subscribers'
    )
    list_filter = (
        *UserAdmin.list_filter,
        filters.UserSubscriptionsListFilter,
    )
    search_fields = ('username', 'email',)
    empty_value_display = '-пусто-'

    @admin.display(description='Рецепты')
    def recipes(self, user):
        return user.recipes.count()

    @admin.display(description='Подписок')
    def subscriptions(self, user):
        return user.subscribers.count()

    @admin.display(description='Подписчиков')
    def subscribers(self, user):
        return user.authors.count()


class RecipeIngredientAmountInLine(admin.TabularInline):
    model = models.RecipeIngredientAmount
    extra = 1


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'display_color',
        'slug'
    )
    search_fields = ('name', 'slug', 'color')
    empty_value_display = '-пусто-'

    @admin.display(description='Цвет')
    def display_color(self, tag):
        return mark_safe(
            f'<div style="width: {constants.ADMIN_COLOR_WIDTH}px; '
            f'height:{constants.ADMIN_COLOR_HEIGHT}px; '
            f'background-color:{tag.color};"></div>'
        )


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
        'recipes_count'
    )
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    empty_value_display = '-пусто-'

    @admin.display(description='Рецепты')
    def recipes_count(self, ingredient):
        return ingredient.recipe_ingredients.count()


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('favorites', 'show_image')
    list_display = (
        'name',
        'author',
        'cooking_time',
        'get_tags',
        'get_ingredients',
        'show_image'
    )
    inlines = (RecipeIngredientAmountInLine,)
    search_fields = (
        'name',
        'author__username',
    )
    list_filter = ('tags', 'pub_date', filters.RecipesCookingTimeListFilter)
    filter_horizontal = ('tags',)
    empty_value_display = '-пусто-'

    @admin.display(description='В избранном')
    def favorites(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Изображение')
    def show_image(self, recipe):
        return mark_safe(
            f'<img src="{recipe.image.url}" '
            f'width="{constants.ADMIN_IMAGE_WIDTH}" '
            f'height="{constants.ADMIN_IMAGE_HEIGHT}px" />'
        )

    @admin.display(description='Теги')
    def get_tags(self, recipe):
        return mark_safe(
            '<br>'.join(
                recipe.tags.values_list('name', flat=True)
            )
        )

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, recipe):
        return mark_safe(
            '<br>'.join(
                f'- {name[:constants.TRUNCATE_PRODUCT_NAME]}'
                for name in recipe.ingredients.values_list(
                    'name', flat=True
                )
            )
        )


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('user__username', 'recipe__name')
    empty_value_display = '-пусто-'


@admin.register(models.ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('user__username', 'recipe__name')
    empty_value_display = '-пусто-'


@admin.register(models.Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = ('user__username', 'author__username')
    empty_value_display = '-пусто-'
