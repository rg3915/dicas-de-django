# Dica 59 - Django: Busca por palavras acentuadas ou sem acento

**Versões usadas no vídeo:** Django 4.0, Python 3.8, PostgreSQL 13.4 (imagem `postgres:13.4-alpine`) e Bootstrap 4.0.
{: .versoes }

<a href="https://youtu.be/rMW562J6tGE">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`). Se copiar código de lá, remova a `\`.

![](../.gitbook/assets/tags.png)


Github do projeto: [https://github.com/rg3915/django-postgresql-docker](https://github.com/rg3915/django-postgresql-docker)

Busca sem acento

[https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/lookups/](https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/lookups/)

Documentação citada na descrição do vídeo: [https://docs.djangoproject.com/en/4.0/ref/contrib/postgres/lookups/](https://docs.djangoproject.com/en/4.0/ref/contrib/postgres/lookups/)

Quem nunca procurou "cafe" e não achou "café"? Nesta dica vamos fazer uma busca que ignora a acentuação: procurar `frappe` encontra "frappé" e "frapê", `acao` encontra "ação" e `inteligencia` encontra "Inteligência". Para isso usamos o lookup `unaccent` do Django, que existe só para o **PostgreSQL**: ele usa a extensão `unaccent` do banco para remover os acentos antes de comparar. No SQLite isso não funciona.

## Pré-requisitos

Continuamos o projeto da [Dica 58 - Rodando PostgreSQL com Docker + Portainer + pgAdmin + Django local](058-rodando-postgresql-com-docker.md): o PostgreSQL rodando no container `db` (porta 5433 na máquina), o Django rodando localmente e a app `backend.core`.

Nesse projeto a app `core` tem um modelo `Article`, com título e sub-título:

```python
# backend/core/models.py
from django.db import models


class Article(models.Model):
    title = models.CharField('título', max_length=100)
    subtitle = models.CharField('sub-título', max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'artigo'
        verbose_name_plural = 'artigos'

    def __str__(self):
        return f'{self.title}'
```

As rotas:

```python
# backend/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('backend.core.urls', namespace='core')),
    path('admin/', admin.site.urls),
]
```

```python
# backend/core/urls.py
from django.urls import path

from backend.core import views as v

app_name = 'core'

urlpatterns = [
    path('', v.index, name='index'),
    path('articles/', v.article_list, name='article_list'),
]
```

E os templates usam o Bootstrap 4, com um `base.html` e uma barra de navegação com os links **Home** e **Artigos**:

```html
<!-- backend/core/templates/base.html -->
{% load static %}
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="shortcut icon" href="https://www.djangoproject.com/favicon.ico">
  <!-- Bootstrap core CSS -->
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
  <!-- Font-awesome -->
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
  <title>Dicas de Django</title>

  <link rel="stylesheet" href="{% static 'css/style.css' %}">

  {% block css %}{% endblock css %}

  <style>
    body {
      margin-top: 60px;
    }
  </style>
</head>

<body>
  <div class="container">

    {% include "nav.html" %}

    {% block content %}{% endblock content %}
  </div>

  <!-- jQuery -->
  <script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>

  <script src="{% static 'js/main.js' %}"></script>

  {% block js %}{% endblock js %}

</body>

</html>
```

```html
<!-- backend/core/templates/nav.html -->
<nav class="navbar navbar-expand-md navbar-dark bg-dark fixed-top">
    <a class="navbar-brand" href="{% url 'core:index' %}">Dicas de Django</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarsExampleDefault" aria-controls="navbarsExampleDefault" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbarsExampleDefault">
        <ul class="navbar-nav mr-auto">
            <li class="nav-item active">
                <a class="nav-link" href="{% url 'core:index' %}">Home <span class="sr-only">(current)</span></a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="{% url 'core:article_list' %}">Artigos</a>
            </li>
        </ul>
    </div>
</nav>
```

Se estiver montando o projeto agora, rode `python manage.py makemigrations` e `python manage.py migrate` depois de criar o modelo.

## Rodar o PostgreSQL via Docker e criar a extensão unaccent

Suba o container, se ainda não estiver rodando, e confira:

```bash
docker-compose up -d
docker container ls
```

Entre no `psql` do container `db`, conecte-se ao banco `db` e crie a extensão `unaccent`:

```bash
docker container exec -it db psql
```

```
psql (13.4)
Type "help" for help.

