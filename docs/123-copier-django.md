# Copier + Django: login por e-mail em um comando

<!--agendado-->

> 📅 **Vídeo agendado:** será publicado no YouTube em **10/10/2026, às 10:00**.

<!--/agendado-->

**Testado com:** Django 6.1.1, Copier e Python 3.14.
{: .versoes }

<!--yt-block -TBGoqLYYxA video-->

Documentação do Copier: [https://copier.readthedocs.io/](https://copier.readthedocs.io/)

Todo projeto Django começa igual: trocar o username pelo e-mail, fazer login, cadastro, "esqueci minha senha"... e copiar tudo do projeto anterior, esquecendo um pedaço.

Com o **Copier** você gera tudo isso com um comando só: um template Django com usuário que entra com e-mail, cadastro, perfil, troca e reset de senha, app `core` com modelos abstratos, health check e testes. E o projeto ainda atualiza quando o template muda (`copier update`).

## O que é o Copier

O Copier é uma ferramenta que gera projetos a partir de um template. O template pode ser uma pasta ou um repositório git. Ele faz algumas perguntas (nome do projeto, banco de dados...), usa as respostas para preencher os arquivos e grava essas respostas num arquivo `.copier-answers.yml` dentro do projeto gerado.

A grande diferença para o cookiecutter está nesse arquivo de respostas: quando o template muda, o projeto gerado pode ser **atualizado** com `copier update`, sem copiar tudo de novo.

Neste tutorial você vai montar o template `django-auth-template` do zero, arquivo por arquivo, e depois gerar projetos com ele.

## Pré-requisitos

* Python 3.14 e o `uv` ([https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)).
* Git.
* Noções de Django: models, views, urls, templates e o sistema de autenticação.

## Passo 1: instalando o Copier

```
uv tool install copier
copier --version
```

O `uv tool install` instala o Copier isolado, como um programa de linha de comando (no vídeo, a versão é a 9.18.2).

## Passo 2: a estrutura do template

```
django-auth-template/
├── .gitignore
├── copier.yml
└── template/
    ├── {{ _copier_conf.answers_file }}.jinja
    ├── .gitignore
    ├── README.md.jinja
    ├── manage.py.jinja
    ├── pyproject.toml.jinja
    ├── contrib/
    │   └── env_gen.py.jinja
    ├── {{ project_slug }}/
    │   ├── __init__.py
    │   ├── settings.py.jinja
    │   ├── urls.py
    │   ├── wsgi.py.jinja
    │   └── asgi.py.jinja
    ├── accounts/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── forms.py
    │   ├── managers.py
    │   ├── models.py
    │   ├── tests.py
    │   ├── urls.py
    │   ├── views.py
    │   ├── migrations/
    │   │   ├── __init__.py
    │   │   └── 0001_initial.py
    │   └── templates/registration/
    │       ├── _form.html
    │       ├── login.html
    │       ├── signup.html
    │       ├── profile.html
    │       ├── password_change_form.html
    │       ├── password_change_done.html
    │       ├── password_reset_form.html
    │       ├── password_reset_done.html
    │       ├── password_reset_confirm.html
    │       ├── password_reset_complete.html
    │       ├── password_reset_email.html
    │       └── password_reset_subject.txt
    └── core/
        ├── __init__.py
        ├── apps.py
        ├── context_processors.py
        ├── mail.py
        ├── models.py
        ├── tests.py
        ├── urls.py
        ├── views.py
        └── templates/
            ├── base.html
            ├── core/index.html
            └── includes/
                ├── messages.html
                └── nav.html
```

Três regras explicam essa estrutura:

* **O `copier.yml` fica fora.** Ele é a configuração do template. Só o que está dentro da pasta `template/` vira projeto (é o que a chave `_subdirectory: template` diz).
* **Nome de pasta também é template.** A pasta `{{ project_slug }}` vira `loja/` se o projeto se chamar Loja. É ali que ficam o `settings.py`, o `urls.py`, o `wsgi.py` e o `asgi.py`.
* **Só os arquivos terminados em `.jinja` passam pelo Jinja**, e perdem o sufixo na cópia (`settings.py.jinja` vira `settings.py`). São os arquivos que dependem das respostas: nome, pacote e banco. Os arquivos das apps `accounts` e `core` são Django normal, copiados do jeito que estão. Isso é importante porque os templates do Django também usam `{{ }}` e `{% %}`, e o Jinja tentaria interpretá-los.

Crie a pasta e inicie o git:

```
mkdir django-auth-template && cd django-auth-template
git init
```

```
# .gitignore
.venv/
__pycache__/
```

## Passo 3: o copier.yml

```yaml
# copier.yml
# chaves com _ configuram o Copier
_subdirectory: template
_min_copier_version: "9.2.0"
_tasks:
  - "git init"
  - "uv sync"
  - "uv run python contrib/env_gen.py"
  - command: "uv run python manage.py migrate"
    when: "{{ database == 'sqlite' }}"

project_name:
  type: str
  help: Nome do projeto
  default: Meu Projeto

project_slug:
  type: str
  help: Nome do pacote Python
  default: "{{ project_name | lower | replace(' ', '_') }}"
  validator: "{% if not project_slug.isidentifier() %}Use letras, números e _{% endif %}"

database:
  type: str
  help: Banco de dados
  choices: [sqlite, postgres]
  default: sqlite
```

As chaves que começam com `_` configuram o próprio Copier:

* `_subdirectory: template`: só a pasta `template/` é copiada.
* `_min_copier_version`: recusa versões antigas do Copier.
* `_tasks`: comandos que rodam **depois** de gerar o projeto, dentro da pasta dele:
  1. `git init`: o projeto já nasce repositório.
  2. `uv sync`: cria o `.venv` e instala o Django e as dependências.
  3. `uv run python contrib/env_gen.py`: gera o `.env` com uma `SECRET_KEY` nova.
  4. `migrate`, mas só quando o banco é SQLite. O `when` recebe uma expressão Jinja; com Postgres, o banco ainda não existe na hora da geração, então a task é pulada.

Como as tasks executam comandos na sua máquina, o Copier exige a opção `--trust` para rodá-las.

As demais chaves são as perguntas:

* `project_name`: texto livre, com padrão `Meu Projeto`.
* `project_slug`: o nome do pacote Python. O `default` é calculado a partir da resposta anterior (`Minha Loja` vira `minha_loja`), e o `validator` recusa o que não for um identificador válido em Python. Se o validator devolver um texto, o Copier mostra esse texto como erro e pergunta de novo.
* `database`: uma escolha entre `sqlite` e `postgres`.

## Passo 4: o arquivo de respostas e os arquivos da raiz

O arquivo de respostas tem um nome que também é variável: `{{ _copier_conf.answers_file }}` vale `.copier-answers.yml` por padrão.

```yaml
# template/{{ _copier_conf.answers_file }}.jinja
# Changes here will be overwritten by Copier
{{ _copier_answers|to_nice_yaml -}}
```

No projeto gerado, ele fica assim:

```yaml
# loja/.copier-answers.yml
# Changes here will be overwritten by Copier
_commit: v1.0.0
_src_path: gh:rg3915/django-auth-template
database: sqlite
project_name: Loja
project_slug: loja
```

`_commit` é a versão (a tag git) do template usada e `_src_path` é de onde ele veio. É com esse arquivo que o `copier update` sabe o que aplicar. Nunca edite esse arquivo na mão.

O `pyproject.toml` só ganha o driver do Postgres quando ele for escolhido:

```toml
# template/pyproject.toml.jinja
[project]
name = "{{ project_slug }}"
version = "0.1.0"
description = "{{ project_name }}"
readme = "README.md"
requires-python = ">=3.14"
dependencies = [
    "dj-database-url>=3.1.2",
    "django>=6.1.1",
{%- if database == 'postgres' %}
    "psycopg[binary]>=3.3.6",
{%- endif %}
    "python-decouple>=3.8",
]
```

O `{%-` (com hífen) remove a quebra de linha antes da tag, para não sobrar linha em branco no arquivo gerado.

```python
# template/manage.py.jinja
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{ project_slug }}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```

```text
# template/.gitignore
.venv/
__pycache__/
.env
db.sqlite3
```

```markdown
<!-- template/README.md.jinja -->
# {{ project_name }}

Projeto Django gerado pelo template django-auth-template (Copier).

```
uv run python manage.py createsuperuser
uv run python manage.py test
uv run python manage.py runserver
```
```

### O script que gera o .env

```python
# template/contrib/env_gen.py.jinja
"""Gera o arquivo .env com uma SECRET_KEY nova."""
from pathlib import Path

from django.core.management.utils import get_random_secret_key

env = Path(__file__).resolve().parent.parent / '.env'

if env.exists():
    print('.env já existe, nada foi alterado.')
else:
    env.write_text(
        f'SECRET_KEY={get_random_secret_key()}\n'
        'DEBUG=True\n'
        'ALLOWED_HOSTS=127.0.0.1,localhost\n'
{%- if database == 'postgres' %}
        'DATABASE_URL=postgres://postgres:postgres@localhost:5432/{{ project_slug }}\n'
{%- else %}
        '# sem DATABASE_URL: usa o db.sqlite3 na raiz do projeto\n'
{%- endif %}
        '# em produção:\n'
        '# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend\n'
    )
    print('.env criado.')
```

* A `SECRET_KEY` é gerada com a função do próprio Django, por isso o script roda com `uv run`, depois do `uv sync`.
* Para Postgres, o `.env` já sai com a `DATABASE_URL` apontando para um banco com o nome do pacote.
* Se o `.env` já existir, o script não mexe nele. Isso importa porque as tasks rodam de novo a cada `copier update`, e você não quer perder a sua chave e as suas configurações.

## Passo 5: settings com python-decouple e dj-database-url

```python
# template/{{ project_slug }}/settings.py.jinja
"""Settings do {{ project_name }}."""
from pathlib import Path

import dj_database_url
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_NAME = '{{ project_name }}'

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv())

INSTALLED_APPS = [
    'core',
    'accounts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = '{{ project_slug }}.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.project',
            ],
        },
    },
]

WSGI_APPLICATION = '{{ project_slug }}.wsgi.application'

DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600,
    ),
}

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'core:index'
LOGOUT_REDIRECT_URL = 'core:index'

# E-mail: no desenvolvimento sai legível no terminal.
# Em produção, troque o EMAIL_BACKEND no .env.
email_backend = config('EMAIL_BACKEND', default='core.mail.ReadableConsoleEmailBackend')
MAILERS = {'default': {'BACKEND': email_backend}}
if email_backend.endswith('smtp.EmailBackend'):
    MAILERS['default']['OPTIONS'] = {
        'host': config('EMAIL_HOST', default='localhost'),
        'port': config('EMAIL_PORT', default=587, cast=int),
        'username': config('EMAIL_HOST_USER', default=''),
        'password': config('EMAIL_HOST_PASSWORD', default=''),
        'use_tls': config('EMAIL_USE_TLS', default=True, cast=bool),
    }

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='nao-responda@{{ project_slug }}.com')
```

Os pontos principais:

* **python-decouple**: `config()` lê do `.env` ou das variáveis de ambiente. `cast=bool` e `Csv()` convertem os textos.
* **dj-database-url**: uma URL descreve o banco inteiro. Sem `DATABASE_URL`, o padrão é o `db.sqlite3` na raiz; com `postgres://usuario:senha@host:porta/banco`, é Postgres. O mesmo `settings.py` serve para os dois casos.
* **AUTH_USER_MODEL = 'accounts.User'** desde o primeiro arquivo.
* **Idioma e fuso**: `pt-br` e `America/Sao_Paulo`.
* **E-mail**: no Django 6.1, os backends de e-mail se configuram no `MAILERS`. No desenvolvimento, o padrão é o `ReadableConsoleEmailBackend` da app `core`. Em produção, basta colocar `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` no `.env` (com `EMAIL_HOST`, `EMAIL_HOST_USER` e `EMAIL_HOST_PASSWORD`). As `OPTIONS` só entram para o SMTP porque, com `MAILERS`, o Django recusa opções que o backend não conhece.

```python
# template/{{ project_slug }}/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
]
```

```python
# template/{{ project_slug }}/wsgi.py.jinja
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{ project_slug }}.settings')

application = get_wsgi_application()
```

```python
# template/{{ project_slug }}/asgi.py.jinja
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{{ project_slug }}.settings')

application = get_asgi_application()
```

O `template/{{ project_slug }}/__init__.py` é um arquivo vazio.

## Passo 6: a app accounts, um User que entra com e-mail

### O model

```python
# template/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField('e-mail', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'
        ordering = ('email',)

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        self.email = self.email.lower()
```

* `username = None` remove o campo herdado do `AbstractUser`.
* `email` passa a ser único e é o `USERNAME_FIELD`: login, admin e `createsuperuser` pedem e-mail.
* `REQUIRED_FIELDS = []`: o `createsuperuser` pede só e-mail e senha.
* `clean()` guarda o e-mail em minúsculas quando ele passa por um formulário.

### O manager

```python
# template/accounts/managers.py
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Manager do User com e-mail: cria usuários sem username."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('O superusuário precisa de is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('O superusuário precisa de is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        # O login não diferencia maiúsculas de minúsculas.
        return self.get(email__iexact=email)
```

O detalhe está no `get_by_natural_key`. É o método que o backend de autenticação do Django usa para achar o usuário no login. Com `email__iexact`, a busca ignora maiúsculas e minúsculas: quem digitar `Regis@Email.com` entra como `regis@email.com`. Junto com o `.lower()` no `_create_user`, os e-mails ficam sempre gravados em minúsculas.

### A migração inicial já pronta

A pegadinha do usuário customizado: o `AUTH_USER_MODEL` precisa existir **antes** do primeiro `migrate`. Se você rodar o `migrate` com o `User` padrão e trocar depois, as tabelas do `auth` e do `admin` já apontam para o usuário antigo, e a troca vira uma dor de cabeça.

Por isso a migração inicial vem dentro do template. Para gerá-la, crie um projeto de teste com o template (sem rodar as tasks), rode o `makemigrations` e copie o arquivo de volta:

```
copier copy --trust --defaults --skip-tasks ./django-auth-template /tmp/gerar
cd /tmp/gerar
uv sync
uv run python contrib/env_gen.py
uv run python manage.py makemigrations accounts
cp accounts/migrations/0001_initial.py ~/django-auth-template/template/accounts/migrations/
```

```python
# template/accounts/migrations/0001_initial.py
# Generated by Django 6.1.1 on 2026-10-03 18:58

import accounts.managers
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='e-mail')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'usuário',
                'verbose_name_plural': 'usuários',
                'ordering': ('email',),
            },
            managers=[
                ('objects', accounts.managers.UserManager()),
            ],
        ),
    ]
```

O `accounts/migrations/__init__.py` e o `accounts/__init__.py` são arquivos vazios.

```python
# template/accounts/apps.py
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'
    verbose_name = 'contas'
```

### Forms e admin

```python
# template/accounts/forms.py
from django import forms
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm, UserCreationForm

from .models import User


class SignupForm(UserCreationForm):
    """Cadastro pelo site: e-mail, nome e senha."""

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class CustomUserCreationForm(AdminUserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email',)
```

* `SignupForm` herda do `UserCreationForm`, que já cuida das duas senhas e dos validadores de senha; só trocamos os campos.
* `ProfileForm` deixa o usuário editar o nome.
* Os dois últimos forms servem ao admin, que por padrão espera um campo `username`.

```python
# template/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Dados pessoais', {'fields': ('first_name', 'last_name')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2')}),
    )
```

### Views e urls

O template usa as views do próprio Django para login, logout, troca e reset de senha. Só cadastro e perfil são views novas:

```python
# template/accounts/views.py
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import ProfileForm, SignupForm


class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('core:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(self.request, 'Conta criada. Bem-vindo!')
        return response


class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'registration/profile.html'
    success_url = reverse_lazy('profile')
    success_message = 'Perfil atualizado.'

    def get_object(self, queryset=None):
        return self.request.user
```

* `SignupView` cria o usuário e já faz o login. O argumento `backend` do `login()` é obrigatório quando o usuário acabou de ser criado e não passou pelo `authenticate()`.
* `ProfileView` edita o próprio usuário: o `get_object` devolve `request.user`, então ninguém edita o perfil de outra pessoa.

```python
# template/accounts/urls.py
from django.urls import include, path

from . import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    # login, logout, password_change, password_reset (+ done, confirm, complete)
    path('', include('django.contrib.auth.urls')),
]
```

O `include('django.contrib.auth.urls')` traz as rotas `login`, `logout`, `password_change`, `password_change_done`, `password_reset`, `password_reset_done`, `password_reset_confirm` e `password_reset_complete`. Como o include está em `accounts/` no `urls.py` do projeto, as telas ficam em `/accounts/login/`, `/accounts/signup/`, `/accounts/password_reset/` e assim por diante.

### Templates em português

Todos os formulários usam um include, para não repetir o `<form>`:

```html
<!-- template/accounts/templates/registration/_form.html -->
<form method="post">
  {% csrf_token %}
  {{ form }}
  <button type="submit">{{ button }}</button>
</form>
```

```html
<!-- template/accounts/templates/registration/login.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>Entrar</h2>
    {% include 'registration/_form.html' with button='Entrar' %}
    <small><a href="{% url 'password_reset' %}">Esqueci minha senha</a> · <a href="{% url 'signup' %}">Criar conta</a></small>
  </article>
{% endblock %}
```

O formulário de login do Django (`AuthenticationForm`) chama o campo de `username`, mas o rótulo vem do `USERNAME_FIELD`, então a tela mostra "E-mail".

```html
<!-- template/accounts/templates/registration/signup.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>Criar conta</h2>
    {% include 'registration/_form.html' with button='Criar conta' %}
    <small>Já tem conta? <a href="{% url 'login' %}">Entrar</a></small>
  </article>
{% endblock %}
```

```html
<!-- template/accounts/templates/registration/profile.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>Meu perfil</h2>
    <p>{{ user.email }}</p>
    {% include 'registration/_form.html' with button='Salvar' %}
    <a href="{% url 'password_change' %}">Trocar a senha</a>
  </article>
{% endblock %}
```

```html
<!-- template/accounts/templates/registration/password_change_form.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>Trocar a senha</h2>
    {% include 'registration/_form.html' with button='Trocar a senha' %}
  </article>
{% endblock %}
```

```html
<!-- template/accounts/templates/registration/password_change_done.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>Senha alterada</h2>
    <p>Sua senha foi trocada com sucesso.</p>
    <a href="{% url 'profile' %}">Voltar ao perfil</a>
  </article>
{% endblock %}
```

```html
<!-- template/accounts/templates/registration/password_reset_form.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>Esqueci minha senha</h2>
    <p>Informe seu e-mail e enviaremos um link para criar uma senha nova.</p>
    {% include 'registration/_form.html' with button='Enviar link' %}
  </article>
{% endblock %}
```

```html
<!-- template/accounts/templates/registration/password_reset_done.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>Confira o seu e-mail</h2>
    <p>Se houver uma conta com esse e-mail, você vai receber o link em instantes.</p>
  </article>
{% endblock %}
```

```html
<!-- template/accounts/templates/registration/password_reset_confirm.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    {% if validlink %}
      <h2>Senha nova</h2>
      {% include 'registration/_form.html' with button='Salvar senha' %}
    {% else %}
      <h2>Link inválido</h2>
      <p>Este link já foi usado ou expirou.</p>
      <a href="{% url 'password_reset' %}">Pedir um link novo</a>
    {% endif %}
  </article>
{% endblock %}
```

```html
<!-- template/accounts/templates/registration/password_reset_complete.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>Senha alterada</h2>
    <p>Pronto! Agora é só entrar com a senha nova.</p>
    <a href="{% url 'login' %}" role="button">Entrar</a>
  </article>
{% endblock %}
```

O assunto e o corpo do e-mail de reset também são templates. O assunto precisa ter uma linha só:

```text
{# template/accounts/templates/registration/password_reset_subject.txt #}
Redefinição de senha — {{ domain }}
```

```text
{# template/accounts/templates/registration/password_reset_email.html #}
{% autoescape off %}Olá!

Recebemos um pedido para redefinir a senha da conta {{ user.email }}.

Clique no link abaixo para criar uma senha nova:

{{ protocol }}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}

Se não foi você, ignore este e-mail.
{% endautoescape %}
```

O `{% autoescape off %}` evita que o link seja escapado como HTML, já que o e-mail é texto puro. As variáveis `protocol`, `domain`, `uid`, `token` e `user` vêm da `PasswordResetView`.

## Passo 7: a app core, o que todo projeto repete

### Modelos abstratos

```python
# template/core/models.py
import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """Preenche created e modified sozinho."""

    created = models.DateTimeField('criado em', auto_now_add=True)
    modified = models.DateTimeField('modificado em', auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Chave primária UUID em vez de 1, 2, 3..."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class ActiveQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def inactive(self):
        return self.filter(active=False)


class ActiveModel(models.Model):
    """Desativa o registro sem apagar: Model.objects.active() e .inactive()."""

    active = models.BooleanField('ativo', default=True)

    objects = ActiveQuerySet.as_manager()

    class Meta:
        abstract = True
```

* `TimeStampedModel`: `class Pedido(TimeStampedModel)` ganha `created` e `modified` preenchidos sozinhos.
* `UUIDModel`: chave primária UUID em vez de 1, 2, 3 (não dá para adivinhar o próximo id pela URL).
* `ActiveModel`: campo `active` e um manager com `.active()` e `.inactive()`, como em `Produto.objects.active()`.

Como são abstratos, não criam tabela e não precisam de migração. A app `core` nem tem pasta `migrations`.

### Backend de e-mail legível

```python
# template/core/mail.py
from django.core.mail.backends.console import EmailBackend


class ReadableConsoleEmailBackend(EmailBackend):
    """Mostra o e-mail legível no terminal: acentos e link inteiros.

    O backend de console do Django imprime a mensagem MIME crua, com o corpo
    codificado (quoted-printable), o que quebra acentos e links longos.
    """

    def write_message(self, message):
        self.stream.write(f'Subject: {message.subject}\n')
        self.stream.write(f'From: {message.from_email}\n')
        self.stream.write(f'To: {", ".join(message.to)}\n\n')
        self.stream.write(f'{message.body}\n')
        self.stream.write('-' * 79)
        self.stream.write('\n')
```

O backend de console do Django imprime a mensagem MIME crua. Como o corpo vai codificado, os acentos aparecem como `=C3=A1` e o link pode sair quebrado em várias linhas. Este backend herda do console e reescreve só o `write_message`, imprimindo assunto, remetente, destinatário e o corpo como texto.

### Health check, contexto e urls

```python
# template/core/views.py
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render


def index(request):
    return render(request, 'core/index.html')


def health(request):
    """Health check para o deploy: responde 200 se o banco estiver de pé."""
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    return JsonResponse({'status': 'ok'})
```

A rota `/health/` faz um `SELECT 1` no banco e responde `{"status": "ok"}`. Serviços de deploy e balanceadores usam esse tipo de rota para saber se a aplicação está de pé.

```python
# template/core/context_processors.py
from django.conf import settings


def project(request):
    """Deixa {{ project_name }} disponível em todo template."""
    return {'project_name': getattr(settings, 'PROJECT_NAME', '')}
```

O `PROJECT_NAME` vem do `settings.py.jinja` (`PROJECT_NAME = '{{ project_name }}'`), e o context processor o deixa disponível em todos os templates. Assim, o `base.html` não precisa ser `.jinja`.

```python
# template/core/urls.py
from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('health/', views.health, name='health'),
]
```

```python
# template/core/apps.py
from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
```

### base.html, menu e mensagens

```html
<!-- template/core/templates/base.html -->
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}{{ project_name }}{% endblock %}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
</head>
<body>
  {% include 'includes/nav.html' %}
  <main class="container">
    {% include 'includes/messages.html' %}
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

```html
<!-- template/core/templates/includes/nav.html -->
<header class="container">
  <nav>
    <ul>
      <li><a href="{% url 'core:index' %}"><strong>{{ project_name }}</strong></a></li>
    </ul>
    <ul>
      {% if user.is_authenticated %}
        <li><a href="{% url 'profile' %}">{{ user.email }}</a></li>
        <li>
          <form method="post" action="{% url 'logout' %}" style="margin: 0">
            {% csrf_token %}
            <button type="submit" class="outline">Sair</button>
          </form>
        </li>
      {% else %}
        <li><a href="{% url 'login' %}">Entrar</a></li>
        <li><a href="{% url 'signup' %}" role="button">Criar conta</a></li>
      {% endif %}
    </ul>
  </nav>
</header>
```

```html
<!-- template/core/templates/includes/messages.html -->
{% for message in messages %}
  <article{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</article>
{% endfor %}
```

```html
<!-- template/core/templates/core/index.html -->
{% extends 'base.html' %}

{% block content %}
  <h1>{{ project_name }}</h1>
  {% if user.is_authenticated %}
    <p>Você entrou como <strong>{{ user.email }}</strong>.</p>
  {% else %}
    <p><a href="{% url 'login' %}">Entre</a> ou <a href="{% url 'signup' %}">crie uma conta</a>.</p>
  {% endif %}
{% endblock %}
```

O CSS é o Pico CSS via CDN ([https://picocss.com/](https://picocss.com/)), que estiliza o HTML sem precisar de classes. O menu muda conforme o login, e as mensagens do framework `messages` (como "Conta criada" e "Perfil atualizado") aparecem em todas as páginas.

## Passo 8: os testes

São 15 testes, todos vindos com o template. Os da `accounts` cobrem o model, o login com e-mail (inclusive com maiúsculas), o cadastro, o perfil e o fluxo completo de reset de senha:

```python
# template/accounts/tests.py
import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user_with_email(self):
        user = User.objects.create_user(email='ana@email.com', password='s3nh4-forte!')
        self.assertEqual(user.email, 'ana@email.com')
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password('s3nh4-forte!'))

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='s3nh4-forte!')

    def test_create_superuser(self):
        user = User.objects.create_superuser(email='admin@email.com', password='s3nh4-forte!')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_has_no_username(self):
        self.assertFalse(hasattr(User, 'username') and User.username is not None)

    def test_str_is_email(self):
        user = User.objects.create_user(email='ana@email.com', password='s3nh4-forte!')
        self.assertEqual(str(user), 'ana@email.com')


