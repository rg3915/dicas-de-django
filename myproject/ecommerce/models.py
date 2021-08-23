from django.db import models
from django.db.models import F, Sum

from myproject.core.models import TimeStampedModel
from myproject.product.models import Product


class Order(TimeStampedModel):
    nf = models.CharField('nota fiscal', max_length=100, unique=True)

    class Meta:
        ordering = ('nf',)
        verbose_name = 'ordem de compra'
        verbose_name_plural = 'ordens de compra'

    def __str__(self):
        return self.nf

    def total(self):
        return round(self.order_items.aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0, 2)  # noqa E501


class OrderItems(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        verbose_name='ordem',
        related_name='order_items',
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        verbose_name='produto',
        related_name='product_items',
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField('quantidade')
    price = models.DecimalField('preço', max_digits=7, decimal_places=2)

    class Meta:
        ordering = ('pk',)

    def __str__(self):
        return f'{self.pk} - {self.order.pk} - {self.product}'

    def get_subtotal(self):
        return self.quantity * self.price
