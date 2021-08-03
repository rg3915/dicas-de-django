# 41 - django-seed

<a href="">
    <img src="../.gitbook/assets/youtube.png">
</a>


O [django-seed](https://github.com/Brobin/django-seed) é uma lib para que gera dados aleatórios para o seu modelo de uma forma rápida e simples.

```
pip install django-seed
```

Adicione em `INSTALLED_APPS` em `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'django_seed',
]
```

E depois simplesmente rode o comando

```
python manage.py seed travel --number=15
```

onde `travel` é o nome da nossa app neste projeto.

