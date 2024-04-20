from django.db import models

from . import constants


class BaseWithNameFieldModel(models.Model):
    name = models.CharField(
        max_length=constants.NAME_MAX_LENGTH
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
