from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriber'
    )
    subscribing = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribing'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribing'],
                name='unique_name_subscribing'
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.subscribing}'
