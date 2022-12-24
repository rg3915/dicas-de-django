# crm/models.py
from django.db import models

from backend.core.models import TimeStampedModel


class Person(models.Model):
    first_name = models.CharField('nome', max_length=100)
    last_name = models.CharField('sobrenome', max_length=255, null=True, blank=True)  # noqa E501
    email = models.EmailField('e-mail', max_length=50, unique=True)

    class Meta:
        abstract = True
        ordering = ('first_name',)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name or ""}'.strip()

    def __str__(self):
        return self.full_name


class Customer(Person, TimeStampedModel):
    linkedin = models.URLField(max_length=255, null=True, blank=True)
    tags = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'


class Seller(Person, TimeStampedModel):
    internal = models.BooleanField('interno', default=True)
    commission = models.DecimalField('comissão', max_digits=7, decimal_places=2, default=0)  # noqa E501

    class Meta:
        verbose_name = 'vendedor'
        verbose_name_plural = 'vendedores'


class Pessoa(models.Model):
    first_name = models.CharField('nome', max_length=100)
    last_name = models.CharField('sobrenome', max_length=255, null=True, blank=True)  # noqa E501
    email = models.EmailField('e-mail', max_length=50, unique=True)

    class Meta:
        ordering = ('first_name',)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name or ""}'.strip()

    def __str__(self):
        return self.full_name


class PF(Pessoa):
    '''
    Pessoa Física.
    É um multi-table inheritance (herança multi-tabela)
    porque a classe pai não tem abstract.
    '''
    cpf = models.CharField(max_length=11, null=True, blank=True)
    rg = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        verbose_name = 'Pessoa Física'
        verbose_name_plural = 'Pessoas Físicas'


class PJ(Pessoa):
    '''
    Pessoa Jurídica.
    '''
    cnpj = models.CharField(max_length=14, null=True, blank=True)
    ie = models.CharField('inscrição estadual', max_length=14, null=True, blank=True)  # noqa E501

    class Meta:
        verbose_name = 'Pessoa Jurídica'
        verbose_name_plural = 'Pessoas Jurídicas'
