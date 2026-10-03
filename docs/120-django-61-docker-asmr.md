# Django 6.1 + Docker ASMR Programming - No Talking

Publicado em 01/10/2026.

<a href="https://youtu.be/QA7Zpk8T4S4">
    <img src="../.gitbook/assets/youtube.png">
</a>

Django 6.1 do zero, sem narração: só o teclado. Um projeto completo, tudo no Docker: PostgreSQL 18, Mailpit e o Django 6.1 instalado com o **uv** dentro do container. Código em inglês, docstrings em português e templates HTML escritos com **Emmet**.

## O que é construído

* **core**: models abstratos (`TimeStampedModel` e `ActiveModel`) e o `base.html`.
* **accounts**: usuário com e-mail no login, logout e todo o fluxo de reset de senha (e-mail no Mailpit).
* **person**: cadastro de funcionários (`Employee`), grupos Vendedor e Gerente, e permissões (o vendedor não vê salário nem exclui; o gerente pode tudo).
* Novidade do Django 6.1: o e-mail se configura no `MAILERS`.

### Capítulos

* 00:00 Abertura
* 00:08 Docker: Dockerfile, compose.yaml e .env
* 01:26 Django 6.1 com uv, dentro do Docker
* 02:21 settings.py: apps, PostgreSQL 18, MAILERS (Mailpit)
* 03:53 App core: models abstratos e base.html
* 07:47 App accounts: login com e-mail e reset de senha
* 13:52 App person: funcionários, grupos e permissões
* 21:42 Subindo tudo: migrations, grupos e usuários
* 23:33 Navegando: vendedor, gerente, reset de senha e admin

## O que você vai construir

Um sistema pequeno de uma empresa, com três apps:

* `core`: dois models abstratos reaproveitáveis, a página inicial, o `base.html` e a página de acesso negado (`403.html`).
* `accounts`: um `User` customizado que entra com o **e-mail** (não existe `username`), com login, logout e o fluxo completo de "esqueci minha senha". O e-mail de reset cai no **Mailpit**, uma caixa de entrada falsa que roda no Docker.
* `person`: o cadastro de funcionários (`Employee`), com dois grupos: **Vendedor** (vê a lista e cadastra, mas não edita, não exclui e não vê o salário) e **Gerente** (pode tudo).

Tudo roda no Docker: o PostgreSQL 18, o Mailpit e o próprio Django. Você não precisa de Python instalado na máquina, só do Docker.

## Pré-requisitos

* Docker com o Docker Compose (o comando `docker compose`).
* Noções de Django: models, views, urls e templates.

Documentação de apoio:

