from django.conf import settings
from django.contrib.admin import SimpleListFilter
from django.db.models import Max

from . import models


SUBSCRIBING = 'with-subscribing'
SUBSCRIBERS = 'with-subscribers'
FAST_DISHES = 'Быстрые за {time} мин. ({recipes})'
LONGTIME_DISHES = 'Долго, свыше {time} мин. ({recipes})'


class UserSubscriptionsListFilter(SimpleListFilter):
    title = 'Подписки'
    parameter_name = 'subscriptions'

    def lookups(self, request, model_admin):
        return (
            (SUBSCRIBING, 'Только с подписками'),
            (SUBSCRIBERS, 'Только с подписчиками'),
        )

    def get_subscriptions_filter(self, field_name, users):
        return users.filter(
            id__in=models.Subscriptions
            .objects.select_related(field_name)
            .values(f'{field_name}__id')
        )

    def queryset(self, request, users):
        if self.value() == SUBSCRIBING:
            return self.get_subscriptions_filter(
                field_name='user',
                users=users,
            )
        if self.value() == SUBSCRIBERS:
            return self.get_subscriptions_filter(
                field_name='author',
                users=users,
            )


class RecipesCookingTimeListFilter(SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking-time'

    def lookups(self, request, model_admin):
        recipes = (
            model_admin.get_queryset(request)
        )
        return (
            (
                settings.FASTER,
                FAST_DISHES.format(
                    time=settings.FASTER,
                    recipes=recipes.filter(
                        cooking_time__lte=settings.FASTER
                    ).count()
                )
            ),
            (
                settings.FAST,
                FAST_DISHES.format(
                    time=settings.FAST,
                    recipes=recipes.filter(
                        cooking_time__range=(settings.FASTER, settings.FAST)
                    ).count()
                )
            ),
            (
                recipes.aggregate(maxtime=Max('cooking_time'))['maxtime'],
                LONGTIME_DISHES.format(
                    time=settings.FAST,
                    recipes=recipes.filter(
                        cooking_time__gt=settings.FAST
                    ).count()
                )
            ),

        )

    def queryset(self, request, recipes):
        if self.value():
            value = int(self.value())
            if value == settings.FASTER:
                return recipes.filter(cooking_time__lte=settings.FASTER)
            if settings.FASTER < value <= settings.FAST:
                return recipes.filter(
                    cooking_time__range=(settings.FASTER, settings.FAST)
                )
            return recipes.filter(
                cooking_time__range=(
                    settings.FAST,
                    recipes
                    .aggregate(maxtime=Max('cooking_time'))['maxtime'] + 1
                )
            )
