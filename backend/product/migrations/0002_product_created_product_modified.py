# Generated by Django 4.1.3 on 2023-02-19 10:21

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='criado em'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modificado em'),
        ),
    ]
