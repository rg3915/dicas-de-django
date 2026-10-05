# Dica 43 - django-admin-rangefilter

**Versões usadas no vídeo:** Django 3.2.6, django-admin-rangefilter 0.8.1 e Python 3.9.6.
{: .versoes }

<a href="https://youtu.be/GalpHaLJK3Q">
    <img src="../.gitbook/assets/youtube.png">
</a>


https://github.com/silentsokolov/django-admin-rangefilter

Na [Dica 5](005-django-admin-date-range-filter.md) usamos a biblioteca **django-daterange-filter** para filtrar por intervalo de datas no Admin do Django. Ao atualizar o projeto para o Django 3.2.6, essa biblioteca simplesmente parou de funcionar. No lugar dela vamos usar a **django-admin-rangefilter**, que faz a mesma coisa (dois campos de data com calendário no filtro lateral do Admin) e ainda tem um filtro para data **e hora**.

Neste tutorial vamos:

* atualizar o projeto do Django 2.2 para o 3.2.6;
* trocar o `django-daterange-filter` pelo `django-admin-rangefilter`;
* corrigir o que quebrou na atualização (`asgi.py`, `apps.py`, `settings.py` e duas bibliotecas incompatíveis);
* usar o `DateRangeFilter` e o `DateTimeRangeFilter` no Admin de artigos.

## Pré-requisitos

O vídeo usa o projeto do repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django) (pasta `myproject`), que até aqui estava no Django 2.2 e usava o `django-daterange-filter` no Admin do model `Article` (app `core`), como na Dica 5.

## Atualizando o Django e instalando a biblioteca

Atualize o Django para a versão mais recente (no vídeo, a 3.2.6) e instale a nova biblioteca:

```bash
pip install -U django
pip install django-admin-rangefilter
pip freeze
```

No `pip freeze` aparecem `Django==3.2.6` e `django-admin-rangefilter==0.8.1`. No `requirements.txt`, troque a linha do `django-daterange-filter` pela nova biblioteca e atualize a linha do Django:

```
# requirements.txt (trecho)
django-admin-rangefilter==0.8.1
...
Django==3.2.*
```

O `requirements.txt` completo do projeto, depois da troca, ficou assim:

```
# requirements.txt
bitbucket-python==0.2.2
click==7.1.2
clint==0.5.1
dj-database-url==0.5.0
django-autoslug==1.9.7
django-admin-rangefilter==0.8.1
django-debug-toolbar==2.2.1
django-extensions==2.2.9
django-filter==2.3.0
django-hashid-field==3.1.3
django-seed==0.2.2
django-widget-tweaks==1.4.8
Django==3.2.*
Faker==8.7.0
hashids==1.2.0
progress==1.5
progressbar2==3.53.1
python-dateutil==2.8.1
python-decouple==3.3
python-gitlab==2.4.0
requests==2.24.0
shortuuid==1.0.1
tqdm==4.55.2
```

## O que quebra na atualização

Rodando `python manage.py makemigrations` logo depois da atualização, aparecem dois erros, um de cada biblioteca antiga.

O `django-autoslug` 1.9.7 importa de um lugar que não existe mais:

```
ImportError: cannot import name 'FieldDoesNotExist' from 'django.db.models.fields'
```

E o `django-daterange-filter` também:

```
ModuleNotFoundError: No module named 'django.contrib.admin.templatetags.admin_static'
```

O `admin_static` foi removido no Django 3.0, e o `FieldDoesNotExist` deixou de ser importável de `django.db.models.fields` no Django 3.1. O `django-daterange-filter` vamos trocar; o `AutoSlugField` vamos só comentar por enquanto, porque ele não é necessário nesta dica.

Além disso, um projeto criado no Django 2.2 precisa de alguns ajustes para o 3.2, que vemos a seguir.

## Criando o asgi.py

Projetos criados a partir do Django 3.0 têm um arquivo `asgi.py` ao lado do `wsgi.py`. O nosso projeto foi criado no 2.2, então ele não existe. Crie o arquivo:

```bash
cd myproject
touch asgi.py
cd ..
```

```python
# myproject/asgi.py
"""
ASGI config for myproject project.
It exposes the ASGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

application = get_asgi_application()
```

## Ajustando o apps.py dos apps

Os apps ficam dentro da pasta `myproject`, e no `INSTALLED_APPS` eles são registrados como `myproject.core` e `myproject.travel`. No Django 3.2, o `name` do `AppConfig` precisa ser o caminho completo do app:

```python
# myproject/core/apps.py
from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'myproject.core'
```

```python
# myproject/travel/apps.py
from django.apps import AppConfig


class TravelConfig(AppConfig):
    name = 'myproject.travel'
```

## Ajustando o settings.py

Em `INSTALLED_APPS`, troque o `'daterange_filter'` por `'rangefilter'` (aproveitamos para separar as bibliotecas de terceiros dos nossos apps com comentários):

