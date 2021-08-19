from django.db import models


class Room(models.Model):
    name = models.CharField('nome', max_length=100, unique=True)
    num_participants = models.PositiveSmallIntegerField('quantidade de participantes')  # noqa E501
    num_chairs = models.PositiveSmallIntegerField('quantidade de cadeiras')

    class Meta:
        ordering = ('name',)
        verbose_name = 'sala'
        verbose_name_plural = 'salas'

    def __str__(self):
        return self.name
