from django.core.management import BaseCommand

from ._load_data import TAGS_DATA_MODEL


def tags_bulk_create():
    model = TAGS_DATA_MODEL[1]
    try:
        model.objects.bulk_create(
            model(**tags)
            for tags in TAGS_DATA_MODEL[0]
        )
    except Exception as error:
        raise Exception(
            f'Ошибка импорта тегов:'
            f'{error}'
        )


class Command(BaseCommand):
    help = 'This command imports tags'

    def handle(self, *args, **options):
        try:
            print('Начало импорта тегов...', end=' ')
            tags_bulk_create()
        except Exception as error:
            raise Exception(error)
        else:
            print('(ok)')
            print()
            print('Импорт тегов выполнен успешно')
