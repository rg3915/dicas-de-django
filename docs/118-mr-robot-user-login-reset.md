# Se o Elliot usasse Django: User, login e reset de senha

Publicado em 24/09/2026.

**Testado com:** Django 6.0.8, Python 3.13 (no Docker) e PostgreSQL 17.
{: .versoes }

<a href="https://youtu.be/nq1uZju7IW8">
    <img src="../.gitbook/assets/youtube.png">
</a>

As telas do Mr. Robot, mas com o código que a gente escreve de verdade: um app de contas em Django rodando em Docker com Postgres. Neste tutorial vamos montar esse projeto do zero: `Dockerfile` com Python 3.13 e gunicorn, `compose.yml` com Postgres e health check, um `User` customizado que faz login pelo e-mail, as telas de login e de redefinição de senha usando as views prontas do `django.contrib.auth` e, no fim, o shell gerando o token de reset na mão.

## Pré-requisitos

* Docker e Docker Compose.
* Python 3.12 ou superior na máquina, só para criar o projeto (depois tudo roda no contêiner).
* Conhecimento básico de Django (settings, urls, views e templates).

## Criando o projeto

```bash
mkdir fsociety && cd fsociety
python -m venv .venv
source .venv/bin/activate
pip install "Django>=6.0,<6.1" gunicorn Pillow "psycopg[binary]" python-decouple

django-admin startproject config .
python manage.py startapp accounts
mkdir -p accounts/templates/accounts
```

```
# requirements.txt
Django==6.0.8
gunicorn==26.2.0
Pillow==12.3.0
psycopg[binary]==3.3.6
python-decouple==3.8
```

O Pillow é necessário por causa do `ImageField` do avatar.

## Docker: Dockerfile, compose e .env

```dockerfile
# Dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
```

* O `requirements.txt` é copiado antes do resto do código: assim a camada do `pip install` fica em cache e só é refeita quando as dependências mudam.
* `PYTHONUNBUFFERED=1` faz os `print` e os logs aparecerem na hora no `docker compose logs`.
* O gunicorn serve a aplicação WSGI; `--access-logfile -` escreve uma linha por requisição na saída padrão.

```yaml
# compose.yml
services:
  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 10

  web:
    build: .
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
```

O ponto principal é o **health check**. Um `depends_on` simples só espera o contêiner do banco *iniciar*, não o Postgres *aceitar conexões*. Com `healthcheck` (o `pg_isready` roda a cada 5 segundos) e `condition: service_healthy`, o contêiner `web` só sobe quando o banco está pronto. O `$$` escapa o `$` para que a variável seja lida dentro do contêiner, e não pelo Compose.

```bash
# .env
DEBUG=True
SECRET_KEY=troque-esta-chave-por-uma-aleatoria
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=fsociety
POSTGRES_USER=elliot
POSTGRES_PASSWORD=elliot
DB_HOST=db
```

O Compose lê esse `.env` para preencher `${POSTGRES_DB}` e companhia, e o `env_file` entrega as mesmas variáveis ao Django. `DB_HOST=db` é o nome do serviço do banco: dentro da rede do Compose, os serviços se enxergam pelo nome. Não versione o `.env`.

## settings.py

Os trechos que mudam em relação ao gerado pelo `startproject`:

```python
# config/settings.py
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # my apps
    'accounts',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', 'fsociety'),
        'USER': config('POSTGRES_USER', 'elliot'),
        'PASSWORD': config('POSTGRES_PASSWORD', 'elliot'),
        'HOST': config('DB_HOST', 'db'),
        'PORT': config('DB_PORT', 5432, cast=int),
    }
}

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:home'
LOGOUT_REDIRECT_URL = 'accounts:login'

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='no-reply@fsociety.local')
```

* **`AUTH_USER_MODEL = 'accounts.User'`**: diz ao Django que o usuário do projeto é o nosso model. Isso precisa estar definido **antes do primeiro `migrate`**: trocar o model de usuário com o banco já criado é trabalhoso, porque as tabelas de admin, grupos e permissões já apontam para `auth_user`.
* **`LOGIN_REDIRECT_URL`** e **`LOGOUT_REDIRECT_URL`**: para onde ir depois de entrar e de sair.
* **`EMAIL_BACKEND`** de console: o e-mail de reset é impresso no log do contêiner em vez de ser enviado. Em produção, troque por SMTP. No Django 6.1 essa configuração passa a ser feita pelo `MAILERS` (veja a dica 119).

