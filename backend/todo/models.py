from django.db import models

from backend.core.models import TimeStampedModel


class Todo(TimeStampedModel):
    task = models.CharField('tarefa', max_length=100)
    done = models.BooleanField('feita', default=False)

    class Meta:
        ordering = ('task',)
        verbose_name = 'tarefa'
        verbose_name_plural = 'tarefas'

    def __str__(self):
        return f'{self.task}'

    def to_dict(self):
        return {
            'id': self.id,
            'task': self.task,
            'done': self.done,
        }
