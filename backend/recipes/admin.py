from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.contrib.auth.models import Group

from . import models
from . import utils
from . import filters


HTML_TAG_IMG = (
    '<img src="{url}" '
    'width="{width}" '
    'height="{height}px" />'
)


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

    @admin.display(description='Количество рецептов')
    def recipes(self, user):
        return user.recipes.count()

    @admin.display(description='Количество подписок')
    def subscriptions(self, user):
        return user.subscribers.count()

    @admin.display(description='Количество подписчиков')
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
        'slug'
    )
    search_fields = ('name', 'slug', 'color')
    empty_value_display = '-пусто-'


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
        'ingredient_recipes_count'
    )
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    empty_value_display = '-пусто-'

    @admin.display(description='Рецептов связанных с продуктом')
    def ingredient_recipes_count(self, ingredient):
        return ingredient.ingredient_recipes.count()


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

    @admin.display(description='Количество добавлений в избранное')
    def favorites(self, recipe):
        return recipe.favorite.count()

    @admin.display(description='Изображение')
    def show_image(self, recipe):
        return mark_safe(
            HTML_TAG_IMG.format(
                url=recipe.image.url,
                width=settings.ADMIN_IMAGE_WIDTH,
                height=settings.ADMIN_IMAGE_HEIGHT
            )
        )

    @admin.display(description='Теги')
    def get_tags(self, recipe):
        return mark_safe(
            '{tags}'.format(
                tags='<br>'.join(
                    recipe.tags.values_list('name', flat=True)
                )
            )
        )

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, recipe):
        return mark_safe(
            '{ingredients}'.format(
                ingredients='<br>'.join(
                    utils.get_ingredients_amount(recipes_ids=[recipe.id, ])
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
        'add_date'
    )
    list_filter = ('add_date',)
    search_fields = ('user__username', 'recipe__name')
    empty_value_display = '-пусто-'


@admin.register(models.Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
        'subscribe_date'
    )
    list_filter = ('subscribe_date',)
    search_fields = ('user__username', 'author__username')
    empty_value_display = '-пусто-'
