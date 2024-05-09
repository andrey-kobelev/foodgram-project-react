from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from . import models


User = get_user_model()


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
    search_fields = ('username', 'email',)
    empty_value_display = '-пусто-'

    def recipes(self, user):
        return user.recipes.count()

    def subscriptions(self, user):
        return user.subscribers.count()

    def subscribers(self, user):
        return user.authors.count()

    recipes.short_description = 'Количество рецептов'
    subscriptions.short_description = 'Количество подписок'
    subscribers.short_description = 'Количество подписчиков'


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
    empty_value_display = '-пусто-'


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('favorites',)
    list_display = (
        'name',
        'author',
    )
    inlines = (RecipeIngredientAmountInLine,)
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'

    def favorites(self, recipe):
        return str(recipe.favorite.count())

    favorites.short_description = 'Количество добавлений в избранное'


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    empty_value_display = '-пусто-'


@admin.register(models.ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    empty_value_display = '-пусто-'
