# Dica 1 - Django boilerplate e cookiecutter-django

**Versões usadas no vídeo:** Python 3.8.2; Django 2.2.13 (boilerplatesimple.sh), Django 2.2.12 com Bootstrap 3 (boilerplate2.sh) e Django 3.0 (cookiecutter-django de junho de 2020).
{: .versoes }

<a href="https://youtu.be/OYcOpcPcp8Y">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas próximas dicas, troque

![](../.gitbook/assets/tags.png)

Ou seja, remova a `\` no meio das tags. (Isso era necessário quando o site era feito com o GitBook; hoje as tags de template já aparecem normais, como `{% block content %}`.)

Começar um projeto Django do zero sempre passa pelas mesmas tarefas: criar a virtualenv, instalar o Django e as bibliotecas de sempre, rodar o `startproject`, criar um app, tirar a `SECRET_KEY` do `settings.py`, configurar o banco, as URLs, o superusuário... Um **boilerplate** é um esqueleto pronto que faz tudo isso de uma vez, para você já começar escrevendo o código da sua aplicação.

Nesta primeira dica vamos ver três opções, da mais simples para a mais completa:

1. [boilerplatesimple.sh](https://gist.github.com/rg3915/b363f5c4a998f42901705b23ccf4b8e8): um shell script que cria um projeto Django mínimo, com `settings.py` configurado e um app `core` vazio.
2. [boilerplate2.sh](https://gist.github.com/rg3915/a264d0ade860d2f2b4bf): um shell script que cria um projeto completo, com um cadastro de contatos (CRUD), templates, testes, Selenium e dados de exemplo.
3. [cookiecutter-django](https://github.com/pydanny/cookiecutter-django): o boilerplate "profissional" criado pelo Daniel Roy Greenfeld (pydanny), com PostgreSQL, cadastro de usuários com confirmação de e-mail, debug toolbar e muito mais.

Depois deste vídeo, o boilerplate virou um repositório: [django-boilerplate](https://github.com/rg3915/django-boilerplate). Veja a [Dica 1.1 - Django boilerplate](001-django-boilerplate.md).

## Pré-requisitos

* Linux ou macOS com `bash`, `curl` (ou `wget`) e Python 3 (no vídeo, Python 3.8.2, no Ubuntu).
* Para os dois shell scripts: o `sed` do GNU (o padrão do Linux). Os scripts usam `sed -i` no formato do GNU, que não funciona com o `sed` do macOS.
* Para o cookiecutter-django: PostgreSQL instalado e rodando.

## Opção 1: boilerplatesimple.sh

### Baixando o script

Crie uma pasta temporária e baixe o script do gist. O comando de download está no próprio cabeçalho do script:

```bash
mkdir /tmp/dica01
cd /tmp/dica01

curl https://gist.githubusercontent.com/rg3915/b363f5c4a998f42901705b23ccf4b8e8/raw/b759d5a4c1dd471a1c1851c2a9e7cbc705f11ac1/boilerplatesimple.sh -o boilerplatesimple.sh
```

O link acima aponta para a revisão do gist usada no vídeo (V 0.1.1, de 06/06/2020). Se preferir o `wget`:

```bash
wget https://gist.githubusercontent.com/rg3915/b363f5c4a998f42901705b23ccf4b8e8/raw/b759d5a4c1dd471a1c1851c2a9e7cbc705f11ac1/boilerplatesimple.sh -O boilerplatesimple.sh
```

### Antes de rodar, confira o script

Uma dica importante: **nunca rode um script baixado da internet sem olhar o que ele faz**. No mínimo, procure por `rm`, que apaga arquivos. No vídeo isso é feito no `vim`:

```bash
vim boilerplatesimple.sh
```

Dentro do `vim`, digite `/rm` e Enter. Neste script a busca termina com `E486: Padrão não encontrado: rm`, ou seja, não há nenhum `rm` nele.

O cabeçalho do script diz o que ele faz:

```bash
# V 0.1.1
# 2020-06-06

# Shell script to create a very simple Django project.
# This script require Python 3.x and pyenv
# Settings.py is config to Django 2.2.13

