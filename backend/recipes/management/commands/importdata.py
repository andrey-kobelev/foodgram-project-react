from django.core.management.base import BaseCommand

from ._data import (TAG_INGREDIENT_DATA_MODEL,
                    RECIPES,
                    USER_DATA_MODEL,
                    create_ingredients_tags,
                    get_user)
from recipes.models import Recipe


def tags_ingredients_bulk_create():
    try:
        for datas, model in TAG_INGREDIENT_DATA_MODEL:
            model.objects.bulk_create(
                model(**data)
                for data in datas
            )
    except Exception as error:
        raise Exception(
            f'Ошибка при создании тегов, ингредиентов:'
            f'{error}'
        )


def users_bulk_create():
    try:
        for data, model in USER_DATA_MODEL:
            for user_data in data:
                password = user_data.pop('password')
                user = model.objects.create(
                    **user_data
                )
                user.set_password(password)
                user.save()
    except Exception as error:
        raise Exception(f'Ошибка при создании пользователей: {error}')


def recipes_bulk_create():
    try:
        for recip_data in RECIPES:
            recip_data['author'] = get_user(recip_data['author'])
            recipe = Recipe.objects.create(
                **recip_data
            )
            create_ingredients_tags(recipe=recipe)
    except Exception as error:
        raise Exception(f'Ошибка при создании рецептов: {error}')


class Command(BaseCommand):
    help = 'This command populates the database'

    def handle(self, *args, **options):
        try:
            print('START!')
            users_bulk_create()
            tags_ingredients_bulk_create()
            recipes_bulk_create()
        except Exception as error:
            raise Exception(error)
        else:
            print('FINISH!')
            print()
            print('База данных наполнена нужными данными. Наслаждайтесь =))')
