# Generated by Django 4.1.3 on 2022-12-19 15:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookstore', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paid', models.BooleanField(default=False, verbose_name='pago')),
                ('date_paid', models.DateTimeField(blank=True, null=True, verbose_name='data de pagamento')),
                ('method', models.CharField(choices=[('di', 'dinheiro'), ('de', 'débito'), ('cr',
                 'crédito'), ('pix', 'Pix')], max_length=3, verbose_name='forma de pagamento')),
                ('deadline', models.PositiveSmallIntegerField(default=15, verbose_name='prazo de entrega')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('ordered', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                 to='bookstore.ordered', verbose_name='ordem de compra')),
            ],
            options={
                'verbose_name': 'venda',
                'verbose_name_plural': 'vendas',
                'ordering': ('-pk',),
            },
        ),
    ]
