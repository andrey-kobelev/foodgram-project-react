from django.core.management.base import BaseCommand

from ._load_data import USER_DATA_MODEL


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
        raise Exception(f'Ошибка импорта пользователей: {error}')


class Command(BaseCommand):
    help = 'This command imports users'

    def handle(self, *args, **options):
        try:
            print('Начало импорта пользователей...', end=' ')
            users_bulk_create()
        except Exception as error:
            raise Exception(error)
        else:
            print('(ok)')
            print()
            print('Импорт пользователей выполнен успешно')
