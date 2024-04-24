from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    @property
    def is_admin(self):
        return self.is_superuser

    class Meta:
        ordering = ('email',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
