# Dica 06 - Criando o projeto Django

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, python-decouple 3.6, django-extensions 3.2.1 e Tailwind CSS (via CDN).
{: .versoes }

<a href="https://youtu.be/9U9MLXFqjlk">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`). Se copiar código de lá, remova a `\`.

![](../.gitbook/assets/tags.png)

Esta é a dica que (re)começa o projeto **Dicas de Django** do zero. Nas dicas 01 a 05 trabalhamos só com o front-end (HTML puro, Bulma, Tailwind e htmx); agora vamos criar o projeto Django que será usado em todas as próximas dicas da série, já com o Tailwind CSS como framework CSS.

Ao final teremos:

* um projeto chamado `backend`, com a app `core` **dentro** da pasta do projeto (`backend/core`);
* as configurações sensíveis lidas de um arquivo `.env` com o `python-decouple`;
* uma estrutura de templates com herança (`base.html`, `index.html` e a pasta `includes`);
* arquivos estáticos (CSS e JS) da app;
* uma view renderizando a página inicial.

Código da aula: [https://github.com/rg3915/dicas-de-django/tree/aula06](https://github.com/rg3915/dicas-de-django/tree/aula06)

## Pré-requisitos

* Python 3.10 (o do vídeo).
* git.
* O repositório do projeto Dicas de Django clonado (ou uma pasta vazia, se for começar sozinho).

No vídeo, cada aula é uma branch nova. A issue da aula é criada com o script da [Dica 01](061-01-criando-issues-com-api-github.md) e em seguida vem a branch:

```bash
python cli/create_issue.py \
--title='Criando o projeto Django' \
--body='g ch -b aula06' \
--labels='backend,feature'

git checkout -b aula06
```

## Ambiente virtual e dependências

```bash
python -m venv .venv
source .venv/bin/activate

# .venv\Scripts\activate  # Windows

pip install django python-decouple django-extensions
```

Saída no vídeo:

```
Collecting django
  Using cached Django-4.1.3-py3-none-any.whl (8.1 MB)
Requirement already satisfied: python-decouple in ./.venv/lib/python3.10/site-packages (3.6)
Collecting django-extensions
  Using cached django_extensions-3.2.1-py3-none-any.whl (229 kB)
...
Successfully installed asgiref-3.5.2 django-4.1.3 django-extensions-3.2.1 sqlparse-0.4.3
```

* `django`: o framework.
* `python-decouple`: lê as variáveis de ambiente do arquivo `.env`, para não deixar senha e `SECRET_KEY` no código.
* `django-extensions`: uma coleção de comandos extras para o `manage.py` (`shell_plus`, `show_urls`, `runserver_plus` etc.).

Acrescente os pacotes ao `requirements.txt`:

```bash
pip freeze | grep -E 'Django|python-decouple|django-extensions' >> requirements.txt
```

Senão, digite apenas `pip freeze` e copie os pacotes manualmente. O `requirements.txt` do vídeo ficou assim (o `click` e o `requests` vieram das dicas anteriores):

```
# requirements.txt
click==8.1.3
python-decouple==3.6
requests==2.28.1
Django==4.1.3
django-extensions==3.2.1
```

## Criando o projeto

```bash
django-admin startproject backend .
```

O ponto no final cria o `manage.py` na pasta atual (a raiz do repositório), e não numa pasta `backend/backend`:

```
.
├── backend
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

## Criando a app core

Eu gosto de manter as apps organizadas **dentro** da pasta do projeto. Para isso, entre em `backend` e rode o `startapp` chamando o `manage.py` que está um nível acima:

```bash
cd backend
python ../manage.py startapp core
cd ..
tree backend
```

```
backend/
├── asgi.py
├── core
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── __init__.py
├── settings.py
├── urls.py
└── wsgi.py
```

Como a app está dentro de `backend`, o caminho Python dela é `backend.core`, e isso vai aparecer no `settings.py`, no `apps.py` e nas urls.

## Gerando o .env

O repositório tem um script, `contrib/env_gen.py`, que gera o arquivo `.env` com uma `SECRET_KEY` aleatória:

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
#POSTGRES_DB=
#POSTGRES_USER=
#POSTGRES_PASSWORD=%s
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

Rode o comando:

```bash
python contrib/env_gen.py

cat .env
```

```
DEBUG=True
SECRET_KEY=dUw5bk0KxrHeyAZcP^u79o+BS4fp(v6CqRM...
ALLOWED_HOSTS=127.0.0.1,.localhost,0.0.0.0

#DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
#POSTGRES_DB=
#POSTGRES_USER=
#POSTGRES_PASSWORD=...
#DB_HOST=localhost

#DEFAULT_FROM_EMAIL=
...
```

A `SECRET_KEY` muda a cada execução. As linhas comentadas serão usadas na [Dica 07](067-07-docker-compose.md) (PostgreSQL e e-mail).

