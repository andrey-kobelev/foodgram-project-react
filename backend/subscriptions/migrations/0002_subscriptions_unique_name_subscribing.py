# Generated by Django 3.2.16 on 2024-04-30 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='subscriptions',
            constraint=models.UniqueConstraint(fields=('user', 'subscribing'), name='unique_name_subscribing'),
        ),
    ]
