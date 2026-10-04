# Novidades do Django 5.1

**Versões usadas no vídeo:** Django 5.1, Python 3.12, django-extensions 3.2.3, Faker 28.0.0 e Pico CSS 2.
{: .versoes }

<a href="https://youtu.be/zQdjRQA4y6s?si=jU6fqaven5fcud2u">
    <img src="../.gitbook/assets/youtube.png">
</a>

Doc: [https://docs.djangoproject.com/en/5.1/releases/5.1/](https://docs.djangoproject.com/en/5.1/releases/5.1/)

Github: [https://github.com/rg3915/django51](https://github.com/rg3915/django51)


**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`). Aqui elas já estão escritas do jeito certo, sem a barra.

![](../.gitbook/assets/tags.png)

O Django 5.1 foi lançado em 7 de agosto de 2024. Nesta dica vamos ver, num projeto pequeno, as novidades que mais chamam a atenção (não na ordem da documentação):

1. o **`LoginRequiredMiddleware`** e o decorator **`login_not_required`**: login obrigatório em todas as views por padrão;
2. o **logout via POST** com a `LogoutView` padrão do Django;
3. a template tag **`{% querystring %}`**, que mantém o filtro junto com a paginação;
4. o uso de **`__` (lookups) no `list_display`** do Admin.

## O projeto de exemplo

O código completo está no repositório [rg3915/django51](https://github.com/rg3915/django51). O projeto se chama `backend`, com duas apps dentro dele: `core` (páginas, `Category` e `Product`) e `crm` (`Person`). O CSS é o [Pico CSS](https://picocss.com/), carregado por CDN.

```bash
git clone https://github.com/rg3915/django51.git
cd django51

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python contrib/env_gen.py

python manage.py migrate
python manage.py createsuperuser --username="admin" --email=""
```

O `requirements.txt`:

```
Django==5.1
django-extensions==3.2.3
Faker==28.0.0
```

Se for montar do zero, a app `crm` foi criada dentro da pasta `backend`:

```bash
cd backend
python ../manage.py startapp crm
cd ..
```

Em `backend/crm/apps.py` deixe `name = 'backend.crm'` (e `name = 'backend.core'` na app `core`), e registre as apps em `settings.py`:

```python
# backend/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'backend.core',
    'backend.crm',
]
```

## Middleware de autenticação requerido por padrão

[https://docs.djangoproject.com/en/5.1/ref/middleware/#django.contrib.auth.middleware.LoginRequiredMiddleware](https://docs.djangoproject.com/en/5.1/ref/middleware/#django.contrib.auth.middleware.LoginRequiredMiddleware)

O novo **LoginRequiredMiddleware** redireciona todas as solicitações não autenticadas para uma página de login. As views podem permitir solicitações não autenticadas usando o novo decorator **login_not_required()**.

O **LoginRequiredMiddleware** respeita os valores de **login_url** e **redirect_field_name** definidos via o decorator **login_required()**, mas não suporta a definição de **login_url** ou **redirect_field_name** através do **LoginRequiredMixin**.

Ou seja, inverte a lógica: antes era preciso colocar `@login_required` em cada view que exigia login; agora, com o middleware, **todas** as views exigem login, e você marca com `@login_not_required` só as que podem ser abertas sem login.

Para habilitar isso, adicione `"django.contrib.auth.middleware.LoginRequiredMiddleware"` a sua configuração de **MIDDLEWARE**, depois do `AuthenticationMiddleware`. Defina também para onde ir depois do logout:

```python
# backend/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.LoginRequiredMiddleware',  # <---
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

...

LOGOUT_REDIRECT_URL = 'index'
```

Nas views, `index` e `about` ficam livres; `profile` não tem decorator nenhum, então exige login:

```python
# backend/core/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_not_required


@login_not_required
def index(request):
    return render(request, 'index.html')


@login_not_required
def about(request):
    return render(request, 'about.html')


def profile(request):
    return render(request, 'profile.html')
```

As urls usam a `LoginView` e a `LogoutView` do próprio Django. Como o `LOGIN_URL` padrão é `/accounts/login/`, a url de login fica nesse caminho:

```python
# backend/urls.py
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import admin
from django.urls import include, path

from backend.core import views as v


urlpatterns = [
    path('', v.index, name='index'),
    path('about/', v.about, name='about'),
    path('accounts/profile/', v.profile, name='profile'),
    path(
        'accounts/login/',
        LoginView.as_view(template_name='login.html'),
        name='login'
    ),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('person/', include('backend.crm.urls')),
    path('admin/', admin.site.urls),
]
```

Repare que a `LoginView` não precisa de `@login_not_required`: as views de autenticação do Django já vêm marcadas assim.

### Os templates

O `base.html` carrega o Pico CSS e um CSS para destacar a página atual da paginação:

```html
<!-- backend/core/templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
  <link rel="shortcut icon" href="https://www.djangoproject.com/favicon.ico">
  <title>Django 5.1</title>

  <!-- PicoCSS -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css" />

  <style>
    /* Custom CSS for the active pagination link in dark mode */
    .pagination .active {
      font-weight: bold;
      color: #121212;
      background-color: #1e88e5;
      border-radius: 0.25rem;
      padding: 0.5rem 1rem;
      text-decoration: none;
    }

    /* Style pagination links for dark mode */
    .pagination a {
      color: #e0e0e0;
      padding: 0.5rem 1rem;
      border-radius: 0.25rem;
      text-decoration: none;
    }

    .pagination a:hover {
      background-color: #333333;
    }
  </style>
</head>
<body class="container">
  <a href="{% url 'index' %}">Home</a>

  {% block content %}{% endblock content %}
</body>
</html>
```

```html
<!-- backend/core/templates/index.html -->
{% extends "base.html" %}

{% block content %}
  <header>
    <hgroup>
      <h1>
        <a href="https://docs.djangoproject.com/en/5.1/releases/5.1/" target="_blank">Django 5.1</a>
      </h1>
    </hgroup>
  </header>

  <ul>
    <li>
      <a href="{% url 'about' %}">About</a>
    </li>
    <li>
      <a href="{% url 'profile' %}">Profile</a>
    </li>
    <li>
      <a href="{% url 'person_list' %}">Persons</a>
    </li>
  </ul>
{% endblock content %}
```

```html
<!-- backend/core/templates/about.html -->
{% extends "base.html" %}

{% block content %}
  <header>
    <hgroup>
      <h1>About</h1>
    </hgroup>
  </header>
{% endblock content %}
```

```html
<!-- backend/core/templates/login.html -->
{% extends "base.html" %}

{% block content %}
  <header>
    <hgroup>
      <h1>Login</h1>
    </hgroup>
  </header>

  <form action="." method="POST">
    {% csrf_token %}

    <input id="id_username" name="username" class="form-control" type="text" autofocus />
    <input id="id_password" name="password" class="form-control" type="password" />
    <button type="submit">Salvar</button>
  </form>
{% endblock content %}
```

### Testando

Rode `python manage.py runserver` e abra `http://localhost:8000/`. Clicando em **About** a página abre sem login. Clicando em **Profile** você é redirecionado para `/accounts/login/?next=/accounts/profile/`; depois de entrar, cai na página de profile. O mesmo acontece com **Persons**, que também exige login.

## Logout via POST

Desde o Django 5.0 a `LogoutView` não aceita mais `GET`, só `POST` (um `GET` em `/logout/` devolve **405 Method Not Allowed**). Por isso o botão **Sair** da página de profile é um formulário com `method="POST"` e `{% csrf_token %}`:

```html
<!-- backend/core/templates/profile.html -->
{% extends "base.html" %}

{% block content %}
  <header>
    <hgroup>
      <h1>Profile</h1>
    </hgroup>
  </header>

  <form action="{% url 'logout' %}" method="POST">
    {% csrf_token %}
    <button type="submit">Sair</button>
  </form>
{% endblock content %}
```

Ao clicar em **Sair**, o usuário é deslogado e redirecionado para `index` (por causa do `LOGOUT_REDIRECT_URL`).

## `{% querystring %}` template tag

A nova tag `{% querystring %}` monta a query string da url **mantendo os parâmetros que já estão em `request.GET`** e trocando só os que você passar. O foco dela não é a paginação, é o filtro: ela faz a paginação respeitar a busca.

### Os dados

A app `crm` tem um model `Person`:

```python
# backend/crm/models.py
from django.db import models


class Person(models.Model):
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
```

```python
# backend/crm/admin.py
from django.contrib import admin

from .models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email')
    search_fields = ('first_name', 'last_name', 'email')
```

Para ter dados, vamos criar um comando com o `django-extensions`:

```bash
python manage.py create_command core -n create_data
```

```python
# backend/core/management/commands/create_data.py
from django.core.management.base import BaseCommand
from backend.crm.models import Person
from backend.utils import utils as u
from backend.utils.progress_bar import progressbar


def get_person():
    first_name = u.gen_first_name()
    last_name = u.gen_last_name()
    email = u.gen_email(first_name, last_name)
    d = dict(
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    return d


def create_persons():
    aux = []
    for _ in progressbar(range(500), 'Persons'):
        data = get_person()
        obj = Person(**data)
        aux.append(obj)
    Person.objects.bulk_create(aux)


class Command(BaseCommand):
    help = 'Create data.'

    def handle(self, *args, **options):
        self.stdout.write('Create data.')
        create_persons()
```

As funções auxiliares usam o Faker:

```python
# backend/utils/utils.py (trecho)
from django.utils.text import slugify
from faker import Faker

fake = Faker()


def gen_first_name():
    return fake.first_name()


def gen_last_name():
    return fake.last_name()


def gen_email(first_name: str, last_name: str, company: str = None):
    first_name = slugify(first_name)
    last_name = slugify(last_name)
    email = f'{first_name}.{last_name}@email.com'
    return email
```

```python
# backend/utils/progress_bar.py
import sys


def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)

    def show(j):
        x = int(size * j / count)
        file.write("%s[%s%s] %i/%i\r" %
                   (prefix, "#" * x, "." * (size - x), j, count))
        file.flush()
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i + 1)
    file.write("\n")
    file.flush()
```

(Crie também um `backend/utils/__init__.py` vazio.) Rode:

```bash
python manage.py create_data
```

Isso cria 500 pessoas.

### A view com busca e paginação

```python
# backend/crm/views.py
from django.db.models import Q
from django.views.generic import ListView

from .models import Person


class PersonListView(ListView):
    model = Person
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['page'] = self.request.GET.get('page', 1)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        search = self.request.GET.get('search')

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        return queryset
```

* `paginate_by = 10` faz a `ListView` paginar e colocar `page_obj` no contexto;
* em `get_context_data` pegamos `page`, que vem de `request.GET`, com `1` como padrão;
* em `get_queryset` aplicamos o filtro `search` (vindo do formulário) no nome, sobrenome e e-mail.

```python
# backend/crm/urls.py
from django.urls import path
from backend.crm import views as v


urlpatterns = [
    path('', v.PersonListView.as_view(), name='person_list'),
]
```

O template tem um formulário com `method="GET"` e um campo `search`:

```html
<!-- backend/crm/templates/crm/person_list.html -->
{% extends "base.html" %}

{% block content %}
<div>
  <div>
    <div>
      <h1>Lista de Pessoas</h1>
    </div>
    <div>
      <form action="." method="GET">
          <input id="id_search" name="search" type="search" placeholder="Buscar..." />
          <button type="submit">Buscar</button>
        <div>
          <a href=".">Limpar</a>
        </div>
      </form>
    </div>
  </div>
  <table>
    <thead>
      <tr>
        <th>Nome</th>
        <th>E-mail</th>
      </tr>
    </thead>
    <tbody>
      {% for object in object_list %}
      <tr>
        <td>{{ object.full_name }}</td>
        <td>{{ object.email|default:'---' }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>

{% include "includes/pagination.html" %}

{% endblock content %}
```

### A paginação com `{% querystring %}`

Antes, para não perder o filtro ao trocar de página, era preciso remontar a query string na mão:

```html
<a href="?{% if request.GET.search %}search={{ request.GET.search }}{% endif %}&page={{ pg }}">
```

A própria documentação do Django mostra um exemplo ainda mais trabalhoso, com um `for` em `request.GET.iterlists`. Com o Django 5.1 basta:

```html
<a href="{% querystring page=page_obj.next_page_number %}">Next page</a>
```

A paginação completa fica num componente separado:

```html
<!-- backend/core/templates/includes/pagination.html -->
<nav aria-label="Pagination">
  <ul class="pagination">
    {% if page_obj.has_previous %}
      <li><a href="{% querystring page=1 %}">&laquo;</a></li>
      <li><a href="{% querystring page=page_obj.previous_page_number %}">&lsaquo;</a></li>
    {% endif %}

    {% for pg in page_obj.paginator.page_range %}
      {% if pg <= 3 or pg >= page_obj.paginator.num_pages|add:'-2' %}
        <li class="{% if page_obj.number == pg %}active{% endif %}">
          <a href="{% querystring page=pg %}">{{ pg }}</a>
        </li>
      {% elif pg >= page_obj.number|add:'-3' and pg <= page_obj.number|add:'3' %}
        <li class="{% if page_obj.number == pg %}active{% endif %}">
          <a href="{% querystring page=pg %}">{{ pg }}</a>
        </li>
      {% elif pg == page_obj.number|add:'-4' or pg == page_obj.number|add:'4' %}
        <li><a href="#">...</a></li>
      {% endif %}
    {% endfor %}

    {% if page_obj.has_next %}
      <li><a href="{% querystring page=page_obj.next_page_number %}">&rsaquo;</a></li>
      <li><a href="{% querystring page=page_obj.paginator.num_pages %}">&raquo;</a></li>
    {% endif %}
  </ul>
</nav>

<p>{{ request.GET }}</p>
<p>{{ page }} é a página definida pela variável page.</p>
<p>{{ page.next_page_number }} page.next_page_number não existe.</p>
<p>{{ page_obj }} page_obj existe.</p>

<nav aria-label="Pagination">
  <ul>
    {% if page_obj.has_previous %}
      <li>
        <a href="{% querystring page=page|add:-1 %}">Previous page is {{ page|add:-1 }}</a>
      </li>
    {% endif %}

    Current page is {{ page_obj.number }}

    {% if page_obj.has_next %}
      <li>
        <a href="{% querystring page=page|add:1 %}">Next page is {{ page|add:1 }}</a>
      </li>
    {% endif %}
  </ul>
</nav>
```

A primeira `<nav>` é a paginação de verdade: primeira página, anterior, as três primeiras e as três últimas, as páginas próximas da atual, reticências, próxima e última. Todos os links usam `{% querystring page=... %}`.

O trecho de baixo é só para estudo. Ele mostra o `request.GET`, a variável `page` (que nós colocamos no contexto, e que é só um número, por isso `page.next_page_number` não existe) e o `page_obj` (o objeto de página da `ListView`). E mostra que também dá para usar a variável `page` com o filtro `add`:

```html
<a href="{% querystring page=page|add:-1 %}">Previous page is {{ page|add:-1 }}</a>

<a href="{% querystring page=page|add:1 %}">Next page is {{ page|add:1 }}</a>
```

### Testando

Entre em **Persons**, digite `al` na busca e clique em **Buscar**. A url fica

```
http://localhost:8000/person/?search=al
```

Clicando na página 2, a url vira

```
http://localhost:8000/person/?search=al&page=2
```

Ou seja, o `{% querystring %}` manteve o filtro `search=al` e só acrescentou (ou trocou) o `page`. Na tela, o `{{ request.GET }}` mostra `<QueryDict: {'search': ['al'], 'page': ['2']}>`.

## Minor features

### django.contrib.admin

* `ModelAdmin.list_display` agora suporta o uso de `__` para "list fields" de modelos relacionados, ou FK.

Na app `core` temos `Category` (com `title` e `type`) e `Product`, com uma FK para `Category`:

```python
# backend/core/models.py
from django.db import models


class Category(models.Model):
    title = models.CharField('título', max_length=100, unique=True)
    type = models.CharField('tipo', max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return f'{self.title}'


class Product(models.Model):
    title = models.CharField('título', max_length=100, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='categoria',
        related_name='categories',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        return f'{self.title}'
```

Agora dá para colocar `category__title` e `category__type` direto no `list_display`:

```python
# backend/core/admin.py
from django.contrib import admin

from .models import Category, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'category__title', 'category__type')
    search_fields = ('title', 'category__title')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'type')
```

Antes gerava o seguinte erro:

```
File "~/.venv/lib/python3.12/site-packages/django/core/management/base.py", line 563, in check
    raise SystemCheckError(msg)
django.core.management.base.SystemCheckError: SystemCheckError: System check identified some issues:

ERRORS:
<class 'backend.core.admin.ProductAdmin'>: (admin.E108) The value of 'list_display[1]' refers to 'category__title', which is not a callable, an attribute of 'ProductAdmin', or an attribute or method on 'core.Product'.
```

A saída era criar um método no `ModelAdmin` que devolvesse o valor do campo relacionado, usando o decorator `@admin.display` (adicionado no Django 3.2), como vimos na [Dica 39 - Django Admin: display decorator (Django 3.2+)](039-django-admin-display-decorator-django-32.md).

Mas agora foi corrigido: no Admin de produtos aparecem as colunas **Category title** e **Category type** sem erro nenhum.

## Conclusão

O Django 5.1 traz o login obrigatório por padrão com `LoginRequiredMiddleware` e `@login_not_required`, a tag `{% querystring %}` que acaba com a montagem manual de query strings na paginação, e lookups com `__` no `list_display`. Junto com o logout via POST (que vem do Django 5.0), são mudanças pequenas que simplificam bastante o código do dia a dia. A lista completa está nas [notas de lançamento do Django 5.1](https://docs.djangoproject.com/en/5.1/releases/5.1/).
