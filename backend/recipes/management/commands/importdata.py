from django.core.management.base import BaseCommand

from ._data import DATA_MODEL


def data_bulk_create():
    try:
        for datas, model in DATA_MODEL:
            model.objects.bulk_create(
                model(**data)
                for data in datas
            )
    except Exception as error:
        print(
            f'Произошла ошибка при создании объектов:'
            f'{error}'
        )


class Command(BaseCommand):
    help = 'This command populates the database'

    def handle(self, *args, **options):
        try:
            print('START!')
            data_bulk_create()
        except Exception as error:
            raise Exception(error)
        else:
            print('FINISH!')