## Editando o .gitignore

O `.gitignore` é o padrão do Python (o modelo do GitHub, com `__pycache__/`, `.venv`, `.env`, `db.sqlite3` etc.). No final dele acrescente:

```
.DS_Store

media/
staticfiles/
.idea
.ipynb_checkpoints/
.vscode
*.cast
```

A pasta `media/` (arquivos enviados pelos usuários) e a `staticfiles/` (gerada pelo `collectstatic`) não devem ir para o repositório.

## Editando settings.py

Os trechos principais do `settings.py`, já com as alterações (o arquivo completo está no link logo abaixo):

```python
# backend/settings.py
from pathlib import Path

from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

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
    # apps de terceiros
    'django_extensions',
    # minhas apps
    'backend.core',
]

# ... (veja o arquivo completo no GitHub)

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True

DECIMAL_SEPARATOR = ','


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR.joinpath('staticfiles')

# ... (veja o arquivo completo no GitHub)
```

Código completo: [backend/settings.py](https://github.com/rg3915/dicas-de-django/blob/18f3c2dbd32e93b05b025c193a3ce61a5e21cdd9/backend/settings.py)

O que mudou em relação ao arquivo gerado pelo `startproject`:

* `from decouple import config, Csv`: o `config` lê uma variável do `.env` (ou do ambiente); o `Csv` transforma `127.0.0.1,.localhost,0.0.0.0` numa lista.
* `SECRET_KEY`, `DEBUG` e `ALLOWED_HOSTS` agora vêm do `.env`. O `cast=bool` converte o texto `True` em booleano; sem `.env`, o `DEBUG` é `False`.
* Em `INSTALLED_APPS`, separamos as **apps de terceiros** (`django_extensions`) das **minhas apps** (`backend.core`, com o caminho completo, porque a app está dentro de `backend`).
* Idioma e fuso horário do Brasil (`pt-br` e `America/Sao_Paulo`).
* `USE_THOUSAND_SEPARATOR = True` e `DECIMAL_SEPARATOR = ','`: números exibidos como `1.234,56`.
* `STATIC_ROOT`: a pasta `staticfiles`, onde o `collectstatic` junta os estáticos (vamos precisar dela no Docker, na próxima dica).

## Editando core/apps.py

Como a app está dentro de `backend`, o `name` também precisa do caminho completo:

```python
# backend/core/apps.py
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.core'
```

## Editando backend/urls.py

```python
# backend/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('backend.core.urls', namespace='core')),  # noqa E501
    path('admin/', admin.site.urls),  # noqa E501
]
```

O `include` manda a raiz do site para as urls da app `core`, com o namespace `core` (assim, nos templates, a url fica `{% url 'core:index' %}`). O `# noqa E501` evita o aviso de linha longa do flake8: eu prefiro não quebrar a linha nas urls.

## Criando a estrutura de templates

Vamos trabalhar com herança de templates: o `base.html` tem o esqueleto da página, e as outras páginas só preenchem o `block content`. Menu, rodapé e paginação ficam em arquivos separados, na pasta `includes`.

```bash
mkdir -p backend/core/templates/includes
touch backend/core/templates/base.html
touch backend/core/templates/index.html
touch backend/core/templates/includes/menu.html
touch backend/core/templates/includes/footer.html
touch backend/core/templates/includes/pagination.html

# ou

# touch backend/core/templates/includes/{menu,footer,pagination}.html
```

```
backend/core/templates/
├── base.html
├── includes
│   ├── footer.html
│   ├── menu.html
│   └── pagination.html
└── index.html
```

Edite `base.html`

```html
<!-- backend/core/templates/base.html -->
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
  <link rel="shortcut icon" href="https://www.djangoproject.com/favicon.ico">
  <title>Django</title>

  <!-- TailwindCSS -->
  <script src="https://cdn.tailwindcss.com"></script>

  <link rel="stylesheet" href="{% static 'css/style.css' %}">

</head>
<body class="flex flex-col min-h-screen">
  {% include "includes/menu.html" %}

  <main class="flex-auto">
    {% block content %}{% endblock content %}
  </main>

  {% include "includes/footer.html" %}

  <script src="{% static 'js/main.js' %}"></script>
</body>
</html>
```

* `{% load static %}` carrega a tag `static`, que monta o caminho dos arquivos estáticos (`/static/css/style.css`). No vídeo eu esqueci essa linha no começo, e o erro aparece mais adiante.
* O Tailwind CSS vem do CDN (`cdn.tailwindcss.com`), sem instalar nada.
* `{% include "includes/menu.html" %}` insere o conteúdo de outro template.
* `{% block content %}{% endblock content %}` é vazio no `base.html`; quem estende o `base.html` preenche esse bloco.
* As classes `flex flex-col min-h-screen` no `body` e `flex-auto` no `main` mantêm o rodapé no fim da tela.

Edite `index.html`

```html
<!-- backend/core/templates/index.html -->
{% extends "base.html" %}

{% block content %}
  <h1 class="text-2xl font-bold">Conteúdo</h1>
  <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Vero tenetur repudiandae id animi, labore magni cumque tempore eum culpa esse exercitationem modi est enim sunt in maxime aut quo deleniti!</p>
{% endblock content %}
```

Edite `menu.html`

```html
<!-- backend/core/templates/includes/menu.html -->
<header class="menu h-16 bg-slate-800 flex justify-center items-center">
  <h1 class="text-2xl font-bold">Menu</h1>
</header>
```

Edite `footer.html`

```html
<!-- backend/core/templates/includes/footer.html -->
<footer class="h-16 bg-slate-800 text-gray-100 flex justify-between items-center px-4 text-lg">
  <h1>Dicas de Django © 2023</h1>
  <h1>by Regis do Python</h1>
</footer>
```

Edite `pagination.html`. Por enquanto ele fica só com o comentário; a paginação vem numa dica futura.

```html
<!-- backend/core/templates/includes/pagination.html -->
```

## Criando os arquivos estáticos

```bash
mkdir -p backend/core/static/{css,js}
touch backend/core/static/css/style.css
touch backend/core/static/js/main.js
```

Os dois já estão referenciados no `base.html`. Vamos colocar só um conteúdo de teste, para ver se estão sendo carregados.

Edite `style.css`

```css
/* backend/core/static/css/style.css */
.menu {
    color: yellow;
}
```

Edite `main.js`

```js
// backend/core/static/js/main.js
console.log('Teste')
```

## Renderizando a página

Edite `core/views.py`

```python
# backend/core/views.py
from django.shortcuts import render


def index(request):
    template_name = 'index.html'
    return render(request, template_name)
```

Crie `core/urls.py`

```python
# backend/core/urls.py
from django.urls import path
from backend.core import views as v


app_name = 'core'


urlpatterns = [
    path('', v.index, name='index'),  # noqa E501
]
```

O `app_name = 'core'` é obrigatório porque usamos `namespace='core'` no `include` do `backend/urls.py`.

A estrutura final da app fica:

```
backend/core/
├── admin.py
├── apps.py
├── __init__.py
├── migrations
│   └── __init__.py
├── models.py
├── static
│   ├── css
│   │   └── style.css
│   └── js
│       └── main.js
├── templates
│   ├── base.html
│   ├── includes
│   │   ├── footer.html
│   │   ├── menu.html
│   │   └── pagination.html
│   └── index.html
├── tests.py
├── urls.py
└── views.py
```

## Rodando migrate

```bash
python manage.py migrate
```

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK
```

## Rodando o projeto

```bash
python manage.py runserver
```

Acesse [http://localhost:8000](http://localhost:8000). Aparece o menu no topo (com o texto amarelo, vindo do `style.css`), o conteúdo no meio e o rodapé embaixo. No console do navegador aparece `Teste`, vindo do `main.js`.

## Erros que apareceram no caminho

No vídeo eu fui rodando o projeto enquanto montava os arquivos, e alguns erros apareceram. Uma dica: leia o traceback **de baixo para cima**; a última linha diz o problema.

**`NameError: name 'Csv' is not defined`**

```
  File ".../backend/settings.py", line 25, in <module>
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())
NameError: name 'Csv' is not defined
```

Faltou importar o `Csv`: `from decouple import config, Csv`.

**`ModuleNotFoundError: No module named 'backend.core.urls'`**

O `backend/urls.py` faz `include('backend.core.urls')`, mas o arquivo `backend/core/urls.py` ainda não existia. Crie o arquivo.

**`ImproperlyConfigured: Specifying a namespace in include() without providing an app_name`**

```
django.core.exceptions.ImproperlyConfigured: Specifying a namespace in include() without providing an app_name is not supported. Set the app_name attribute in the included module, or pass a 2-tuple containing the list of patterns and app_name instead.
```

O `include` tem `namespace='core'`, mas o `backend/core/urls.py` estava sem `app_name`. Acrescente `app_name = 'core'`. Enquanto a view `index` não existia, eu deixei a linha `path('', v.index, ...)` comentada, com o `urlpatterns` vazio; aí o Django mostra a página padrão "A instalação foi com sucesso! Parabéns!".

**`TemplateSyntaxError: Invalid block tag on line 14: 'static'. Did you forget to register or load this tag?`**

O `base.html` usava `{% static ... %}` sem `{% load static %}` no topo. Acrescente a linha e dê F5.

## Conclusão

Temos o projeto `backend` com a app `core` dentro dele, configurações no `.env`, herança de templates com Tailwind e arquivos estáticos funcionando. Este é o ponto de partida das próximas dicas: na [Dica 07](067-07-docker-compose.md) vamos colocar PostgreSQL, pgAdmin e MailHog com docker-compose.
