# Generated by Django 4.1.3 on 2022-12-24 08:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expense', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Financial',
        ),
        migrations.DeleteModel(
            name='Expense',
        ),
        migrations.DeleteModel(
            name='Receipt',
        ),
    ]
