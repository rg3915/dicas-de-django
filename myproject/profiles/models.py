from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    cpf = models.CharField('CPF', max_length=11, unique=True, null=True, blank=True)  # noqa E501
    rg = models.CharField('RG', max_length=20, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('cpf',)
        verbose_name = 'perfil'
        verbose_name_plural = 'perfis'

    def __str__(self):
        if self.cpf:
            return self.cpf
        return self.user.get_full_name()
