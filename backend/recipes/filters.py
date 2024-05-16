from django.contrib.admin import SimpleListFilter

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
        try:
            recipes = (model_admin.get_queryset(request))
            times = recipes.values_list('cooking_time', flat=True)
            if len(times) < 3:
                return None
            midtimes = [
                time
                for time in times
                if min(times) < time < max(times)
            ]
            mintimes = [
                time
                for time in times
                if time < min(midtimes)
            ]
            maxtimes = [
                time
                for time in times
                if time > max(midtimes)
            ]
            return (
                (
                    ','.join(map(str, mintimes)),
                    FAST_DISHES.format(
                        time=max(mintimes),
                        recipes=recipes.filter(
                            cooking_time__in=mintimes
                        ).count()
                    )
                ),
                (
                    ','.join(map(str, midtimes)),
                    FAST_DISHES.format(
                        time=max(midtimes),
                        recipes=recipes.filter(
                            cooking_time__in=midtimes
                        ).count()
                    )
                ),
                (
                    ','.join(map(str, maxtimes)),
                    LONGTIME_DISHES.format(
                        time=max(maxtimes),
                        recipes=recipes.filter(
                            cooking_time__in=maxtimes
                        ).count()
                    )
                ),

            )
        except ValueError:
            return None

    def queryset(self, request, recipes):
        if not self.value():
            return recipes
        return recipes.filter(
            cooking_time__in=self.value().split(',')
        )
