# Generated by Django 3.2.13 on 2024-04-15 17:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_log_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='intensity',
            field=models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(0)]),
        ),
    ]