* uv: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
* Mailpit: [https://mailpit.axllent.org/](https://mailpit.axllent.org/)
* E-mail no Django 6.1: [https://docs.djangoproject.com/en/6.1/topics/email/](https://docs.djangoproject.com/en/6.1/topics/email/)
* Pico CSS (usado no `base.html`): [https://picocss.com/](https://picocss.com/)

## Passo 1: Dockerfile, compose.yaml e .env

Crie a pasta do projeto:

```
mkdir empresa && cd empresa
```

O `Dockerfile` é mínimo: uma imagem do Python 3.14 com o `uv` copiado da imagem oficial da Astral.

```dockerfile
# Dockerfile
FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app
```

* `COPY --from=ghcr.io/astral-sh/uv:latest` traz os binários `uv` e `uvx` sem precisar instalar nada com `pip`.
* `UV_PROJECT_ENVIRONMENT=/opt/venv` faz o uv criar o ambiente virtual fora da pasta `/app`. Isso é importante porque a pasta `/app` é o seu código montado como volume: se o `.venv` ficasse ali, ele apareceria na sua máquina com binários do Linux.
* `UV_LINK_MODE=copy` evita o aviso de hardlink, já que o cache e o venv ficam em sistemas de arquivos diferentes.
* Repare que o Dockerfile **não** instala as dependências. Quem faz isso é o `uv run`, na hora de rodar o comando (ele sincroniza o ambiente com o `pyproject.toml` antes de executar).

O `compose.yaml` sobe três serviços:

```yaml
# compose.yaml
services:
  db:
    image: postgres:18-alpine
    env_file: .env
    volumes:
      - pgdata:/var/lib/postgresql

  mailpit:
    image: axllent/mailpit
    ports:
      - "8025:8025"

  web:
    build: .
    command: uv run python manage.py runserver 0.0.0.0:8000
    env_file: .env
    volumes:
      - .:/app
      - venv:/opt/venv
    ports:
      - "8000:8000"
    depends_on:
      - db
      - mailpit

volumes:
  pgdata:
  venv:
```

* `db`: o PostgreSQL 18. A partir da versão 18, a imagem oficial guarda os dados em uma subpasta da versão dentro de `/var/lib/postgresql`, por isso o volume é montado nessa pasta (e não em `/var/lib/postgresql/data`, como nas versões antigas). Ele lê `POSTGRES_DB`, `POSTGRES_USER` e `POSTGRES_PASSWORD` do `.env` para criar o banco.
* `mailpit`: recebe os e-mails por SMTP na porta 1025 (dentro da rede do Docker) e mostra uma caixa de entrada em `http://localhost:8025`.
* `web`: o Django. O volume `.:/app` faz qualquer alteração no código valer na hora (o `runserver` recarrega), e o volume nomeado `venv` guarda o ambiente virtual entre uma execução e outra.

O `.env` guarda a configuração. Os valores abaixo são de exemplo, troque a `SECRET_KEY` e a senha do banco:

```
# .env
SECRET_KEY=troque-esta-chave
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=empresa
POSTGRES_USER=postgres
POSTGRES_PASSWORD=troque-esta-senha
POSTGRES_HOST=db
EMAIL_HOST=mailpit
EMAIL_PORT=1025
```

Repare que o host do banco é `db` e o do e-mail é `mailpit`: dentro da rede do Docker, cada serviço é encontrado pelo nome. Não esqueça de colocar o `.env` no `.gitignore`.

## Passo 2: Django 6.1 com uv, dentro do Docker

Construa a imagem e crie o projeto Python com o uv, tudo pelo container:

```
docker compose build
docker compose run --rm web uv init --bare --name empresa
docker compose run --rm web uv add django psycopg[binary] python-decouple
```

* `uv init --bare` cria só o `pyproject.toml`, sem arquivos de exemplo.
* `uv add` instala as dependências no `/opt/venv` e grava as versões no `pyproject.toml` e no `uv.lock`.

O `pyproject.toml` fica assim:

```toml
# pyproject.toml
[project]
name = "empresa"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = [
    "django>=6.1.1",
    "psycopg[binary]>=3.3.6",
    "python-decouple>=3.8",
]
```

Agora crie o projeto (com o nome `config`, na pasta atual) e as três apps:

```
docker compose run --rm web uv run django-admin startproject config .
docker compose run --rm web uv run python manage.py startapp core
docker compose run --rm web uv run python manage.py startapp accounts
docker compose run --rm web uv run python manage.py startapp person
```

Como a pasta `/app` é um volume, os arquivos criados dentro do container aparecem na sua máquina. Crie também as pastas de templates e a do comando customizado:

```
mkdir -p core/templates/core
mkdir -p accounts/templates/registration
mkdir -p person/templates/person
mkdir -p person/management/commands
touch person/management/__init__.py person/management/commands/__init__.py
```

## Passo 3: settings.py com PostgreSQL 18 e MAILERS

Estas são as partes do `config/settings.py` que mudam em relação ao arquivo gerado pelo `startproject` (o resto fica igual):

```python
# config/settings.py
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv())

INSTALLED_APPS = [
    'core',
    'accounts',
    'person',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# MIDDLEWARE, ROOT_URLCONF, TEMPLATES e WSGI_APPLICATION: iguais ao gerado.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('POSTGRES_HOST', default='db'),
        'PORT': 5432,
    }
}

# AUTH_PASSWORD_VALIDATORS: igual ao gerado.

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'OPTIONS': {
            'host': config('EMAIL_HOST', default='localhost'),
            'port': config('EMAIL_PORT', default=1025, cast=int),
        },
    },
}

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'core:index'
LOGOUT_REDIRECT_URL = 'core:index'

DEFAULT_FROM_EMAIL = 'nao-responda@empresa.com'
```

O que mudou e por quê:

* **python-decouple**: `config()` lê do `.env` (ou das variáveis de ambiente). `cast=bool` transforma `"True"` em `True`, e `Csv()` transforma `localhost,127.0.0.1` em uma lista.
* **As apps do projeto vêm primeiro** no `INSTALLED_APPS`. O Django procura templates na ordem das apps, então os templates de `accounts/templates/registration/` têm prioridade sobre os templates padrão do admin com o mesmo nome.
* **PostgreSQL**: o driver é o `psycopg` 3, instalado no passo anterior.
* **MAILERS**: é a novidade do Django 6.1. Em vez de espalhar `EMAIL_BACKEND`, `EMAIL_HOST` e `EMAIL_PORT` pelo settings, você declara um dicionário de "mailers", cada um com o seu `BACKEND` e as suas `OPTIONS`. O `default` é o usado pelo `send_mail` e pelo reset de senha. Aqui ele aponta para o SMTP do Mailpit.
* **AUTH_USER_MODEL**: aponta para o `User` que você vai criar na app `accounts`. Ele precisa estar definido **antes** do primeiro `migrate`.
* **LOGIN_URL e redirecionamentos**: `login` é o nome da rota do Django; `core:index` é a página inicial.

## Passo 4: app core

### Models abstratos

```python
# core/models.py
from django.db import models


class TimeStampedModel(models.Model):
    """Guarda quando o registro foi criado e quando foi alterado pela última vez."""

    created = models.DateTimeField('criado em', auto_now_add=True)
    modified = models.DateTimeField('modificado em', auto_now=True)

    class Meta:
        abstract = True


class ActiveModel(models.Model):
    """Permite desativar um registro sem apagá-lo do banco."""

    active = models.BooleanField('ativo', default=True)

    class Meta:
        abstract = True
```

`abstract = True` significa que esses models não viram tabela. Eles só emprestam os campos para quem herdar deles, como o `Employee` mais adiante.

### View e urls

```python
# core/views.py
from django.shortcuts import render


def index(request):
    return render(request, 'core/index.html')
```

```python
# core/urls.py
from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
]
```

### base.html

No vídeo os templates são escritos com **Emmet** (abreviações que o editor expande em HTML). O resultado é este:

```html
<!-- core/templates/base.html -->
<!DOCTYPE html>
<html lang="pt-br" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Empresa{% endblock %}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
  <style>nav form { margin: 0; }</style>
</head>
<body>
  <header class="container">
    <nav>
      <ul>
        <li><a href="{% url 'core:index' %}"><strong>Empresa</strong></a></li>
      </ul>
      <ul>
        {% if user.is_authenticated %}
          <li><a href="{% url 'person:employee_list' %}">Funcionários</a></li>
          <li>{{ user.email }}</li>
          <li>
            <form method="post" action="{% url 'logout' %}">
              {% csrf_token %}
              <button type="submit" class="outline">Sair</button>
            </form>
          </li>
        {% else %}
          <li><a href="{% url 'login' %}" role="button">Entrar</a></li>
        {% endif %}
      </ul>
    </nav>
  </header>
  <main class="container">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

O botão **Sair** é um formulário com `method="post"`: desde o Django 5.0, a `LogoutView` só aceita POST.

### index.html e 403.html

```html
<!-- core/templates/core/index.html -->
{% extends 'base.html' %}

{% block content %}
  <h1>Bem-vindo à Empresa</h1>
  {% if user.is_authenticated %}
    <p>Você entrou como <strong>{{ user.email }}</strong>.</p>
    <p>
      Grupos:
      {% for group in user.groups.all %}
        <mark>{{ group.name }}</mark>
      {% empty %}
        nenhum
      {% endfor %}
    </p>
  {% else %}
    <p>Entre com o seu e-mail para ver os funcionários.</p>
  {% endif %}
{% endblock %}
```

```html
<!-- core/templates/403.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>Acesso negado</h2>
    <p>Você não tem permissão para acessar esta página.</p>
    <a href="{% url 'core:index' %}">Voltar para o início</a>
  </article>
{% endblock %}
```

O `403.html` fica na raiz de `core/templates/`. Quando uma view levanta `PermissionDenied`, o Django procura um template chamado `403.html` e o usa no lugar da página padrão.

### urls do projeto

```python
# config/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('employees/', include('person.urls')),
    path('admin/', admin.site.urls),
]
```

## Passo 5: app accounts, login com e-mail

### O model User e o manager

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Cria usuários usando o e-mail no lugar do username."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        email = self.normalize_email(email)
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
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Usuário que entra com o e-mail: o username sai e o e-mail vira único."""

    username = None
    email = models.EmailField('e-mail', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
```

* Herdar de `AbstractUser` mantém tudo o que o usuário padrão tem (nome, `is_staff`, grupos, permissões). Só o `username` sai (`username = None`).
* `email` vira `unique=True`, porque agora ele identifica o usuário.
* `USERNAME_FIELD = 'email'` diz ao Django qual campo usar no login, e `REQUIRED_FIELDS = []` faz o `createsuperuser` pedir só e-mail e senha.
* O manager padrão do Django (`UserManager` de `django.contrib.auth`) exige `username`. Por isso escrevemos um manager próprio, com `create_user` e `create_superuser` recebendo o e-mail. `use_in_migrations = True` deixa o manager disponível dentro das migrations.

### Forms e admin

O admin de usuários do Django usa forms que conhecem o campo `username`. Para o nosso `User`, criamos versões com o campo `email`:

```python
# accounts/forms.py
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm

from .models import User


class CustomUserCreationForm(AdminUserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email',)
```

```python
# accounts/admin.py
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
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2')}),
    )
```

O `UserAdmin` do Django tem `fieldsets`, `ordering` e `search_fields` com `username`. Se você não sobrescrever, o admin quebra ao abrir um usuário. O campo `groups` em **Permissões** é o que você vai usar para colocar alguém no grupo Vendedor ou Gerente pelo admin.

### urls: as views prontas do Django

```python
# accounts/urls.py
from django.urls import include, path

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
]
```

Essa linha traz todas as rotas de autenticação do Django, já com nome: `login`, `logout`, `password_change`, `password_change_done`, `password_reset`, `password_reset_done`, `password_reset_confirm` e `password_reset_complete`. Como o include está em `accounts/`, o login fica em `/accounts/login/`. Você só precisa escrever os templates, na pasta `registration/`.

### Templates de login e reset de senha

```html
<!-- accounts/templates/registration/login.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>Entrar</h2>
    <form method="post">
      {% csrf_token %}
      {{ form }}
      <button type="submit">Entrar</button>
    </form>
    <a href="{% url 'password_reset' %}">Esqueci minha senha</a>
  </article>
{% endblock %}
```

```html
<!-- accounts/templates/registration/password_reset_form.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>Esqueci minha senha</h2>
    <p>Digite o seu e-mail e enviaremos um link para criar uma senha nova.</p>
    <form method="post">
      {% csrf_token %}
      {{ form }}
      <button type="submit">Enviar link</button>
    </form>
  </article>
{% endblock %}
```

```html
<!-- accounts/templates/registration/password_reset_done.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>Confira o seu e-mail</h2>
    <p>Se o e-mail estiver cadastrado, você vai receber o link em instantes.</p>
  </article>
{% endblock %}
```

A mensagem diz "se o e-mail estiver cadastrado" de propósito: a `PasswordResetView` mostra a mesma tela para qualquer e-mail, para ninguém descobrir quem tem conta no sistema.

```html
<!-- accounts/templates/registration/password_reset_confirm.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    {% if validlink %}
      <h2>Nova senha</h2>
      <form method="post">
        {% csrf_token %}
        {{ form }}
        <button type="submit">Salvar senha</button>
      </form>
    {% else %}
      <h2>Link inválido</h2>
      <p>Este link já foi usado ou expirou.</p>
      <a href="{% url 'password_reset' %}">Pedir um link novo</a>
    {% endif %}
  </article>
{% endblock %}
```

A variável `validlink` vem da `PasswordResetConfirmView`: ela é `False` quando o token do link já foi usado ou expirou.

```html
<!-- accounts/templates/registration/password_reset_complete.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>Senha alterada</h2>
    <p>Pronto! Agora é só entrar com a senha nova.</p>
    <a href="{% url 'login' %}" role="button">Entrar</a>
  </article>
{% endblock %}
```

O corpo do e-mail não foi sobrescrito: o Django usa o template `registration/password_reset_email.html` que já vem com ele, traduzido para o português por causa do `LANGUAGE_CODE = 'pt-br'`.

## Passo 6: app person, funcionários e permissões

### O model Employee

```python
# person/models.py
from django.db import models

from core.models import ActiveModel, TimeStampedModel


class Employee(TimeStampedModel, ActiveModel):
    """Funcionário da empresa. O salário só aparece para quem tem a permissão view_salary."""

    class Role(models.TextChoices):
        SELLER = 'seller', 'Vendedor'
        MANAGER = 'manager', 'Gerente'

    name = models.CharField('nome', max_length=100)
    email = models.EmailField('e-mail', unique=True)
    role = models.CharField('cargo', max_length=20, choices=Role)
    salary = models.DecimalField('salário', max_digits=10, decimal_places=2)
    hired_on = models.DateField('admissão')

    class Meta:
        ordering = ('name',)
        verbose_name = 'funcionário'
        verbose_name_plural = 'funcionários'
        permissions = [
            ('view_salary', 'Pode ver o salário'),
        ]

    def __str__(self):
        return self.name
```

* Herdando de `TimeStampedModel` e `ActiveModel`, o `Employee` ganha `created`, `modified` e `active` sem repetir código.
* `Role` é um `TextChoices`: no banco fica gravado `seller` ou `manager`, e na tela aparece "Vendedor" ou "Gerente" (com `get_role_display`).
* Todo model já ganha quatro permissões automáticas: `add_employee`, `change_employee`, `delete_employee` e `view_employee`. Em `Meta.permissions` você cria permissões extras. Aqui, `view_salary` controla quem enxerga o salário.

### Form

```python
# person/forms.py
from django import forms

from .models import Employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ('name', 'email', 'role', 'salary', 'hired_on', 'active')
```

### Views com permissões

```python
# person/views.py
"""CRUD de funcionários.

O PermissionRequiredMixin manda quem não entrou para o login e devolve 403 para quem
entrou mas não tem a permissão.
"""
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import EmployeeForm
from .models import Employee


class EmployeeListView(PermissionRequiredMixin, ListView):
    model = Employee
    permission_required = 'person.view_employee'


class EmployeeCreateView(PermissionRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    permission_required = 'person.add_employee'
    success_url = reverse_lazy('person:employee_list')


class EmployeeUpdateView(PermissionRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    permission_required = 'person.change_employee'
    success_url = reverse_lazy('person:employee_list')


class EmployeeDeleteView(PermissionRequiredMixin, DeleteView):
    model = Employee
    permission_required = 'person.delete_employee'
    success_url = reverse_lazy('person:employee_list')
```

O `PermissionRequiredMixin` vem antes da view genérica e faz duas coisas: quem não está logado é redirecionado para o `LOGIN_URL`; quem está logado mas não tem a permissão recebe `403` (e vê o `403.html` da app `core`). A permissão é escrita como `app_label.codename`.

Esconder o botão no template não basta: se o vendedor digitar `/employees/1/delete/` direto no navegador, é a view que barra.

### urls e admin

```python
# person/urls.py
from django.urls import path

from . import views

app_name = 'person'

urlpatterns = [
    path('', views.EmployeeListView.as_view(), name='employee_list'),
    path('new/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
]
```

```python
# person/admin.py
from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'active')
    list_filter = ('role', 'active')
    search_fields = ('name', 'email')
```

### Templates

Na lista, a variável `perms` (que vem do context processor `auth`) decide o que aparece:

```html
<!-- person/templates/person/employee_list.html -->
{% extends 'base.html' %}

{% block content %}
  <h2>Funcionários</h2>
  {% if perms.person.add_employee %}
    <a href="{% url 'person:employee_create' %}" role="button">Novo funcionário</a>
  {% endif %}
  <table>
    <thead>
      <tr>
        <th>Nome</th>
        <th>E-mail</th>
        <th>Cargo</th>
        {% if perms.person.view_salary %}<th>Salário</th>{% endif %}
        <th></th>
      </tr>
    </thead>
    <tbody>
      {% for employee in object_list %}
        <tr>
          <td>{{ employee.name }}</td>
          <td>{{ employee.email }}</td>
          <td>{{ employee.get_role_display }}</td>
          {% if perms.person.view_salary %}<td>R$ {{ employee.salary }}</td>{% endif %}
          <td>
            {% if perms.person.change_employee %}
              <a href="{% url 'person:employee_update' employee.pk %}">Editar</a>
            {% endif %}
            {% if perms.person.delete_employee %}
              <a href="{% url 'person:employee_delete' employee.pk %}">Excluir</a>
            {% endif %}
          </td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
{% endblock %}
```

O mesmo template serve para cadastrar e editar. Na edição, a `UpdateView` coloca o registro em `object`; no cadastro, `object` é `None`:

```html
<!-- person/templates/person/employee_form.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>{% if object %}Editar{% else %}Novo{% endif %} funcionário</h2>
    <form method="post">
      {% csrf_token %}
      {{ form }}
      <button type="submit">Salvar</button>
    </form>
  </article>
{% endblock %}
```

```html
<!-- person/templates/person/employee_confirm_delete.html -->
{% extends 'base.html' %}

{% block content %}
  <article>
    <h2>Excluir funcionário</h2>
    <p>Tem certeza que deseja excluir <strong>{{ object }}</strong>?</p>
    <form method="post">
      {% csrf_token %}
      <button type="submit" class="secondary">Excluir</button>
      <a href="{% url 'person:employee_list' %}">Cancelar</a>
    </form>
  </article>
{% endblock %}
```

Os nomes `employee_list.html`, `employee_form.html` e `employee_confirm_delete.html` são os que as views genéricas procuram por padrão (`<app>/<model>_<sufixo>.html`), por isso nenhuma view precisou de `template_name`.

### Comando create_groups

Em vez de criar os grupos clicando no admin, um comando deixa isso reproduzível em qualquer ambiente:

```python
# person/management/commands/create_groups.py
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

# Cada grupo recebe só as permissões do app person listadas aqui.
GROUPS = {
    'Vendedor': ['view_employee', 'add_employee'],
    'Gerente': [
        'view_employee',
        'add_employee',
        'change_employee',
        'delete_employee',
        'view_salary',
    ],
}


class Command(BaseCommand):
    help = 'Cria os grupos Vendedor e Gerente com as permissões de cada um.'

    def handle(self, *args, **options):
        for name, codenames in GROUPS.items():
            group, _ = Group.objects.get_or_create(name=name)
            permissions = Permission.objects.filter(
                content_type__app_label='person',
                codename__in=codenames,
            )
            group.permissions.set(permissions)
            self.stdout.write(self.style.SUCCESS(f'{name}: {permissions.count()} permissões'))
```

* `get_or_create` permite rodar o comando várias vezes sem duplicar grupos.
* `group.permissions.set(...)` substitui as permissões do grupo pela lista do dicionário. Se você mudar o dicionário e rodar de novo, o grupo fica exatamente como está escrito no código.
* O filtro por `content_type__app_label='person'` evita pegar uma permissão de mesmo nome de outra app.

## Passo 7: subindo tudo

Suba os três serviços em segundo plano:

```
docker compose up -d
```

Gere e aplique as migrations, e crie os grupos:

```
docker compose exec web uv run python manage.py makemigrations
docker compose exec web uv run python manage.py migrate
docker compose exec web uv run python manage.py create_groups
```

A saída do último comando é:

```
Vendedor: 2 permissões
Gerente: 5 permissões
```

O `create_groups` precisa rodar **depois** do `migrate`, porque as permissões são criadas pelo Django no final das migrations.

Agora crie os usuários e alguns funcionários pelo shell. No Django 5.2 em diante, o `shell` já importa os models sozinho (`User`, `Group`, `Employee`...):

```
docker compose exec web uv run python manage.py shell
```

```python
seller = User.objects.create_user(email='vendedor@empresa.com', password='senha12345')
seller.groups.add(Group.objects.get(name='Vendedor'))
manager = User.objects.create_user(email='gerente@empresa.com', password='senha12345')
manager.groups.add(Group.objects.get(name='Gerente'))
User.objects.create_superuser(email='admin@empresa.com', password='senha12345')
Employee.objects.create(name='Ana Souza', email='ana@empresa.com', role='manager', salary=9500, hired_on='2021-03-01')
Employee.objects.create(name='Bruno Lima', email='bruno@empresa.com', role='seller', salary=4200, hired_on='2023-07-10')
Employee.objects.create(name='Carla Mendes', email='carla@empresa.com', role='seller', salary=4350, hired_on='2024-02-05')
exit()
```

Confira se está tudo de pé com `docker compose ps`.

## Passo 8: testando no navegador

* **Vendedor**: entre em `http://localhost:8000/accounts/login/` com `vendedor@empresa.com`. Na lista de funcionários aparecem o botão "Novo funcionário", mas não a coluna de salário nem os links de editar e excluir. Tente abrir `http://localhost:8000/employees/1/delete/` na mão: a resposta é a página "Acesso negado".
* **Gerente**: saia e entre com `gerente@empresa.com`. Agora a coluna de salário e os links de editar e excluir aparecem.
* **Reset de senha**: saia, clique em "Esqueci minha senha" e digite um e-mail cadastrado. Abra o Mailpit em `http://localhost:8025`: o e-mail está lá, com o link para criar a senha nova. Clique no link, salve a senha e entre com ela. Se clicar no mesmo link de novo, cai na tela "Link inválido".
* **Admin**: entre em `http://localhost:8000/admin/` com `admin@empresa.com`. Em **Grupos** você vê as permissões de cada grupo, e em **Usuários** dá para mudar o grupo de alguém.

Um detalhe para você evoluir: o formulário de cadastro mostra o campo salário também para o vendedor. Um exercício é remover o campo `salary` do form quando o usuário não tiver `person.view_salary` (por exemplo, sobrescrevendo `get_form` na `EmployeeCreateView`).

## Resumo

Com um `Dockerfile` de quatro linhas úteis e um `compose.yaml`, você tem Django 6.1, PostgreSQL 18 e Mailpit rodando sem instalar nada na máquina. O `User` com e-mail precisa existir antes do primeiro `migrate`; o reset de senha sai quase de graça com as views do próprio Django; e as permissões ficam em dois lugares: na view (`PermissionRequiredMixin`, que é quem protege de verdade) e no template (`perms`, que só esconde os botões).

## Série de shorts "Django do zero ASMR"

O vídeo também foi dividido em 21 shorts, publicados um a cada dois dias. Os que ainda não saíram já estão agendados para a data indicada.

| Data | Short |
|---|---|
| 02/10/2026 | [01. Docker: Dockerfile, compose.yaml e .env](https://youtube.com/shorts/pfdNbMxj9XY) |
| 04/10/2026 | <!--yt-pending RYgtFEu_mpo short-->02. Django 6.1 com uv, dentro do Docker<!--/yt-pending--> |
| 06/10/2026 | <!--yt-pending m7VSO2c2XTs short-->03. settings.py: PostgreSQL 18 e MAILERS<!--/yt-pending--> |
| 08/10/2026 | <!--yt-pending DK0wBCVK3uU short-->04. App core: models abstratos, view e urls<!--/yt-pending--> |
| 10/10/2026 | <!--yt-pending rmH2ryVtvJw short-->05. base.html com Emmet<!--/yt-pending--> |
| 12/10/2026 | <!--yt-pending -Yam3-cLrLw short-->06. index.html, 403.html e urls do projeto<!--/yt-pending--> |
| 14/10/2026 | <!--yt-pending 63jfz3rk-wA short-->07. accounts: usuário com login por e-mail<!--/yt-pending--> |
| 16/10/2026 | <!--yt-pending 7dF5xftjqpE short-->08. accounts: forms, admin e urls<!--/yt-pending--> |
| 18/10/2026 | <!--yt-pending n9WEV05jwjE short-->09. Templates de login e reset de senha<!--/yt-pending--> |
| 20/10/2026 | <!--yt-pending GfeXJXgsfh8 short-->10. Reset de senha: confirmar a nova senha<!--/yt-pending--> |
| 22/10/2026 | <!--yt-pending 36IzuFs9NoY short-->11. person: model Employee e form<!--/yt-pending--> |
| 24/10/2026 | <!--yt-pending t6xov5ucwAc short-->12. person: views com permissões<!--/yt-pending--> |
| 26/10/2026 | <!--yt-pending PQPoX2Pj14I short-->13. person: urls e admin<!--/yt-pending--> |
| 28/10/2026 | <!--yt-pending 7E86xgWd31I short-->14. Lista de funcionários com Emmet<!--/yt-pending--> |
| 30/10/2026 | <!--yt-pending Lwnzy3fhyuM short-->15. Form e confirmação de exclusão<!--/yt-pending--> |
| 01/11/2026 | <!--yt-pending XcGmd8gh5v4 short-->16. Comando create_groups: Vendedor e Gerente<!--/yt-pending--> |
| 03/11/2026 | <!--yt-pending ydEBp9u2urE short-->17. Subindo tudo: migrate, grupos e usuários<!--/yt-pending--> |
| 05/11/2026 | <!--yt-pending W_8__T2Lxg4 short-->18. Navegando: o vendedor cadastra, mas não exclui<!--/yt-pending--> |
| 07/11/2026 | <!--yt-pending d5As5VHoWlg short-->19. Navegando: o gerente edita e exclui<!--/yt-pending--> |
| 09/11/2026 | <!--yt-pending 56byLG5r9Zw short-->20. Navegando: reset de senha pelo Mailpit<!--/yt-pending--> |
| 11/11/2026 | <!--yt-pending FF5NhPLtWSw short-->21. Navegando: grupos e permissões no admin<!--/yt-pending--> |
