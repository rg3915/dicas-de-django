# Dica 1.1 - Django boilerplate

**Versões usadas no vídeo:** Python 3.8.7 e Django 3.1.8 (django-boilerplate 1.0.0, abril de 2021).
{: .versoes }

<a href="https://youtu.be/eLKjL61HEbQ">
    <img src="../.gitbook/assets/youtube.png">
</a>

Na [Dica 1](000-django-boilerplate-e-cookiecutter-django.md) vimos como criar um projeto rapidamente com o `boilerplatesimple.sh`, um script guardado num gist. Agora ele virou um repositório no GitHub, o [django-boilerplate](https://github.com/rg3915/django-boilerplate), e ficou mais completo: além do `settings.py` configurado, o projeto já nasce com três apps:

* **accounts**: login e logout, da forma mais simples possível.
* **core**: models abstratos prontos para reaproveitar (UUID, data de criação/modificação, endereço, documentos, ativo) e um exemplo de *management command*.
* **crm**: um model `Person` de exemplo, que herda os models abstratos do `core`, já registrado no admin.

No vídeo o repositório estava na versão 1.0.0, com Python 3.8.7 e Django 3.1.8. Depois ele continuou sendo atualizado (a versão desta página, quando foi publicada, usava o Django 4.0.2); aqui descrevemos o que o vídeo mostra.

## Pré-requisitos

* Linux (o script roda em Unix; ele usa o `sed -i` do GNU e o `cp -r` do Linux, por isso não funciona sem ajustes no macOS).
* Python 3 e git.

## Pacotes usados

* Python 3.8.7
* Django 3.1.8
* dj-database-url
* django-extensions
* django-localflavor
* isort
* python-decouple

O script também instala o `ipdb` para depuração, mas não o coloca no `requirements.txt`.

## Baixando o boilerplate

O script copia vários arquivos do repositório, por isso ele espera encontrar o clone em `/tmp/django-boilerplate`. Clone nesse caminho e copie o script para a pasta onde você quer criar o projeto:

```bash
git clone https://github.com/rg3915/django-boilerplate.git /tmp/django-boilerplate
# Copy this file to your actual folder.
cp /tmp/django-boilerplate/boilerplatesimple.sh .
```

Se a pasta `/tmp/django-boilerplate` já existir (de um uso anterior), o `git clone` reclama:

```
fatal: destination path '/tmp/django-boilerplate' already exists and is not an empty directory.
```

Nesse caso, basta seguir com o `cp` (ou apagar a pasta antiga e clonar de novo, para pegar a versão mais recente).

Para não ter que lembrar dos comandos, o README sugere um alias:

```bash
alias bsimple='git clone https://github.com/rg3915/django-boilerplate.git /tmp/django-boilerplate;
cp /tmp/django-boilerplate/boilerplatesimple.sh .
printf "Type:\n`tput setaf 2`source boilerplatesimple.sh myproject\n"'
```

## Criando o projeto

Rode o script com `source`, passando o nome do projeto (se não passar nada, o nome é `myproject`):

```bash
source boilerplatesimple.sh myproject
```

Primeiro ele pergunta a versão do Django. Enter escolhe o padrão, a 3.1.8:

```
Select Django version:
2 - 2.2.20
3 - 3.1.8
Choose from 2, 3 [3]:
>>> You chose Django 3.1.8.
>>> The name of the project is 'myproject'.
>>> Creating .gitignore
>>> Creating README.md
>>> Creating virtualenv
>>> .venv is created
>>> activate the .venv
>>> Installing the Django
```

Ele cria e ativa a `.venv`, instala os pacotes, gera o `.env` e cria o projeto e os apps:

```
>>> Creating contrib/env_gen.py
>>> Running contrib/env_gen.py
Success!
Type: cat .env
>>> Creating the project 'myproject' ...
>>> Creating the app 'core' ...
>>> Creating the app 'accounts' ...
>>> Creating the app 'crm' ...
>>> Editing settings.py
Replace LANGUAGE_CODE to pt-br? [Y/n]
```

Responda `Y` (ou Enter) para trocar o `LANGUAGE_CODE` para `pt-br` e o `TIME_ZONE` para `America/Sao_Paulo`. Em seguida ele escreve os arquivos dos apps:

```
>>> Editing urls.py
>>> Editing accounts/urls.py
>>> Editing core/models.py
>>> Editing core/urls.py
>>> Editing core/views.py
>>> Editing management/commands.
>>> Editing crm/admin.py
>>> Editing crm/forms.py
>>> Editing crm/models.py
>>> Editing crm/urls.py
```

Por fim roda `makemigrations` e `migrate` (repare no `crm.0001_initial`) e pergunta pelo superusuário:

```
  Applying crm.0001_initial... OK
  Applying sessions.0001_initial... OK
Create superuser? [Y/n]
>>> Creating a 'admin' user ...
>>> The password must contain at least 8 characters.
>>> Password suggestions: demodemo
Password:
```

O usuário é sempre `admin`; digite a senha (no vídeo, uma senha simples, só para desenvolvimento). O script termina com os avisos de não publicar o `.env` e move o `boilerplatesimple.sh` para `/tmp`.

O `requirements.txt` gerado lista só os pacotes principais: `Django==3.1.8` na primeira linha e, em seguida, `dj-database-url`, `django-extensions`, `django-localflavor`, `isort` e `python-decouple`, com as versões que o `pip` instalou no momento (o script as pega do `pip freeze`).

## A estrutura do projeto

```
.
├── contrib
│   └── env_gen.py
├── manage.py
├── myproject
│   ├── asgi.py
│   ├── accounts
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── core
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── management
│   │   │   └── commands
│   │   │       ├── hello.py
│   │   │       └── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── crm
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── README.md
└── requirements.txt
```

Os apps ficam dentro da pasta do projeto, por isso são importados como `myproject.core`, `myproject.crm` etc.

## O .env

O `contrib/env_gen.py` gera uma `SECRET_KEY` e uma senha aleatórias e grava o `.env`, já com exemplos comentados para banco e e-mail:

```python
# contrib/env_gen.py
"""
Python SECRET_KEY generator.
"""
import random

chars = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!?@#$%^&*()"
size = 50
secret_key = "".join(random.sample(chars, size))

chars = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!?@#$%_"
size = 20
password = "".join(random.sample(chars, size))

CONFIG_STRING = """
DEBUG=True
SECRET_KEY=%s
ALLOWED_HOSTS=127.0.0.1,.localhost,0.0.0.0

#DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
#DB_NAME=
#DB_USER=
#DB_PASSWORD=%s
#DB_HOST=localhost

#DEFAULT_FROM_EMAIL=
#EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
#EMAIL_HOST=localhost
#EMAIL_PORT=
#EMAIL_HOST_USER=
#EMAIL_HOST_PASSWORD=
#EMAIL_USE_TLS=True
""".strip() % (secret_key, password)

# Writing our configuration file to '.env'
with open('.env', 'w') as configfile:
    configfile.write(CONFIG_STRING)

print('Success!')
print('Type: cat .env')
```

## O settings.py

O script copia um `settings.py` modelo do repositório e troca o nome do projeto, a versão e, conforme a versão do Django escolhida, o `BASE_DIR` (com `pathlib` no Django 3.1, com `os.path` no 2.2). Com Django 3.1.8 e `pt-br`, o resultado é:

```python
# myproject/settings.py
# ... (veja o arquivo completo no GitHub)
from pathlib import Path

from decouple import Csv, config
from dj_database_url import parse as dburl


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# ...
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())

# ...
# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

default_dburl = 'sqlite:///' + str(BASE_DIR / 'db.sqlite3')
DATABASES = {
    'default': config('DATABASE_URL', default=default_dburl, cast=dburl),
}

# ...
USE_THOUSAND_SEPARATOR = True

DECIMAL_SEPARATOR = ','
# ...
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR.joinpath('staticfiles')

LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = 'core:index'
# LOGOUT_REDIRECT_URL = 'core:index'
```

Código completo: [settings.py (modelo, com os marcadores que o script substitui)](https://github.com/rg3915/django-boilerplate/blob/7bf58932599479d17bd64d5e32129c2e51b3a421/settings.py)

Os destaques: `SECRET_KEY`, `DEBUG` e `ALLOWED_HOSTS` vêm do `.env` (python-decouple); o banco vem de `DATABASE_URL`, com SQLite como padrão (dj-database-url); separador de milhar e vírgula decimal para o formato brasileiro; e o login redireciona para `core:index`.

## As URLs

O `urls.py` principal inclui as URLs dos três apps. As de `accounts` ficam **sem namespace**, para que os nomes `login` e `logout` funcionem direto (é o que o Django espera):

```python
# myproject/urls.py
from django.urls import include, path
from django.contrib import admin


urlpatterns = [
    path('', include('myproject.core.urls', namespace='core')),
    path('accounts/', include('myproject.accounts.urls')),  # without namespace
    path('crm/', include('myproject.crm.urls', namespace='crm')),
    path('admin/', admin.site.urls),
]
```

## App accounts: login e logout

Usa as views prontas do Django:

```python
# myproject/accounts/urls.py
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
```

## App core

### Views e URLs

Uma view simples, que devolve um HTML direto, e uma versão comentada com template e `login_required`, para quando você criar o seu `index.html`:

```python
# myproject/core/views.py
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


# @login_required
def index(request):
    return HttpResponse('<h1>Django</h1><p>Página simples.</p>')


# @login_required
# def index(request):
#     template_name = 'index.html'
#     return render(request, template_name)
```

```python
# myproject/core/urls.py
from django.urls import path

from myproject.core import views as v

app_name = 'core'


urlpatterns = [
    path('', v.index, name='index'),
]
```

### Models abstratos

O `core/models.py` não cria nenhuma tabela: todos os models são **abstratos** (`abstract = True`), feitos para serem herdados pelos models dos outros apps. Cada um acrescenta um grupo de campos:

* `UuidModel`: um `uuid` único.
* `TimeStampedModel`: `created` e `modified`, preenchidos automaticamente.
* `CreatedBy`: quem criou o registro (`ForeignKey` para `User`).
* `Address`: endereço completo, com a UF usando os estados do `django-localflavor`.
* `Document`: CPF, RG e CNH.
* `Active`: `active` e `exist_deleted` (para "deletar" sem apagar do banco).

```python
# myproject/core/models.py
import uuid

from django.contrib.auth.models import User
from django.db import models
from localflavor.br.br_states import STATE_CHOICES


class UuidModel(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


# ... (TimeStampedModel, CreatedBy, Address e Document: veja o arquivo completo no GitHub)


class Active(models.Model):
    active = models.BooleanField('ativo', default=True)
    exist_deleted = models.BooleanField(
        'existe/deletado',
        default=True,
        help_text='Se for True o item existe. Se for False o item foi deletado.'
    )

    class Meta:
        abstract = True
```

Código completo: [models.py](https://github.com/rg3915/django-boilerplate/blob/7bf58932599479d17bd64d5e32129c2e51b3a421/models.py)

### Management command

O `core` também traz um exemplo de comando personalizado do `manage.py`, com um argumento opcional:

```python
# myproject/core/management/commands/hello.py
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Print hello world.'

    def add_arguments(self, parser):
        # Argumento nomeado
        parser.add_argument(
            '--awards', '-a',
            action='store_true',
            help='Ajuda da opção awards.'
        )

    def handle(self, *args, **options):
        self.stdout.write('Hello world.')
        if options['awards']:
            self.stdout.write('Awards')
```

```bash
python manage.py hello -a
```

```
Hello world.
Awards
```

## App crm: o exemplo

O `Person` herda de cinco models abstratos do `core` e só declara nome, sobrenome e e-mail. Todos os outros campos (uuid, criado em, endereço, CPF, ativo...) vêm das classes herdadas:

```python
# myproject/crm/models.py
from django.db import models
from django.urls import reverse_lazy

from myproject.core.models import (
    Active,
    Address,
    Document,
    TimeStampedModel,
    UuidModel
)


class Person(UuidModel, TimeStampedModel, Address, Document, Active):
    first_name = models.CharField('nome', max_length=50)
    last_name = models.CharField('sobrenome', max_length=50, null=True, blank=True)  # noqa E501
    email = models.EmailField(null=True, blank=True)

    class Meta:
        ordering = ('first_name',)
        verbose_name = 'pessoa'
        verbose_name_plural = 'pessoas'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name or ""}'.strip()

    def __str__(self):
        return self.full_name

    # def get_absolute_url(self):
    #     return reverse_lazy('crm:person_detail', kwargs={'pk': self.pk})
```

```python
# myproject/crm/admin.py
from django.contrib import admin

from .models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'active')
    # readonly_fields = ('slug',)
    # list_display_links = ('name',)
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('active',)
    # date_hierarchy = 'created'
    # ordering = ('-created',)
    # actions = ('',)
```

```python
# myproject/crm/forms.py
from django import forms

from .models import Person


class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = '__all__'
```

```python
# myproject/crm/urls.py
from django.urls import path

from myproject.crm import views as v

app_name = 'crm'


urlpatterns = [
    # path(),
]
```

## Rodando

```bash
python manage.py runserver
```

Entre em [http://localhost:8000/admin/](http://localhost:8000/admin/) com o usuário `admin`. O admin (em português, por causa do `pt-br`) mostra **Usuários**, **Grupos** e, no app CRM, **Pessoas**. No vídeo é cadastrada uma pessoa de exemplo, e a lista mostra as colunas Pessoa, Email e Ativo, a busca e o filtro "Por ativo".

Este passa a ser o ponto de partida dos projetos das próximas dicas.

Observação: o `django-admin.py` usado pelo script foi removido no Django 4.0 (o comando atual é `django-admin`), e o `USE_L10N` deixou de existir no Django 5.0. As versões mais novas do [django-boilerplate](https://github.com/rg3915/django-boilerplate) já tratam disso.
