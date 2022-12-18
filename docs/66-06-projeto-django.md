# Dica 6 - Criando o projeto Django

VIDEO EM BREVE.

**Importante:** remova a `\` no meio das tags.

![](../.gitbook/assets/tags.png)


```
python -m venv .venv
source .venv/bin/activate

# .venv\Scripts\activate  # Windows

pip install django python-decouple django-extensions
pip freeze | grep -E 'Django|python-decouple|django-extensions' >> requirements.txt
```

Senão digite apenas `pip freeze` e copie os pacotes manualmente.

## Criando o projeto

```
django-admin startproject backend .
```

## Criando a app core

```
cd backend
python ../manage.py startapp core
cd ..
tree backend
```

## Editando settings.py

Rode o comando

```
python contrib/env_gen.py

cat .env
```

Edite `.env`

Edite `.gitignore`

```

.DS_Store

media/
staticfiles/
.idea
.ipynb_checkpoints/
.vscode
*.cast
```

Edite `settings.py`

```python
# settings.py

from pathlib import Path

from decouple import config, Csv


BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())

INSTALLED_APPS = [
    ...
    # apps de terceiros
    'django_extensions',
    # minhas apps
    'backend.core',
]

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_THOUSAND_SEPARATOR = True

DECIMAL_SEPARATOR = ','

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR.joinpath('staticfiles')
```

Edite `backend/urls.py`

```python
# backend/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('backend.core.urls', namespace='core')),  # noqa E501
    path('admin/', admin.site.urls),  # noqa E501
]
```

Edite `core/apps.py`

```python
# core/apps.py
from django.apps import AppConfig


class CoreConfig(AppConfig):
    ...
    name = 'backend.core'
```

## Criando a estrutura de templates

Vamos trabalhar com herança de templates.

```
mkdir -p backend/core/templates/includes
touch backend/core/templates/base.html
touch backend/core/templates/index.html
touch backend/core/templates/includes/menu.html
touch backend/core/templates/includes/footer.html
touch backend/core/templates/includes/pagination.html

# ou

# touch backend/core/templates/includes/{menu,footer,pagination}.html
```

Edite `base.html`

```html
<!-- base.html -->
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

  <link rel="stylesheet" href="{\% static 'css/style.css' %}">

</head>
<body class="flex flex-col min-h-screen">
  {\% include "includes/menu.html" %}

  <main class="flex-auto">
    {\% block content %}{\% endblock content %}
  </main>

  {\% include "includes/footer.html" %}

  <script src="{\% static 'js/main.js' %}"></script>
</body>
</html>
```
Edite `index.html`

```html
<!-- index.html -->
{\% extends "base.html" %}

{\% block content %}
  <h1 class="text-2xl font-bold">Conteúdo</h1>
  <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Vero tenetur repudiandae id animi, labore magni cumque tempore eum culpa esse exercitationem modi est enim sunt in maxime aut quo deleniti!</p>
{\% endblock content %}
```
Edite `menu.html`

```html
<!-- menu.html -->
<header class="menu h-16 bg-slate-800 flex justify-center items-center">
  <h1 class="text-2xl font-bold">Menu</h1>
</header>
```

Edite `footer.html`

```html
<!-- footer.html -->
<footer class="h-16 bg-slate-800 text-gray-100 flex justify-between items-center px-4 text-lg">
  <h1>Dicas de Django © 2023</h1>
  <h1>by Regis do Python</h1>
</footer>
```
Edite `pagination.html`

```html
<!-- pagination.html -->
```

## Criando os arquivos estáticos

```
mkdir -p backend/core/static/{css,js}
touch backend/core/static/css/style.css
touch backend/core/static/js/main.js
```

Edite `style.css`

```css
.menu {
    color: yellow;
}
```
Edite `main.js`

```js
// main.js
console.log('Teste')
```

## Rodando migrate

```
python manage.py migrate
```

## Rodando o projeto

```
python manage.py runserver
```

## Renderizando a página

Edite `core/views.py`

```python
# core/views.py
from django.shortcuts import render


def index(request):
    template_name = 'index.html'
    return render(request, template_name)
```

Edite `core/urls.py`

```python
# core/urls.py
from django.urls import path
from backend.core import views as v


app_name = 'core'


urlpatterns = [
    path('', v.index, name='index'),  # noqa E501
]
```