## O model User

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField('e-mail', unique=True)
    avatar = models.ImageField('avatar', upload_to='avatars/', blank=True)
    email_verified = models.BooleanField('e-mail verificado', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
```

* **`AbstractUser`** traz tudo do usuário padrão (senha com hash, `is_staff`, grupos, permissões). Só acrescentamos o que falta.
* **`email` com `unique=True`**: no `AbstractUser` o e-mail não é único; para servir de login, precisa ser.
* **`USERNAME_FIELD = 'email'`**: o campo usado para autenticar passa a ser o e-mail. É ele que o `authenticate()`, o formulário de login e o `createsuperuser` vão pedir.
* **`REQUIRED_FIELDS = ['username']`**: campos extras que o `createsuperuser` pergunta. O `username` continua existindo (e único), mas não é mais o login.
* **`avatar`** e **`email_verified`**: campos do perfil. O `email_verified` fica pronto para um fluxo de confirmação de e-mail.

```python
# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'email_verified', 'is_staff', 'is_active')
    list_filter = ('email_verified', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Perfil', {'fields': ('avatar', 'email_verified')}),
    )
```

Herdar do `UserAdmin` do Django mantém a tela de troca de senha e os formulários com hash; só acrescentamos o bloco "Perfil".

## Login e reset de senha com as views do django.contrib.auth

Não escrevemos lógica de autenticação: herdamos as views prontas e trocamos o template, o formulário e para onde ir depois.

```python
# accounts/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'autofocus': True, 'autocomplete': 'email'}),
    )
```

O `AuthenticationForm` chama o campo de login de `username`, seja qual for o `USERNAME_FIELD`. Aqui só trocamos o campo por um `EmailField`, que valida o formato e mostra o teclado de e-mail no celular.

```python
# accounts/views.py
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from accounts.forms import EmailAuthenticationForm


class LoginView(auth_views.LoginView):
    template_name = 'accounts/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.txt'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


class HomeView(TemplateView):
    template_name = 'accounts/home.html'
```

O fluxo de reset tem quatro passos, cada um com a sua view:

1. `PasswordResetView`: o usuário informa o e-mail. Se existir um usuário ativo com ele, o Django gera um token e envia o e-mail com o link. Por segurança, a resposta é a mesma exista ou não a conta.
2. `PasswordResetDoneView`: a página "verifique seu e-mail".
3. `PasswordResetConfirmView`: a página do link, `reset/<uidb64>/<token>/`. Ela valida o token e mostra o formulário de nova senha.
4. `PasswordResetCompleteView`: a confirmação de que a senha foi trocada.

Como usamos um namespace (`accounts:`), o `success_url` de cada passo precisa ser informado; os padrões do Django apontam para nomes sem namespace.

```python
# accounts/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
```

```python
# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('accounts.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

O `uidb64` é o id do usuário em base64 e o `token` é gerado pelo `default_token_generator`. O token é um hash que inclui a senha atual e o último login do usuário: depois que a senha é trocada, o mesmo link deixa de valer. A validade é definida por `PASSWORD_RESET_TIMEOUT` (padrão de 3 dias).

## Templates

```html
<!-- accounts/templates/accounts/base.html -->
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}fsociety{% endblock %}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
</head>
<body>
  <main class="container">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

```html
<!-- accounts/templates/accounts/home.html -->
{% extends 'accounts/base.html' %}

{% block content %}
  {% if user.is_authenticated %}
    <h1>Hello, {{ user.email }}</h1>
    <form method="post" action="{% url 'accounts:logout' %}">
      {% csrf_token %}
      <button type="submit">Sair</button>
    </form>
  {% else %}
    <h1>Hello, friend.</h1>
    <a href="{% url 'accounts:login' %}" role="button">Entrar</a>
  {% endif %}
{% endblock %}
```

O logout é um `POST` com CSRF: desde o Django 5.0 a `LogoutView` não aceita mais `GET`.

```html
<!-- accounts/templates/accounts/login.html -->
{% extends 'accounts/base.html' %}