```python
# myproject/settings.py
INSTALLED_APPS = [
    'myproject.core',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd partys
    'debug_toolbar',
    'django_extensions',
    'rangefilter',
    'django_filters',
    'django_seed',
    # my apps
    'myproject.travel',
]
```

Mude o idioma e o fuso horário, para que o Admin (e os calendários do filtro) fiquem em português:

```python
# myproject/settings.py
LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'
```

E, no final do arquivo, defina o tipo padrão da chave primária, novidade do Django 3.2 (sem isso, o Django mostra um aviso para cada model):

```python
# myproject/settings.py
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

## Ajustando o models.py

Em `core/models.py`, comente o import e o campo do `AutoSlugField`. Aproveite e crie um model abstrato `TimeStampedModel`, com os campos `created` e `modified`, e faça o `Article` herdar dele. Assim teremos um campo de data e hora (`modified`) para testar o `DateTimeRangeFilter`.

```python
# myproject/core/models.py
import uuid

# from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.db import models
from hashid_field import HashidAutoField


class TimeStampedModel(models.Model):
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
        abstract = True

# ... (veja o arquivo completo no GitHub)


class Article(TimeStampedModel):
    id = HashidAutoField(primary_key=True, salt='dicas')
    title = models.CharField('título', max_length=200)
    subtitle = models.CharField('sub-título', max_length=200)
    # slug = AutoSlugField(populate_from='title')
    # ... (veja o arquivo completo no GitHub)
```

Código completo: [myproject/core/models.py](https://github.com/rg3915/dicas-de-django/blob/9f7edc791f3ebe2b18443883941eae14ba9d88c5/myproject/core/models.py)

Os demais models do arquivo (`Category`, `Person`) continuam iguais.

## Usando o rangefilter no Admin

Em `core/admin.py`, troque o import antigo (`from daterange_filter.filter import DateRangeFilter`) pelo da nova biblioteca:

```python
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
```

No `ArticleAdmin`:

* o `published_date` continua com o `DateRangeFilter` (só data);
* o `modified` ganha o `DateTimeRangeFilter` (data e hora);
* o `slug` sai do `list_display` e o `readonly_fields` fica comentado, porque comentamos o campo `slug` no model.

```python
# myproject/core/admin.py
from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter

from .models import Article, Category, Person

# from .forms import ArticleAdminForm


admin.site.login_template = 'myproject/core/templates/admin/login.html'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'get_published_date',
        'get_category',
        'status'
    )
    search_fields = ('title',)
    list_filter = (
        ('published_date', DateRangeFilter),
        ('modified', DateTimeRangeFilter),
        'category',
        'status',
    )
    # readonly_fields = ('slug',)
    date_hierarchy = 'published_date'
    # form = ArticleAdminForm
    list_editable = ('title', 'status')
    actions = ('make_published',)

    ...
```

O resto da classe (as actions, o `get_published_date`, o `get_category`, o `get_urls` etc.) não muda.

No `list_filter`, cada filtro de intervalo é uma tupla `('nome_do_campo', ClasseDoFiltro)`. Os outros itens (`'category'`, `'status'`) continuam sendo os filtros normais do Admin.

## Recriando o banco e as migrations

Como mexemos em vários models (campo comentado, model abstrato novo) e o histórico de migrations tinha vários merges, no vídeo foi feito o caminho radical: apagar o banco e as migrations e começar do zero. **Só faça isso num projeto de estudo**; em produção você perderia os dados.

```bash
rm -f db.sqlite3
cd myproject/
rm -rf core/migrations
rm -rf travel/migrations
mkdir -p core/migrations
mkdir -p travel/migrations
touch core/migrations/__init__.py
touch travel/migrations/__init__.py
cd ..
python manage.py makemigrations
python manage.py migrate
```

Saída do `migrate` (trecho):

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, core, sessions, travel
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying core.0001_initial... OK
  Applying sessions.0001_initial... OK
  Applying travel.0001_initial... OK
```

Crie um superusuário e suba o servidor:

```bash
python manage.py createsuperuser
python manage.py runserver
```

## Resultado

Entre em `http://localhost:8000/admin/core/article/`, cadastre alguns artigos e veja o filtro lateral:

* **criado em** (`published_date`, com `DateRangeFilter`): campos "Data inicial" e "Data final", com calendário, e os botões **Pesquisar** e **Limpar**;
* **modificado em** (`modified`, com `DateTimeRangeFilter`): para o início e para o fim, um campo de **Data** e um de **Hora**, com calendário e relógio.

Basta preencher o intervalo e clicar em **Pesquisar** para listar só os artigos daquele período.

Observação: o `django-autoslug` ficou comentado no vídeo porque a versão 1.9.7 não funciona no Django 3.1 ou mais novo. Versões mais novas da biblioteca já corrigiram isso.