# The project contains:
# Settings config
# Admin config
```

### Rodando o script

O script é executado com `source` (e não com `bash`), porque ele ativa a virtualenv e isso precisa valer para o seu terminal. O nome do projeto é opcional; o padrão é `myproject`:

```bash
source boilerplatesimple.sh
# ou: source boilerplatesimple.sh outronome
```

A saída começa assim:

```
>>> The name of the project is 'myproject'.
>>> Creating README.md
>>> Creating virtualenv
>>> .venv is created
>>> activate the .venv
>>> Installing the Django
```

O que o script faz, na ordem:

1. Cria o `README.md` do projeto.
2. Cria e ativa a virtualenv `.venv` (`python -m venv .venv`).
3. Instala `django==2.2.13`, `dj-database-url`, `django-widget-tweaks`, `python-decouple` e `django-extensions`, e grava o `requirements.txt` com `pip freeze`.
4. Cria `contrib/env_gen.py` e roda esse arquivo para gerar o `.env` com uma `SECRET_KEY` aleatória.
5. Cria o `.gitignore`.
6. Roda `django-admin.py startproject myproject .` e cria o app `core` **dentro** da pasta do projeto (`myproject/core`).
7. Edita o `settings.py` com `sed`, cria `core/urls.py` e reescreve o `urls.py` principal.
8. Roda `makemigrations` e `migrate` e pergunta se você quer criar um superusuário.

No fim, o `migrate` aplica as migrations do Django 2.2 e o script pergunta pelo superusuário:

```
  Applying sessions.0001_initial... OK
Create superuser? (y/N) y
>>> Creating a 'admin' user ...
>>> The password must contain at least 8 characters.
>>> Password suggestions: demodemo
```

Responda `y` e digite a senha. O usuário é sempre `admin`. Use uma senha simples assim apenas em desenvolvimento.

O `requirements.txt` gerado no vídeo ficou assim:

```
dj-database-url==0.5.0
Django==2.2.13
django-extensions==2.2.9
django-widget-tweaks==1.4.8
python-decouple==3.3
pytz==2020.1
sqlparse==0.3.1
```

### Os arquivos gerados

O `contrib/env_gen.py` gera o `.env`:

```python
# contrib/env_gen.py
"""
Django SECRET_KEY generator.
"""
from django.utils.crypto import get_random_string


chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

CONFIG_STRING = """
DEBUG=True
SECRET_KEY=%s
ALLOWED_HOSTS=127.0.0.1, .localhost
""".strip() % get_random_string(50, chars)

# Writing our configuration file to '.env'
with open('.env', 'w') as configfile:
    configfile.write(CONFIG_STRING)
```

O `.gitignore`:

```
__pycache__/
*.py[cod]
*.sqlite3
*.env
*.DS_Store
.venv/
staticfiles/
.ipynb_checkpoints/
```

A estrutura final do projeto (vista com o comando `tree`, sem os `__pycache__`):

```
.
├── boilerplatesimple.sh
├── contrib
│   └── env_gen.py
├── db.sqlite3
├── manage.py
├── myproject
│   ├── core
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── README.md
└── requirements.txt
```

O `models.py` e o `views.py` do `core` vêm vazios, como o `startapp` cria:

```python
# myproject/core/models.py
from django.db import models

# Create your models here.
```

O `core/urls.py` já vem com o esqueleto pronto. É só descomentar as linhas quando criar a primeira view:

```python
# myproject/core/urls.py
from django.urls import path
# from myproject.core import views as v


app_name = 'core'


