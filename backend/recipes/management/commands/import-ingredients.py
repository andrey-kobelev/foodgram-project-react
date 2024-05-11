from django.core.management import BaseCommand

from ._load_data import INGREDIENTS_DATA_MODEL


def ingredients_bulk_create():
    try:
        for datas, model in INGREDIENTS_DATA_MODEL:
            model.objects.bulk_create(
                model(**data)
                for data in datas
            )
    except Exception as error:
        raise Exception(
            f'Ошибка импорта ингредиентов:'
            f'{error}'
        )


class Command(BaseCommand):
    help = 'This command imports ingredients'

    def handle(self, *args, **options):
        try:
            print('Начало импорта ингредиентов...', end=' ')
            ingredients_bulk_create()
        except Exception as error:
            raise Exception(error)
        else:
            print('(ok)')
            print()
            print('Импорт ингредиентов выполнен успешно')