{% block title %}Login{% endblock %}

{% block content %}
  <article>
    <h1>Login</h1>
    <form method="post">
      {% csrf_token %}
      {{ form.as_div }}
      <input type="hidden" name="next" value="{{ next }}">
      <button type="submit">Entrar</button>
    </form>
    <a href="{% url 'accounts:password_reset' %}">Esqueci minha senha</a>
  </article>
{% endblock %}
```

```html
<!-- accounts/templates/accounts/password_reset_form.html -->
{% extends 'accounts/base.html' %}

{% block title %}Redefinir senha{% endblock %}

{% block content %}
  <article>
    <h1>Redefinir senha</h1>
    <p>Informe seu e-mail e enviaremos um link para criar uma nova senha.</p>
    <form method="post">
      {% csrf_token %}
      {{ form.as_div }}
      <button type="submit">Enviar link</button>
    </form>
  </article>
{% endblock %}
```

```html
<!-- accounts/templates/accounts/password_reset_done.html -->
{% extends 'accounts/base.html' %}

{% block content %}
  <h1>Verifique seu e-mail</h1>
  <p>Se existir uma conta com esse e-mail, você receberá um link para redefinir a senha.</p>
{% endblock %}
```

```html
<!-- accounts/templates/accounts/password_reset_confirm.html -->
{% extends 'accounts/base.html' %}

{% block content %}
  {% if validlink %}
    <h1>Nova senha</h1>
    <form method="post">
      {% csrf_token %}
      {{ form.as_div }}
      <button type="submit">Salvar nova senha</button>
    </form>
  {% else %}
    <h1>Link inválido</h1>
    <p>O link de redefinição é inválido ou já foi usado. Peça um novo.</p>
  {% endif %}
{% endblock %}
```

```html
<!-- accounts/templates/accounts/password_reset_complete.html -->
{% extends 'accounts/base.html' %}

