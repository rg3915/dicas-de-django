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


METHOD_PAYMENT = (
    ('di', 'dinheiro'),
    ('de', 'débito'),
    ('cr', 'crédito'),
    ('pix', 'Pix'),
)


class Sale(models.Model):
    ordered = models.OneToOneField(
        Ordered,
        on_delete=models.CASCADE,
        verbose_name='ordem de compra'
    )
    paid = models.BooleanField('pago', default=False)
    date_paid = models.DateTimeField('data de pagamento', null=True, blank=True)
    method = models.CharField('forma de pagamento', max_length=3, choices=METHOD_PAYMENT)  # noqa E501
    deadline = models.PositiveSmallIntegerField('prazo de entrega', default=15)
    created = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'venda'
        verbose_name_plural = 'vendas'

    def __str__(self):
        if self.ordered:
            return f'{str(self.pk).zfill(3)}-{self.ordered}'

        return f'{str(self.pk).zfill(3)}'


class Author(models.Model):
    first_name = models.CharField('nome', max_length=100)
    last_name = models.CharField('sobrenome', max_length=255, null=True, blank=True)  # noqa E501

    class Meta:
        ordering = ('first_name',)
        verbose_name = 'autor'
        verbose_name_plural = 'autores'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name or ""}'.strip()

    def __str__(self):
        return self.full_name


class Book(models.Model):
    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField('título', max_length=255)
    rating = models.DecimalField('pontuação', max_digits=5, decimal_places=2, default=5)
    authors = models.ManyToManyField(
        Author,
        verbose_name='autores',
        blank=True
    )
    price = models.DecimalField('preço', max_digits=5, decimal_places=2)
    stock_min = models.PositiveSmallIntegerField(default=0)
    stock = models.PositiveSmallIntegerField(default=0)
    publisher = models.ForeignKey(
        'Publisher',
        on_delete=models.SET_NULL,
        verbose_name='editora',
        related_name='books',
        null=True,
        blank=True
    )
    created = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )
    modified = models.DateTimeField(
        'modificado em',
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'livro'
        verbose_name_plural = 'livros'

    def __str__(self):
        return f'{self.title}'


class Store(models.Model):
    name = models.CharField('nome', max_length=255)
    books = models.ManyToManyField(
        Book,
        verbose_name='livros',
        blank=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'loja'
        verbose_name_plural = 'lojas'

    def __str__(self):
        return f'{self.name}'


class Publisher(models.Model):
    name = models.CharField('nome', max_length=255)

    class Meta:
        ordering = ('name',)
        verbose_name = 'editora'
        verbose_name_plural = 'editoras'

    def __str__(self):
        return f'{self.name}'
