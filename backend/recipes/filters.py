from django.contrib.admin import SimpleListFilter
from django.db.models import Max, Min, Q

from . import models


SUBSCRIBING = 'with-subscribing'
SUBSCRIBERS = 'with-subscribers'
FAST_DISHES = 'Быстрые за {time} мин. ({recipes})'
LONGTIME_DISHES = 'Долго, {time} мин. ({recipes})'


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
        mintime = recipes.aggregate(mintime=Min('cooking_time'))['mintime']
        maxtime = recipes.aggregate(maxtime=Max('cooking_time'))['maxtime']
        midtime = recipes.filter(
            Q(cooking_time__gt=mintime)
            & Q(cooking_time__lt=maxtime)
        ).aggregate(midtime=Min('cooking_time'))['midtime']
        return (
            (
                mintime,
                FAST_DISHES.format(
                    time=mintime,
                    recipes=recipes.filter(
                        cooking_time=mintime
                    ).count()
                )
            ),
            (
                midtime,
                FAST_DISHES.format(
                    time=midtime,
                    recipes=recipes.filter(
                        cooking_time=midtime
                    ).count()
                )
            ),
            (
                maxtime,
                LONGTIME_DISHES.format(
                    time=maxtime,
                    recipes=recipes.filter(
                        cooking_time=maxtime
                    ).count()
                )
            ),

        )

    def queryset(self, request, recipes):
        if not self.value() or not self.value().isdigit():
            return recipes
        return recipes.filter(
            cooking_time=int(self.value())
        )
