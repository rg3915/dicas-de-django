import uuid
from django.db import models
from autoslug import AutoSlugField
from hashid_field import HashidAutoField
from django.contrib.auth.models import User


class UuidModel(models.Model):
    slug = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


STATUS_CHOICES = (
    ('d', 'Rascunho'),
    ('p', 'Publicado'),
    ('w', 'Retirado'),
)


class Article(models.Model):
    id = HashidAutoField(primary_key=True, salt='dicas')
    title = models.CharField('título', max_length=200)
    subtitle = models.CharField('sub-título', max_length=200)
    slug = AutoSlugField(populate_from='title')
    category = models.ForeignKey(
        'Category',
        related_name='categories',
        verbose_name='categoria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    published_date = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'artigo'
        verbose_name_plural = 'artigos'

    def __str__(self):
        return self.title


class Category(UuidModel):
    title = models.CharField('título', max_length=50, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.title
