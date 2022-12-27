from django.db import models

from .managers import RentManager, SaleManager

TYPE_OF_NEGOTIATION = (
    ('a', 'aluguel'),
    ('v', 'venda'),
)


class Realty(models.Model):
    name = models.CharField('nome', max_length=255)
    type_of_negotiation = models.CharField(
        'tipo de negociação',
        max_length=1,
        choices=TYPE_OF_NEGOTIATION,
    )
    price = models.DecimalField('preço', max_digits=12, decimal_places=2)

    class Meta:
        ordering = ('name',)
        verbose_name = 'imóvel'
        verbose_name_plural = 'imóveis'

    def __str__(self):
        return f'{self.name}'


class PropertyRent(Realty):

    objects = RentManager()

    class Meta:
        proxy = True
        verbose_name = 'aluguel'
        verbose_name_plural = 'aluguéis'

    def save(self, *args, **kwargs):
        self.type_of_negotiation = 'a'
        super(PropertyRent, self).save(*args, **kwargs)


class PropertySale(Realty):

    objects = SaleManager()

    class Meta:
        proxy = True
        verbose_name = 'venda'
        verbose_name_plural = 'vendas'

    def save(self, *args, **kwargs):
        self.type_of_negotiation = 'v'
        super(PropertySale, self).save(*args, **kwargs)