{% block content %}
  <h1>Senha alterada</h1>
  <a href="{% url 'accounts:login' %}" role="button">Entrar</a>
{% endblock %}
```

O assunto e o corpo do e-mail são templates de texto. O assunto precisa ter uma linha só:

```
{# accounts/templates/accounts/password_reset_subject.txt #}
Redefinição de senha em {{ site_name }}
```

```
{# accounts/templates/accounts/password_reset_email.txt #}
Olá, {{ user.username }}.

Recebemos um pedido para redefinir a senha da conta {{ email }}.
Para criar uma nova senha, acesse:

{{ protocol }}://{{ domain }}{% url 'accounts:password_reset_confirm' uidb64=uid token=token %}

Se não foi você, ignore este e-mail.
```

(Os comentários `{# ... #}` acima são só para indicar o caminho; não os coloque no arquivo do assunto, que precisa ter uma única linha.) As variáveis `protocol`, `domain`, `site_name`, `uid`, `token`, `user` e `email` são enviadas pela própria `PasswordResetView`.

## Subindo tudo

```bash
docker compose up --build -d
docker compose ps
```

O `ps` deve mostrar o `db` como `healthy` e o `web` rodando. Agora as migrations e o superusuário:

```bash
docker compose exec web python manage.py makemigrations accounts
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

O `createsuperuser` pede **E-mail** (o `USERNAME_FIELD`), depois **Usuário** (o `REQUIRED_FIELDS`) e a senha. Para conferir a tabela criada:

```bash
docker compose exec db psql -U elliot -d fsociety -c '\d accounts_user'
```

Você verá as colunas do `AbstractUser` mais `email` (com `UNIQUE`), `avatar` e `email_verified`.

## O shell: criando o usuário e gerando o token de reset

```bash
docker compose exec web python manage.py shell
```

```python
>>> from django.contrib.auth import get_user_model
>>> from django.contrib.auth.tokens import default_token_generator
>>> from django.utils.encoding import force_bytes
>>> from django.utils.http import urlsafe_base64_encode
>>> User = get_user_model()
>>> user = User.objects.create_user(username='elliot', email='elliot@fsociety.org', password='hello-friend-2015')
>>> user
<User: elliot@fsociety.org>
>>> user.check_password('hello-friend-2015')
True
>>> user.check_password('errada')
False
>>> uid = urlsafe_base64_encode(force_bytes(user.pk))
>>> token = default_token_generator.make_token(user)
>>> f'/reset/{uid}/{token}/'
'/reset/MQ/dfvqn9-4dd47eb3fc53b071840635a83a26f247/'
>>> default_token_generator.check_token(user, token)
True
```

* `get_user_model()` devolve o model configurado em `AUTH_USER_MODEL`. Use sempre ele (ou `settings.AUTH_USER_MODEL` em FKs) em vez de importar `User` direto.
* `create_user` grava a senha com hash; `check_password` compara a senha informada com o hash.
* `make_token` e `urlsafe_base64_encode` montam exatamente o link que a `PasswordResetView` envia por e-mail. O seu token será diferente.

## Testando no navegador e nos logs

1. Acesse `http://localhost:8000/login/` e entre com o e-mail e a senha.
2. Saia, clique em "Esqueci minha senha" e informe o e-mail.
3. Veja o e-mail impresso no log e copie o link:

```bash
docker compose logs -f web
```

4. Abra o link, defina a nova senha e entre de novo.

No mesmo log aparece uma linha do gunicorn por requisição, por exemplo:

```
192.168.65.1 - - [03/Oct/2026:15:49:57 -0300] "GET /login/ HTTP/1.1" 200 1050 "-" "curl/8.7.1"
```

## Testes automatizados

```python
# accounts/tests.py
import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AccountsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='elliot', email='elliot@fsociety.org', password='hello-friend-2015'
        )

    def test_login_com_email(self):
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'elliot@fsociety.org', 'password': 'hello-friend-2015'},
        )
        self.assertRedirects(response, reverse('accounts:home'))

    def test_reset_de_senha(self):
        response = self.client.post(reverse('accounts:password_reset'), {'email': 'elliot@fsociety.org'})
        self.assertRedirects(response, reverse('accounts:password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)

        link = re.search(r'http://\S+', mail.outbox[0].body).group()
        response = self.client.get(link, follow=True)
        self.assertTrue(response.context['validlink'])

        response = self.client.post(
            response.redirect_chain[-1][0],
            {'new_password1': 'control-is-an-illusion', 'new_password2': 'control-is-an-illusion'},
        )
        self.assertRedirects(response, reverse('accounts:password_reset_complete'))

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('control-is-an-illusion'))
```

Nos testes, o Django troca o backend de e-mail por um em memória: tudo o que seria enviado fica em `mail.outbox`. O teste de reset pega o link do corpo do e-mail e o abre. A `PasswordResetConfirmView` guarda o token na sessão e redireciona para `reset/<uidb64>/set-password/` (para que o token não vaze pelo cabeçalho `Referer`); por isso usamos `follow=True` e postamos a nova senha na URL final.

```bash
docker compose exec web python manage.py test accounts
```

Para desligar tudo (o `-v` apaga também o volume do banco):

```bash
docker compose down -v
```

## Resumo

* Comece todo projeto Django com um `User` customizado, antes do primeiro `migrate`, mesmo que ele não tenha nenhum campo novo no início.
* Health check no banco e `condition: service_healthy` no `web` evitam o erro de conexão na subida.
* Login e reset de senha já vêm prontos no `django.contrib.auth`: herde as views e troque só template, formulário e destino.

Documentação:

* [Substituindo o model de usuário](https://docs.djangoproject.com/en/6.0/topics/auth/customizing/#substituting-a-custom-user-model)
* [Views de autenticação](https://docs.djangoproject.com/en/6.0/topics/auth/default/#all-authentication-views)
* [Ordem de inicialização no Docker Compose](https://docs.docker.com/compose/how-tos/startup-order/)

## Shorts da série Mr. Robot

* [O Elliot subiu o Django no Docker em 1 comando](https://youtube.com/shorts/gLL3iWZAD5Y) (21/09/2026)
* [Reset de senha estilo Mr. Robot, em Django](https://youtube.com/shorts/sMTdIeFqntA) (22/09/2026)
