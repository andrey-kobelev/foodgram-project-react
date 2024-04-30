from django.contrib import admin

from .models import (Ingredient,
                     Recipe,
                     RecipeIngredientAmount,
                     Tag,
                     ShoppingCart,
                     Favorite)


class RecipeIngredientAmountInLine(admin.TabularInline):
    model = RecipeIngredientAmount
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug'
    )
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
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

    def favorites(self, obj):
        return str(obj.favorite.count())

    favorites.short_description = 'Количество добавлений в избранное'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    empty_value_display = '-пусто-'