urlpatterns = [
    # path('', v.index, name='index'),
]
```

O `urls.py` principal inclui as URLs do `core` com o namespace `core`:

```python
# myproject/urls.py
from django.urls import include, path
from django.contrib import admin
urlpatterns = [
    path('', include('myproject.core.urls', namespace='core')),
    path('admin/', admin.site.urls),
]
```

E o `settings.py` lê `SECRET_KEY`, `DEBUG` e `ALLOWED_HOSTS` do `.env` com o `python-decouple`, usa o `dj-database-url` para o banco (SQLite por padrão, ou o que estiver em `DATABASE_URL`), registra o `django_extensions` e o app `myproject.core`, e define o `STATIC_ROOT`. Este é o arquivo completo gerado pelo script:

```python
# myproject/settings.py
"""
Django settings for myproject project.

Generated by 'django-admin startproject' using Django 2.2.13.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from decouple import config, Csv
from dj_database_url import parse as dburl

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'myproject.core'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

default_dburl = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
DATABASES = {
    'default': config('DATABASE_URL', default=default_dburl, cast=dburl),
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

### Rodando o projeto

Como o script já rodou o `migrate`, basta subir o servidor:

```bash
python manage.py runserver
```

```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
June 14, 2020 - 04:41:33
Django version 2.2.13, using settings 'myproject.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Em [http://localhost:8000](http://localhost:8000) aparece a página padrão do Django ("The install worked successfully! Congratulations!"), porque ainda não existe nenhuma view. O admin já funciona em `/admin/`, com o usuário `admin`. É um esqueleto mínimo, bom para testes rápidos ou para começar um projeto do seu jeito.

No fim, o script lembra: não suba o `.env` para um repositório público e apague o `boilerplatesimple.sh`.

## Opção 2: boilerplate2.sh

O segundo script é bem mais completo: ele cria um projeto com um cadastro de contatos funcionando, com templates, testes, Selenium e dados de exemplo. Saia da virtualenv anterior e use outra pasta:

```bash
deactivate
cd ..
mkdir dica01-boilerplate
cd dica01-boilerplate

curl https://gist.githubusercontent.com/rg3915/a264d0ade860d2f2b4bf/raw/ac1cc2f36ba104b6b2cd38f050638f4c6f07fbe5/boilerplate2.sh -o boilerplate2.sh
```

O cabeçalho diz o que o projeto vai ter:

```bash
# Shell script to create a complete Django project.
# This script require Python 3.x and pyenv
# Settings.py is config to Django 2.2.12

# The project contains:
# Settings config
# Person model and form
# Person list and detail
# Person create, update and delete
# Admin config
# Tests
# Selenium test
# Manage shell
```

Antes de rodar, de novo, procure por `rm` no `vim` (`/rm` e depois `n` para ir à próxima ocorrência). Neste script aparecem dois, nenhum perigoso: `rm -rf djangoproject`, que apaga a pasta `djangoproject` (criada pelo próprio script) antes de recriá-la, e `rm -f core/tests.py`, que apaga o `tests.py` padrão do app, porque os testes vão para a pasta `core/tests/`.

```bash
source boilerplate2.sh
```

```
>>> The name of the project is 'myproject'.
>>> Remove djangoproject
>>> Creating djangoproject
>>> Creating README.md
>>> Creating virtualenv
>>> .venv is created
>>> activate the .venv
>>> Installing the Django
```

O script:

1. Cria a pasta `djangoproject`, entra nela, cria e ativa a `.venv`.
2. Instala `django==2.2.12`, `dj-database-url`, `django-daterange-filter`, `django-localflavor`, `django-widget-tweaks`, `python-decouple`, `pytz`, `selenium` e `django-extensions`.
3. Cria o projeto `myproject` e o app `core` com models, forms, mixins, views, URLs, admin, templates (Bootstrap 3 e Font Awesome via CDN), CSS e testes.
4. Roda as migrations e os testes (`Ran 14 tests ... OK`).
5. Popula o banco com `python manage.py shell_plus < shell/shell_person.py`, que lê o `fix/person.csv` e cria os contatos com `bulk_create` e telefones aleatórios.
6. Faz um backup com `dumpdata` em `fixtures.json`, pergunta pelo superusuário, roda os testes de novo e instala `ipdb` e `ipython[notebook]`.
7. Mostra o `Makefile` com os atalhos do projeto.

O `Makefile` exibido no fim da instalação:

```makefile
# Makefile
shell_person:
	python manage.py shell_plus < shell/shell_person.py

selenium_person:
	python selenium/selenium_person.py

createuser:
	python manage.py createsuperuser --username='admin' --email=''

backup:
	python manage.py dumpdata core --format=json --indent=2 > fixtures.json

load:
	python manage.py loaddata fixtures.json
```

A estrutura gerada (resumida):

```
djangoproject
├── contrib
│   └── env-sample
├── db.sqlite3
├── fix
│   └── person.csv
├── fixtures.json
├── Makefile
├── manage.py
├── myproject
│   ├── core
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations
│   │   ├── mixins.py
│   │   ├── models.py
│   │   ├── static
│   │   │   └── css
│   │   │       ├── main.css
│   │   │       └── social.css
│   │   ├── templates
│   │   │   ├── base.html
│   │   │   ├── core
│   │   │   │   ├── person_detail.html
│   │   │   │   ├── person_form.html
│   │   │   │   └── person_list.html
│   │   │   ├── footer.html
│   │   │   ├── index.html
│   │   │   ├── nav.html
│   │   │   └── pagination.html
│   │   ├── tests
│   │   │   ├── data.py
│   │   │   ├── test_form_person.py
│   │   │   ├── test_model_person.py
│   │   │   ├── test_view_person_detail.py
│   │   │   └── test_view_person_list.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── README.md
├── requirements.txt
├── selenium
│   └── selenium_person.py
└── shell
    └── shell_person.py
```

### Os models

O app tem dois models abstratos (`TimeStampedModel` e `Address`), o `Person` e o `Phone`:

```python
# myproject/core/models.py
from django.db import models
from django.shortcuts import resolve_url as r
from localflavor.br.br_states import STATE_CHOICES

PHONE_TYPE = (
    ('pri', 'principal'),
    ('com', 'comercial'),
    ('res', 'residencial'),
    ('cel', 'celular'),
    ('cl', 'Claro'),
    ('oi', 'Oi'),
    ('t', 'Tim'),
    ('v', 'Vivo'),
    ('n', 'Nextel'),
    ('fax', 'fax'),
    ('o', 'outros'),
)


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


class Address(models.Model):
    address = models.CharField(u'endereço', max_length=100, blank=True)
    complement = models.CharField('complemento', max_length=100, blank=True)
    district = models.CharField('bairro', max_length=100, blank=True)
    city = models.CharField('cidade', max_length=100, blank=True)
    uf = models.CharField(
        'UF',
        max_length=2,
        choices=STATE_CHOICES,
        blank=True
    )
    cep = models.CharField('CEP', max_length=9, blank=True)

    class Meta:
        abstract = True


class Person(TimeStampedModel, Address):
    first_name = models.CharField('nome', max_length=50)
    last_name = models.CharField(
        'sobrenome',
        max_length=50,
        null=True,
        blank=True
    )
    email = models.EmailField(null=True, blank=True)
    blocked = models.BooleanField('bloqueado', default=False)

    class Meta:
        ordering = ['first_name']
        verbose_name = 'contato'
        verbose_name_plural = 'contatos'

    def __str__(self):
        return ' '.join(filter(None, [self.first_name, self.last_name]))

    full_name = property(__str__)

    def get_absolute_url(self):
        return r('core:person_detail', pk=self.pk)


class Phone(models.Model):
    phone = models.CharField('telefone', max_length=20, blank=True)
    person = models.ForeignKey('Person', on_delete=models.PROTECT)
    phone_type = models.CharField(
        'tipo',
        max_length=3,
        choices=PHONE_TYPE,
        default='pri'
    )

    def __str__(self):
        return self.phone
```

### As views, o mixin de busca, o formulário e as URLs

As views são as genéricas do Django. A lista usa o `NameSearchMixin`, que filtra pelo campo de busca `search_box` (nome, sobrenome ou e-mail), e pagina de 10 em 10:

```python
# myproject/core/mixins.py
from django.db.models import Q


class NameSearchMixin(object):

    def get_queryset(self):
        queryset = super(NameSearchMixin, self).get_queryset()
        q = self.request.GET.get('search_box')
        if q:
            return queryset.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(email__icontains=q))
        return queryset
```

```python
# myproject/core/views.py
from django.shortcuts import render
from django.urls import reverse_lazy as r
from django.views.generic import CreateView, ListView, DetailView
from django.views.generic import UpdateView, DeleteView
from .mixins import NameSearchMixin
from .models import Person
from .forms import PersonForm


def home(request):
    return render(request, 'index.html')


class PersonList(NameSearchMixin, ListView):
    model = Person
    paginate_by = 10


person_detail = DetailView.as_view(model=Person)

person_create = CreateView.as_view(model=Person, form_class=PersonForm)

person_update = UpdateView.as_view(model=Person, form_class=PersonForm)

person_delete = DeleteView.as_view(model=Person, success_url=r('core:person_list'))
```

```python
# myproject/core/forms.py
from django import forms
from .models import Person


class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = (
            'first_name',
            'last_name',
            'email',
            'address',
            'complement',
            'district',
            'city',
            'uf',
            'cep',
            'blocked'
        )
```

```python
# myproject/core/urls.py
from django.urls import path
from myproject.core import views as c


app_name = 'core'
urlpatterns = [
    path('', c.home, name='home'),
    path('person/', c.PersonList.as_view(), name='person_list'),
    path('person/add/', c.person_create, name='person_add'),
    path('person/<int:pk>/', c.person_detail, name='person_detail'),
    path('person/<int:pk>/edit/', c.person_update, name='person_edit'),
    path('person/<int:pk>/delete/',
         c.person_delete, name='person_delete'),
]
```

O admin já vem com os telefones em linha (`TabularInline`) e um filtro por intervalo de datas com o `django-daterange-filter` (assunto da [Dica 5](005-django-admin-date-range-filter.md)):

```python
# myproject/core/admin.py
from daterange_filter.filter import DateRangeFilter
from django.contrib import admin
from .models import Person, Phone
from .forms import PersonForm


class PhoneInline(admin.TabularInline):
    model = Phone
    extra = 1


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [PhoneInline]
    list_display = ('__str__', 'email', 'phone', 'uf', 'created', 'blocked')
    date_hierarchy = 'created'
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = (
        # 'uf',
        ('created', DateRangeFilter),
    )
    form = PersonForm

    def phone(self, obj):
        return obj.phone_set.first()

    phone.short_description = 'telefone'
```

Os templates, o CSS, os testes e o script do Selenium são longos e estão completos no [boilerplate2.sh](https://gist.github.com/rg3915/a264d0ade860d2f2b4bf).

### Usando o projeto

```bash
python manage.py runserver
```

Em [http://localhost:8000](http://localhost:8000) já existe um layout com menu (Home, Lista de Contatos, Admin). No vídeo:

* Em **Adicionar** (`/person/add/`) aparece o formulário "Novo Contato", com nome, sobrenome, e-mail, endereço, complemento, bairro, cidade, UF, CEP e bloqueado. Ao salvar, você vai para a página de detalhe do contato.
* Na página de detalhe dá para **editar** (`/person/<pk>/edit/`) e **excluir** (com uma página de confirmação).
* A **Lista de Contatos** (`/person/`) mostra nome, e-mail, telefone e UF, o total de contatos (32, vindos do `person.csv`) e a paginação. O campo **Localizar** busca por nome, sobrenome ou e-mail, por exemplo `/person/?search_box=elliot`.

## Opção 3: cookiecutter-django

O [cookiecutter-django](https://github.com/pydanny/cookiecutter-django) é um boilerplate criado pelo Daniel Roy Greenfeld (pydanny), com muitos contribuidores. Ele usa o Cookiecutter, uma ferramenta que gera projetos a partir de um modelo fazendo perguntas no terminal. A [documentação](https://cookiecutter-django.readthedocs.io/en/latest/) explica cada opção.

### Instalando o Cookiecutter

```bash
deactivate
cd ..
mkdir cookiecutter
cd cookiecutter

python -V
# Python 3.8.2
python -m venv .venv
source .venv/bin/activate

pip install "cookiecutter>=1.7.0"
```

### Gerando o projeto

```bash
cookiecutter https://github.com/pydanny/cookiecutter-django
```

Se você já tinha baixado o modelo antes, ele pergunta se pode apagar e baixar de novo; responda que sim:

```
You've downloaded /home/regis/.cookiecutters/cookiecutter-django before. Is it okay to delete and re-download it? [yes]:
```

Depois vêm as perguntas. Entre colchetes está o valor padrão (Enter aceita o padrão). As respostas usadas no vídeo:

```
project_name [My Awesome Project]: myproject
project_slug [myproject]:
description [Behold My Awesome Project!]:
author_name [Daniel Roy Greenfeld]: Regis Santos
domain_name [example.com]:
email [regis-santos@example.com]:
version [0.1.0]:
Select open_source_license:
1 - MIT
2 - BSD
3 - GPLv3
4 - Apache Software License 2.0
5 - Not open source
Choose from 1, 2, 3, 4, 5 [1]:
timezone [UTC]:
windows [n]:
use_pycharm [n]:
use_docker [n]:
Select postgresql_version:
1 - 11.3
2 - 10.8
3 - 9.6
4 - 9.5
5 - 9.4
Choose from 1, 2, 3, 4, 5 [1]:
Select js_task_runner:
1 - None
2 - Gulp
Choose from 1, 2 [1]:
Select cloud_provider:
1 - AWS
2 - GCP
3 - None
Choose from 1, 2, 3 [1]:
Select mail_service:
1 - Mailgun
2 - Amazon SES
3 - Mailjet
4 - Mandrill
5 - Postmark
6 - Sendgrid
7 - SendinBlue
8 - SparkPost
9 - Other SMTP
Choose from 1, 2, 3, 4, 5, 6, 7, 8, 9 [1]:
use_async [n]:
use_drf [n]:
custom_bootstrap_compilation [n]:
use_compressor [n]:
use_celery [n]:
use_mailhog [n]:
use_sentry [n]:
use_whitenoise [n]:
use_heroku [n]: y
Select ci_tool:
1 - None
2 - Travis
3 - Gitlab
Choose from 1, 2, 3 [1]:
keep_local_envs_in_vcs [y]:
debug [n]:
```

Ou seja: projeto `myproject`, sem Docker, PostgreSQL 11.3, sem Celery, sem DRF, com os arquivos de deploy para o Heroku. O resto ficou no padrão.

### Instalando as dependências e criando o banco

Entre na pasta do projeto e instale os requirements de desenvolvimento (o `local.txt` inclui o `base.txt` e acrescenta debug toolbar, pytest, linters etc.):

```bash
cd myproject
pip install -r requirements/local.txt
```

O projeto usa PostgreSQL. Se você rodar o `migrate` antes de criar o banco, dá erro:

```bash
python manage.py migrate
```

```
django.db.utils.OperationalError: FATAL:  database "myproject" does not exist
```

Então crie o banco (considerando que o PostgreSQL já está instalado e que existe o usuário `postgres`) e rode o `migrate` de novo:

```bash
createdb myproject -U postgres
python manage.py migrate
```

### Rodando

```bash
python manage.py runserver
```

Em [http://localhost:8000](http://localhost:8000) aparece o site com o menu Home, About, Cadastro e Entrar, e a barra lateral do **Django Debug Toolbar**.

O cadastro de usuários (feito com o `django-allauth`) já funciona, com confirmação de e-mail:

1. Clique em **Cadastro** e preencha e-mail, nome de usuário e senha.
2. Em desenvolvimento o e-mail não é enviado de verdade: ele aparece no terminal onde está o `runserver`, com o link de confirmação, algo como `http://localhost:8000/accounts/confirm-email/MQ:1jkKe.../`.
3. Abra o link e confirme o e-mail ("Confirmou rg3915@example.com").
4. Agora é só **Entrar** com o usuário e a senha. Logado, aparecem **My Profile** e **Sair**.

## Resumo

* `boilerplatesimple.sh`: o mínimo, um projeto com `settings.py` organizado (decouple + dj-database-url) e um app `core` vazio.
* `boilerplate2.sh`: um projeto de exemplo completo, com CRUD de contatos, testes e dados.
* `cookiecutter-django`: um projeto pronto para produção, com PostgreSQL, autenticação com allauth e muitas opções.

Os comandos do cookiecutter-django, de uma vez:

```
python -m venv .venv
source .venv/bin/activate

pip install "cookiecutter>=1.7.0"
cookiecutter https://github.com/pydanny/cookiecutter-django
pip install -r requirements/local.txt 
python manage.py migrate

createdb myproject -U postgres

python manage.py migrate
```

Observação: o cookiecutter-django mudou de endereço para [github.com/cookiecutter/cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django) (o link antigo redireciona) e hoje usa versões bem mais novas do Django, com outras perguntas. O `django-admin.py` usado pelos scripts deixou de existir no Django 4.0; nas versões novas o comando é `django-admin`.