class LoginTests(TestCase):
    def setUp(self):
        User.objects.create_user(email='ana@email.com', password='s3nh4-forte!')

    def test_login_with_email(self):
        response = self.client.post(
            reverse('login'), {'username': 'ana@email.com', 'password': 's3nh4-forte!'}
        )
        self.assertRedirects(response, reverse('core:index'))

    def test_login_ignores_case(self):
        response = self.client.post(
            reverse('login'), {'username': 'Ana@Email.com', 'password': 's3nh4-forte!'}
        )
        self.assertRedirects(response, reverse('core:index'))

    def test_login_wrong_password(self):
        response = self.client.post(
            reverse('login'), {'username': 'ana@email.com', 'password': 'errada'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class SignupTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(reverse('signup'), {
            'email': 'bia@email.com',
            'first_name': 'Bia',
            'last_name': 'Souza',
            'password1': 's3nh4-forte!',
            'password2': 's3nh4-forte!',
        })
        self.assertRedirects(response, reverse('core:index'))
        self.assertTrue(User.objects.filter(email='bia@email.com').exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class ProfileTests(TestCase):
    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")

    def test_profile_updates_name(self):
        user = User.objects.create_user(email='ana@email.com', password='s3nh4-forte!')
        self.client.force_login(user)
        self.client.post(reverse('profile'), {'first_name': 'Ana', 'last_name': 'Lima'})
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Ana')


class PasswordResetTests(TestCase):
    def test_full_password_reset_flow(self):
        User.objects.create_user(email='ana@email.com', password='senha-antiga!')

        # 1. Pede o link
        response = self.client.post(reverse('password_reset'), {'email': 'ana@email.com'})
        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Redefinição de senha', mail.outbox[0].subject)

        # 2. Abre o link do e-mail
        link = re.search(r'http://testserver(/accounts/reset/\S+)', mail.outbox[0].body).group(1)
        response = self.client.get(link, follow=True)
        self.assertTrue(response.context['validlink'])

        # 3. Define a senha nova
        response = self.client.post(response.redirect_chain[-1][0], {
            'new_password1': 'senha-nova-123!',
            'new_password2': 'senha-nova-123!',
        })
        self.assertRedirects(response, reverse('password_reset_complete'))

        # 4. Entra com a senha nova
        self.assertTrue(self.client.login(username='ana@email.com', password='senha-nova-123!'))
```

Durante os testes, o Django troca o backend de e-mail por um que guarda as mensagens em `mail.outbox`, então o teste lê o link de reset direto do corpo do e-mail e percorre o fluxo inteiro.

```python
# template/core/tests.py
from io import StringIO

from django.core.mail import EmailMessage
from django.test import TestCase
from django.urls import reverse

from .mail import ReadableConsoleEmailBackend


class HealthTests(TestCase):
    def test_health(self):
        response = self.client.get(reverse('core:health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})


class IndexTests(TestCase):
    def test_index(self):
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)


class ReadableConsoleEmailBackendTests(TestCase):
    def test_writes_readable_message(self):
        stream = StringIO()
        backend = ReadableConsoleEmailBackend(stream=stream)
        message = EmailMessage('Redefinição de senha', 'Olá, você!', 'a@a.com', ['b@b.com'])
        backend.send_messages([message])
        output = stream.getvalue()
        self.assertIn('Subject: Redefinição de senha', output)
        self.assertIn('Olá, você!', output)
```

## Passo 9: versionando o template

O `copier update` depende de tags git. Faça o commit e marque a versão:

```
git add -A
git commit -m "Template Django com login por e-mail"
git tag v1.0.0
```

Se publicar o template no GitHub, envie as tags também (`git push --tags`).

## Passo 10: gerando projetos

Com o template no GitHub, use o prefixo `gh:`:

```
copier copy --trust gh:rg3915/django-auth-template loja
```

Também dá para usar o caminho local da pasta do template, sem publicar nada:

```
copier copy --trust ~/django-auth-template loja
```

O Copier faz as três perguntas:

```
? Nome do projeto
   Loja
? Nome do pacote Python
   loja
? Banco de dados
   sqlite
```

E depois cria os arquivos e roda as tasks:

```
Copying from template version 1.0.0
    create  .copier-answers.yml
    create  core
    create  core/mail.py
    ...
    create  pyproject.toml
 > Running task 1 of 4: git init
 > Running task 2 of 4: uv sync
 > Running task 3 of 4: uv run python contrib/env_gen.py
.env criado.
 > Running task 4 of 4: uv run python manage.py migrate
Operations to perform:
  Apply all migrations: accounts, admin, auth, contenttypes, sessions
...
  Applying accounts.0001_initial... OK
...
```

### Segundo projeto, sem perguntas

Com `--defaults`, o Copier usa os valores padrão, e `-d` responde as perguntas pela linha de comando:

```
copier copy --trust --defaults -d project_name=Blog -d database=postgres gh:rg3915/django-auth-template blog
```

Como o banco é Postgres, a task do `migrate` é pulada. Compare os dois projetos:

```
$ diff loja/pyproject.toml blog/pyproject.toml
2c2
< name = "loja"
---
> name = "blog"
4c4
< description = "Loja"
---
> description = "Blog"
9a10
>     "psycopg[binary]>=3.3.6",
```

O mesmo template, e o blog ganhou o driver do Postgres sozinho. Para usá-lo, crie o banco `blog` no seu Postgres (ou ajuste a `DATABASE_URL` no `.env`) e rode `uv run python manage.py migrate`.

### Superusuário, testes e servidor

```
cd loja && uv run python manage.py createsuperuser
```

```
E-mail: admin@loja.com
Password:
Password (again):
Superuser created successfully.
```

Ele não pergunta o username: só e-mail e senha.

```
uv run python manage.py test
```

```
Found 15 test(s).
...
Ran 15 tests

OK
```

```
uv run python manage.py runserver
```

### O e-mail de reset chegando

Entre em `http://127.0.0.1:8000/accounts/login/` com o e-mail, saia e clique em "Esqueci minha senha". Depois de clicar em "Enviar link", o e-mail aparece no terminal do `runserver`, legível:

```
Subject: Redefinição de senha — 127.0.0.1:8000
From: nao-responda@loja.com
To: admin@loja.com

Olá!

Recebemos um pedido para redefinir a senha da conta admin@loja.com.

Clique no link abaixo para criar uma senha nova:

http://127.0.0.1:8000/accounts/reset/MQ/<token>/

Se não foi você, ignore este e-mail.

-------------------------------------------------------------------------------
```

O link funciona de verdade: ele abre a tela de senha nova (`password_reset_confirm`, do próprio Django). Sem servidor de e-mail e sem conta em lugar nenhum. Em produção, troque uma linha no `.env`:

```
# .env de produção
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

## Passo 11: copier update

Melhorou o template? Por exemplo, criou um rodapé em `core/templates/includes/footer.html` e o incluiu no `base.html`. Faça o commit no template e crie uma tag nova:

```
git tag v1.1.0 && git push --tags
```

No projeto (com o git limpo, tudo commitado):

```
copier update --trust
```

```
Updating to template version 1.1.0
    identical  loja/settings.py
    overwrite  core/templates/base.html
    create     core/templates/includes/footer.html
```

O Copier lê o `.copier-answers.yml` (versão e respostas), gera o projeto na versão antiga e na nova, e aplica a diferença por cima das suas alterações (um merge de três vias). O que não fechar vira marcador de conflito no arquivo, como num merge do git. Por isso:

* O template precisa ser um repositório git com tags.
* O projeto precisa estar com o git limpo antes do update.
* Não edite o `.copier-answers.yml` na mão.

Repare que as `_tasks` rodam de novo no update; é por isso que o `env_gen.py` não sobrescreve um `.env` existente. Documentação do update: [https://copier.readthedocs.io/en/stable/updating/](https://copier.readthedocs.io/en/stable/updating/).

## Resumo

Um template e quantos projetos Django você quiser: login por e-mail com a migração inicial já pronta, cadastro, perfil, troca e reset de senha, app `core` com modelos abstratos, health check, e-mail legível no terminal e 15 testes, tudo em um comando. E, quando o template evolui, os projetos acompanham com `copier update`.

## Comandos do vídeo

```
uv tool install copier
copier copy --trust gh:rg3915/django-auth-template loja
copier copy --trust --defaults -d project_name=Blog -d database=postgres gh:rg3915/django-auth-template blog
cd loja && uv run python manage.py createsuperuser
uv run python manage.py test
uv run python manage.py runserver
copier update --trust
```

## Prompt para a sua IA

> Crie um template do Copier para projetos Django 6, versionado em git com a tag v1.0.0.
>
> Dentro do arquivo copier.yml, faça três perguntas: nome do projeto, nome do pacote Python (gerado a partir do nome, com validação) e banco de dados (Postgres ou SQLite). Use a chave _subdirectory: template e depois adicione as _tasks, que vão rodar git init, uv sync, um script que gera o .env com uma SECRET_KEY nova e o migrate — esse último só quando o banco for SQLite.
>
> Crie uma app accounts com um usuário customizado: sem username, usando o e-mail único como USERNAME_FIELD, e com um manager em que o login não diferencia maiúsculas de minúsculas. Deixe a migração inicial pronta dentro do template, para o AUTH_USER_MODEL existir desde o primeiro migrate. Inclua cadastro, perfil, login, logout, troca de senha e reset de senha, usando as views do próprio Django, com templates em português.
>
> Crie também uma app core com três modelos abstratos (TimeStampedModel, UUIDModel, ActiveModel), um base.html com menu e mensagens, uma rota /health/ e um backend de e-mail de console que mostre a mensagem legível, com acentos.
>
> Configure o settings com python-decouple e dj-database-url, idioma pt-br e fuso de São Paulo. Escreva testes para o login por e-mail e para o fluxo completo de reset de senha.

## Short

* <!--yt-pending 6jqsywJzYG4 short-->Todo projeto Django começa igual? Conheça o Copier<!--/yt-pending--> — 09/10/2026, às 10:00.
