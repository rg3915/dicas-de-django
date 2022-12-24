from django.db import models


class Customer(models.Model):
    first_name = models.CharField('nome', max_length=100)
    last_name = models.CharField('sobrenome', max_length=255, null=True, blank=True)
    email = models.EmailField('e-mail', max_length=50, unique=True)
    active = models.BooleanField('ativo', default=True)

    class Meta:
        ordering = ('first_name',)
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name or ""}'.strip()

    def __str__(self):
        return self.full_name


STATUS = (
    ('p', 'Pendente'),
    ('a', 'Aprovado'),
    ('c', 'Cancelado'),
)


class Ordered(models.Model):
    status = models.CharField(max_length=1, choices=STATUS, default='p')
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        verbose_name='cliente',
        related_name='ordereds',
        null=True,
        blank=True
    )
    created = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'ordem de compra'
        verbose_name_plural = 'ordens de compra'

    def __str__(self):
        if self.customer:
            return f'{str(self.pk).zfill(3)}-{self.customer}'

        return f'{str(self.pk).zfill(3)}'
