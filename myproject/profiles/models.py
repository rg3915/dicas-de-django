from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