postgres=# \c db
You are now connected to database "db" as user "postgres".
db=# CREATE EXTENSION unaccent;
CREATE EXTENSION
db=# \q
```

A extensão é criada uma vez por banco. Sem ela, a busca com `unaccent` dá erro, porque a função `UNACCENT` não existe no banco.

## Edite settings.py

O lookup `unaccent` faz parte do `django.contrib.postgres`, que precisa estar no `INSTALLED_APPS`:

```python
# backend/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    # 3rd apps
    'django_extensions',
    # my apps
    'backend.core',
]
```

## Adicionar artigos pelo shell_plus

Vamos cadastrar alguns artigos com palavras acentuadas. Abra o shell do django-extensions:

```bash
python manage.py shell_plus
```

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

Saída:

```
[<Article: Filmes>, <Article: Gastronomia>, <Article: Livros>, <Article: Café>]
```

O `bulk_create` grava todos os objetos da lista numa única consulta. Saia com `Ctrl+D`.

## Criar campo de busca

O template da lista já tem um formulário de busca com um campo chamado `search`. Como o formulário não define `method`, ele faz um GET, e o texto digitado vai para a URL como `?search=...`. O link **Limpar** volta para a lista sem filtro.

```html
<!-- backend/core/templates/core/article_list.html -->
{% extends "base.html" %}

{% block content %}
  <div class="row">
    <div class="col-md-4">
      <h1>Lista de Artigos</h1>
    </div>
    <div class="col-md-8">
      <form class="form-inline my-2">
        <label>Busca</label>
        <input class="form-control ml-sm-2" name="search" type="text"/>
        <button class="btn btn-primary my-2 my-sm-0" type="submit">OK</button>
        <a href=".">Limpar</a>
      </form>
    </div>
  </div>

  <div class="row">
    <div class="col-md-12">
      <table class="table">
        <thead>
          <tr>
            <th>Título</th>
            <th>Sub-título</th>
          </tr>
        </thead>
        <tbody>
          {% for obj in object_list %}
            <tr>
              <td>{{ obj.title }}</td>
              <td>{{ obj.subtitle|default:"---" }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
{% endblock content %}
```

Rode o servidor e abra [http://localhost:8000/articles/](http://localhost:8000/articles/):

```bash
python manage.py runserver
```

A lista mostra os quatro artigos, ordenados pelo título. Inspecionando o elemento, confirme que o `input` se chama `search`: é esse nome que vamos ler na view.

## Fazendo a busca com ou sem acento

Edite a view:

```python
# backend/core/views.py
from django.shortcuts import render
from django.db.models import Q


from .models import Article


def index(request):
    template_name = 'index.html'
    return render(request, template_name)


def article_list(request):
    template_name = 'core/article_list.html'
    object_list = Article.objects.all()

    search = request.GET.get('search')

    if search:
        object_list = object_list.filter(
            Q(title__unaccent__icontains=search) |
            Q(subtitle__unaccent__icontains=search)
        )

    context = {'object_list': object_list}
    return render(request, template_name, context)
```

* `request.GET.get('search')` lê o texto da busca; se não houver busca, devolve `None` e a lista fica completa.
* `title__unaccent__icontains=search` encadeia dois lookups: `unaccent` tira os acentos do campo **e** do texto buscado, e `icontains` procura o texto em qualquer parte, sem diferenciar maiúsculas de minúsculas.
* Os objetos `Q` combinados com `|` fazem um OR: o artigo aparece se o texto estiver no título **ou** no sub-título.

O SQL gerado mostra o que acontece no banco:

```sql
SELECT "core_article"."id", "core_article"."title", "core_article"."subtitle"
  FROM "core_article"
 WHERE UPPER(UNACCENT("core_article"."title")::text) LIKE '%' || UPPER(... (UNACCENT('cafe')) ...) || '%'
 ORDER BY "core_article"."title" ASC
```

Reinicie o servidor.

```bash
python manage.py runserver
```

## Testando a busca

Repare nas palavras cadastradas: "Café" com acento, "frappé" com acento agudo, "frapê" com circunflexo, "solúvel", "ação" com til e cedilha, "França" com cedilha e "Inteligência" com circunflexo. Agora:

| Busca | Resultado |
| --- | --- |
| `frappe` | Café (Café frappé ou café frapê é um café solúvel gelado) |
| `café` | Café |
| `acao` | Filmes (Conheça os filmes de ação de 2021) |
| `inteligencia` | Livros (Inteligência emocional) |
| `inteligência` | Livros |

Com ou sem acento, a busca encontra os artigos. Para comparar, sem o `__unaccent` (`title__icontains=search`), as buscas `frappe`, `acao` e `inteligencia` não encontram nada.

## Conclusão

Com o PostgreSQL, buscar ignorando acentos é simples: crie a extensão `unaccent` no banco, coloque `django.contrib.postgres` no `INSTALLED_APPS` e use o lookup `__unaccent` antes do `__icontains`. A documentação também mostra o `TrigramExtension` e o lookup `trigram_similar`, para buscas por similaridade.

Observação: em vez de rodar `CREATE EXTENSION unaccent;` à mão no `psql`, dá para criar a extensão numa migration com a operação `UnaccentExtension()`, de `django.contrib.postgres.operations`. Assim ela é criada automaticamente em qualquer banco onde o projeto rodar, inclusive no banco de testes.
