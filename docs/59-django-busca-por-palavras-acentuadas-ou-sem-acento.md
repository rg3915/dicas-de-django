# Dica 59 - Django: Busca por palavras acentuadas ou sem acento

<a href="https://youtu.be/rMW562J6tGE">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github do projeto: [https://github.com/rg3915/django-postgresql-docker](https://github.com/rg3915/django-postgresql-docker)

Busca sem acento

[https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/lookups/](https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/lookups/)

## Rodar o PostgreSQL via Docker

```
docker-compose up -d

docker container exec -it db psql

\c db

CREATE EXTENSION unaccent;

\q
```

Edite `settings.py`

```python
INSTALLED_APPS = [
    ...
    'django.contrib.postgres',
    ...
]
```

## Adicionar artigos pelo shell_plus

`python manage.py shell_plus`

```python
artigos = [
    ('Filmes', 'Conheça os filmes de ação de 2021'),
    ('Gastronomia', 'Conheça os melhores pratos da França'),
    ('Livros', 'Inteligência emocional'),
    ('Café', 'Café frappé ou café frapê é um café solúvel gelado'),
]

aux_list = []
for artigo in artigos:
    obj = Article(
        title=artigo[0],
        subtitle=artigo[1]
    )
    aux_list.append(obj)

Article.objects.bulk_create(aux_list)
```


## Criar campo de busca

Edite `core/article_list.html`

```html
<h1>Lista de {\% model_name_plural model %}</h1>

<form class="form-inline my-2">
  <label>Busca</label>
  <input class="form-control ml-sm-2" name="search" type="text"/>
  <button class="btn btn-primary my-2 my-sm-0" type="submit">OK</button>
  <a href=".">Limpar</a>
</form>

```

## Fazendo a busca com ou sem acento

Edite `core/views.py`

```python
from django.db.models import Q


def article_list(request):
    template_name = 'core/article_list.html'
    object_list = Article.objects.all()

    search = request.GET.get('search')

    if search:
        object_list = object_list.filter(
            Q(title__unaccent__icontains=search) |
            Q(subtitle__unaccent__icontains=search)
        )
    ...
```

Reinicie o servidor.

`python manage.py runserver`

