from django.db import models
from django.urls import reverse_lazy

from backend.core.models import TimeStampedModel


class Category(models.Model):
    title = models.CharField('título', max_length=255, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return f'{self.title}'


class Product(TimeStampedModel):
    title = models.CharField('título', max_length=255, unique=True)
    description = models.TextField('descrição', null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='categoria',
        related_name='products',
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse_lazy('product:product_detail', kwargs={'pk': self.pk})


class Photo(TimeStampedModel):
    photo = models.ImageField(upload_to='')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        ordering = ('pk',)
        verbose_name = 'foto'
        verbose_name_plural = 'fotos'

    def __str__(self):
        return f'{self.pk}'
