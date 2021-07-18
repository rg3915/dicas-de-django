# Dicas de Django

Várias dicas de Django - assuntos diversos.

0. [Django boilerplate e cookiecutter-django](#1---django-boilerplate-e-cookiecutter-django)
1. [Novo Django boilerplate](#11---django-boilerplate)
2. [Django extensions](#2---django-extensions)
3. [Django bulk_create e django-autoslug](#3---django-bulk_create-e-django-autoslug)
4. [Django Admin personalizado](#4---django-admin-personalizado)
5. [Django Admin Date Range filter](#5---django-admin-date-range-filter)
6. [Geradores de senhas randômicas - uuid, hashids, secrets](#6---geradores-de-senhas-rand%C3%B4micas---uuid-hashids-secrets)
7. [Rodando o ORM do Django no Jupyter Notebook](#7---rodando-o-orm-do-django-no-jupyter-notebook)
8. [Conhecendo o Django Debug Toolbar](#8---conhecendo-o-django-debug-toolbar)
9. [Escondendo suas senhas python-decouple](#9---escondendo-suas-senhas-python-decouple)
10. [Prototipagem de web design (Mockup)](#10---prototipagem-de-web-design-mockup)
11. [Bootstrap e Bulma + Colorlib](#11---bootstrap-e-bulma--colorlib)
12. [Imagens: pexels e unsplash](#12---imagens-pexels-e-unsplash)
13. [Cores](#13---cores)
14. [Herança de Templates e Arquivos estáticos](#14---herança-de-templates-e-arquivos-estáticos)
15. [Busca por data no frontend](#15---busca-por-data-no-frontend)
16. [Filtros com django-filter](#16---filtros-com-django-filter)
17. [Criando comandos personalizados](#17---criando-comandos-personalizados)
18. [bulk_create e bulk_update](#18---bulk_create-e-bulk_update)
19. [Criando Issues por linha de comando com a api do github](#19---criando-issues-por-linha-de-comando-com-a-api-do-github)
20. [api github e click](#20---api-github-e-click)
21. [Criando issues por linha de comando com gitlab cli](#21---criando-issues-por-linha-de-comando-com-gitlab-cli)
22. [Criando issues por linha de comando com bitbucket cli](#22---criando-issues-por-linha-de-comando-com-bitbucket-cli)
23. [Diferença entre JSON dump, dumps, load e loads](#23---diferença-entre-json-dump-dumps-load-e-loads)
24. [Barra de progresso](#24---barra-de-progresso)
25. [Rodando Shell script dentro do Python](#25---rodando-shell-script-dentro-do-python)
26. [Rodando Python dentro do Shell script](#26---rodando-python-dentro-do-shell-script)
27. [Retornando os nomes dos campos do model](#27---retornando-os-nomes-dos-campos-do-model)
28. [Admin: Usando short description](#28---admin-usando-short-description)
29. [Django Admin: Criando actions no Admin](#29---django-admin-criando-actions-no-admin)
30. [Django Admin: Editando direto na listview do Admin](#30---django-admin-editando-direto-na-listview-do-admin)
31. [Django Admin: Pegando usuário logado no Admin](#31---django-admin-pegando-usuário-logado-no-admin)
32. [Django Admin: Sobreescrevendo os templates do Admin](#32---django-admin-sobreescrevendo-os-templates-do-admin)
33. [Github cli](#33---github-cli)
34. [Django: custom template tags](#34---django-custom-template-tags)
35. [Django: passando usuário logado no formulário](#35---django-passando-usuário-logado-no-formulário)
36. [Django: visualizando seus modelos com graph models](#36---django-visualizando-seus-modelos-com-graph-models)
37. [Faker](#37---faker)
38. [Django: Paginação + Filtros](#38---django-paginação--filtros)
39. [Django Admin: display decorator (Django 3.2+)](#39---django-admin-display-decorator-django-32)
40. [Formulários: date, datetime, duration e templatetags de data](#40---formulários-date-datetime-duration-e-templatetags-de-data)

## This project was done with:

* Python 3.8.2
* Django 2.2.20

## How to run project?

* Clone this repository.
* Create virtualenv with Python 3.
* Active the virtualenv.
* Install dependences.
* Run the migrations.

```
git clone https://github.com/rg3915/dicas-de-django.git
cd dicas-de-django
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python contrib/env_gen.py
python manage.py migrate
```

## Este projeto foi feito com:

* Python 3.8.2
* Django 2.2.20

## Como rodar o projeto?

* Clone esse repositório.
* Crie um virtualenv com Python 3.
* Ative o virtualenv.
* Instale as dependências.
* Rode as migrações.

```
git clone https://github.com/rg3915/dicas-de-django.git
cd dicas-de-django
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python contrib/env_gen.py
python manage.py migrate
```

# 1 - Django boilerplate e cookiecutter-django

<a href="https://youtu.be/OYcOpcPcp8Y">
    <img src="img/youtube.png">
</a>

[boilerplatesimple.sh](https://gist.github.com/rg3915/b363f5c4a998f42901705b23ccf4b8e8)

[boilerplate2.sh](https://gist.github.com/rg3915/a264d0ade860d2f2b4bf)

[cookiecutter-django](https://github.com/pydanny/cookiecutter-django)

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

# 1.1 - Django boilerplate

<a href="https://youtu.be/eLKjL61HEbQ">
    <img src="img/youtube.png">
</a>

Novo boilerplate com Django 3.1.8

https://github.com/rg3915/django-boilerplate

# 2 - Django extensions



https://django-extensions.readthedocs.io/en/latest/index.html

```
pip install django-extensions
```

```python
# settings.py
INSTALLED_APPS = (
    ...
    'django_extensions',
)
```

```
python manage.py show_urls
```

```
python manage.py shell_plus
```


# 3 - Django bulk_create e django-autoslug

<a href="https://youtu.be/Py-AG6S_vJI">
    <img src="img/youtube.png">
</a>

### python-slugify

https://pypi.org/project/python-slugify/

```python
from slugify import slugify

text = 'Dicas de Django'
print(slugify(text))
url = f'example.com/{slugify(text)}'
```

#### bulk-create

https://docs.djangoproject.com/en/3.0/ref/models/querysets/#bulk-create


#### django-autoslug

https://pypi.org/project/django-autoslug/

```
pip install django-autoslug
```


#### models.py

```python
from autoslug import AutoSlugField
from django.db import models


class Article(models.Model):
    title = models.CharField('título', max_length=200)
    subtitle = models.CharField('sub-título', max_length=200)
    slug = AutoSlugField(populate_from='title')
    category = models.ForeignKey(
        'Category',
        related_name='categories',
        verbose_name='categoria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    published_date = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'artigo'
        verbose_name_plural = 'artigos'

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField('título', max_length=50, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.title
```


#### shell_plus

```python
categories = [
    'dicas',
    'django',
    'python',
]

aux = []

for category in categories:
    obj = Category(title=category)
    aux.append(obj)

Category.objects.bulk_create(aux)


titles = [
    {
        'title': 'Django Boilerplate',
        'subtitle': 'Django Boilerplate',
        'category': 'dicas'
    },
    {
        'title': 'Django extensions',
        'subtitle': 'Django extensions',
        'category': 'dicas'
    },
    {
        'title': 'Django Admin',
        'subtitle': 'Django Admin',
        'category': 'admin'
    },
    {
        'title': 'Django Autoslug',
        'subtitle': 'Django Autoslug',
        'category': 'dicas'
    },
]

aux = []

for title in titles:
    category = Category.objects.filter(title=title['category']).first()
    article = dict(
        title=title['title'],
        subtitle=title['subtitle']
    )
    if category:
        obj = Article(category=category, **article)
    else:
        obj = Article(**article)
    aux.append(obj)

Article.objects.bulk_create(aux)
```



# 4 - Django Admin personalizado

<a href="https://youtu.be/jogkxIkCzI8">
    <img src="img/youtube.png">
</a>

https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#modeladmin-options

#### admin.py

```python
from django.conf import settings
from django.contrib import admin

from .models import Article, Category

# from .forms import ArticleAdminForm


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'get_published_date')
    search_fields = ('title',)
    list_filter = (
        'category',
    )
    readonly_fields = ('slug',)
    date_hierarchy = 'published_date'
    # form = ArticleAdminForm

    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    get_published_date.short_description = 'Data de Publicação'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request, obj=None):
        return False

    if not settings.DEBUG:
        def has_delete_permission(self, request, obj=None):
            return False
```




# 5 - Django Admin Date Range filter

<a href="https://youtu.be/s5QzePekrvQ">
    <img src="img/youtube.png">
</a>

https://github.com/tzulberti/django-datefilterspec

```
pip install django-daterange-filter
```

```python
# settings.py
INSTALLED_APPS = (
    ...
    'daterange_filter'
)
```

```python
# admin.py
from daterange_filter.filter import DateRangeFilter

...

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    ...
    list_filter = (
        ('published_date', DateRangeFilter),
        'category',
    )
```

# 6 - Geradores de senhas randômicas - uuid, hashids, secrets

<a href="https://youtu.be/-3znAePkMqY">
    <img src="img/youtube.png">
</a>

## 6.1 - uuid

https://docs.python.org/3/library/uuid.html

```python
import uuid

uuid.uuid4()

uuid.uuid4().hex
```

```python
# models.py
import uuid

from django.db import models


class UuidModel(models.Model):
    slug = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True

class Category(UuidModel):
    title = models.CharField('título', max_length=50, unique=True)
    ...
```

## 6.2 - shortuuid

<a href="https://youtu.be/qsRefchlXlo">
    <img src="img/youtube.png">
</a>


https://pypi.org/project/shortuuid/

```
pip install shortuuid
```

```python
>>> import shortuuid
>>> 
>>> shortuuid.uuid()
'823MMBZx7LNEnnPBtCAorG'
>>> 
>>> shortuuid.uuid(name='example.com')
'exu3DTbj2ncsn9tLdLWspw'
>>> 
>>> shortuuid.ShortUUID().random(length=22)
'4CHN7TshKtrVnW4KLgVMhY'
>>> 
>>> shortuuid.set_alphabet('regis')
>>> shortuuid.uuid()
'gerigigiesreissgisrsggrrseieereggierrgreriissreiiisiegrr'
>>> 
```

## 6.3 - hashids

https://gist.github.com/rg3915/4684721a603cf6d0dd3b9495744482fe

https://pypi.org/project/hashids/

```
pip install hashids
```

```python
from hashids import Hashids

hashids = Hashids()

>>> hashids.encode(42)
'9x'
>>> hashids.decode('9x')
(42,)
>>> hashids.encode(665190)
'k7qWJ'
>>> hashids.decode('k7qWJ')
(665190,)
>>> hashids.encode(1122, 4200, 32665)
'ELmhW0mFD7o'
>>> hashids.decode('ELmhW0mFD7o')
(1122, 4200, 32665)
>>> hashids = Hashids(alphabet='abcdefghijklmnopqrstuvwxyz1234567890', min_length=22)
>>> for i in range(10): hashids.encode(i)
... 
'9xkwnvoj3ejwgp6481y5mq'
'ml6kz731jdkoe524rxn0yq'
'kwp7yx456gl9g91lm23v8n'
'0qr6jxo9memje214w8zlvp'
'9poy2jq1xdn0e037nwv4zl'
'nz97pw01jgo5el24yrxv6m'
'q4pkmy631epjenrxv70w5l'
'n97kyw8q0dq9eo143z2x6v'
'x7n4zl0pkgr4d6o3vq92wy'
'6y27mjnzkev3d3549vq0xl'
>>> 
```

### django-hashid-field

https://pypi.org/project/django-hashid-field/

```
pip install django-hashid-field==3.1.3
```

```python
# models.py
from hashid_field import HashidAutoField


class Article(models.Model):
    id = HashidAutoField(primary_key=True)
    ...
```


```python
# python manage.py shell_plus
from hashid_field import Hashid

articles = Article.objects.all()
for article in articles:
    hashid = Hashid(article.id)
    print(article.id, hashid.id)
```

https://www.howtogeek.com/howto/30184/10-ways-to-generate-a-random-password-from-the-command-line/

### Gerando senhas no terminal Linux

```
date +%s | sha256sum | base64 | head -c 32 ; echo

openssl rand -base64 32

strings /dev/urandom | grep -o '[[:alnum:]]' | head -n 30 | tr -d '\n'; echo

date | md5sum
```


```
# apt install -y gpw

gpw

gpw 3 32

gpw 1 5
```

### Gerando senhas com Python

#### com random

```python
import random

chars = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
size = 8
secret_key = "".join(random.sample(chars,size))
print(secret_key)
```

#### com random e string

https://pynative.com/python-generate-random-string/

```python
# Generate a random string of specific letters only

import random
import string


def randString(length=5):
    # put your letters in the following string
    your_letters='abcdefghi'
    return ''.join((random.choice(your_letters) for i in range(length)))

print("Random String with specific letters ", randString())
print("Random String with specific letters ", randString(5))
```

#### com secrets

https://docs.python.org/3/library/secrets.html

*New in Python 3.6*

```python
import secrets

secrets.token_hex(16)

secrets.token_urlsafe(16)

url = 'https://mydomain.com/reset=' + secrets.token_urlsafe()
```

### Django

```
vim contrib/env_gen.py
```

```python
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

print(CONFIG_STRING)

# Writing our configuration file to '.env'
with open('.env', 'w') as configfile:
    configfile.write(CONFIG_STRING)
```

```
python contrib/env_gen.py
```

# 7 - Rodando o ORM do Django no Jupyter Notebook

<a href="https://youtu.be/bXtmvu_O_sk">
    <img src="img/youtube.png">
</a>


Instale

```
pip install ipython[notebook]
```

Rode

```
python manage.py shell_plus --notebook
```

**Obs**: No Django 3.x talvez você precise dessa configuração [async-safety](https://docs.djangoproject.com/en/3.0/topics/async/#async-safety).

`os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"`


# 8 - Conhecendo o Django Debug Toolbar

<a href="https://youtu.be/T23bEwMhD6A">
    <img src="img/youtube.png">
</a>


https://django-debug-toolbar.readthedocs.io/en/latest/

```
pip install django-debug-toolbar
```

#### Configurando o `settings.py`

```
INSTALLED_APPS = [
    # ...
    'django.contrib.staticfiles',
    # ...
    'debug_toolbar',
]

MIDDLEWARE = [
    # ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Deve estar por último.
]

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

STATIC_URL = '/static/'
```

#### Configurando o `urls.py`

```
from django.conf import settings
from django.urls import include, path

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

# 9 - Escondendo suas senhas python-decouple

<a href="https://youtu.be/eOwN7e0QBXo">
    <img src="img/youtube.png">
</a>

[Video do Henrique Bastos na Live de Python #97](https://www.youtube.com/watch?v=zYJGpLw5Wv4)

<a href="https://www.youtube.com/watch?v=zYJGpLw5Wv4">
    <img src="img/youtube.png">
</a>


https://github.com/henriquebastos/python-decouple


```
pip install python-decouple
```

Crie um arquivo `.env` com o seguinte conteúdo (de exemplo)

```
DEBUG=True
SECRET_KEY=c9^3g^bn6wgo8tabf*dl$@vx@m-!9ux%*9)88qnun&hk++sa90
ALLOWED_HOSTS=127.0.0.1,.localhost
POSTGRES_DB=mydb
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypass
DB_HOST=localhost

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=

# console ou smtp
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

repare que não deve haver espaços e nem aspas.

E em `settings.py` faça

```
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())

EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('DB_HOST', 'localhost'),
        'PORT': '5432',
    }
}
```

# 10 - Prototipagem de web design (Mockup)

<a href="https://youtu.be/Ypbj_d1oGuY">
    <img src="img/youtube.png">
</a>


[excalidraw.com](https://excalidraw.com/)

[moqups.com](https://moqups.com/)

[balsamiq.com](https://balsamiq.com/)

[marvelapp.com](https://marvelapp.com/)

[mockflow.com](https://www.mockflow.com/)


# 11 - Bootstrap e Bulma + Colorlib

<a href="https://youtu.be/J86_rp0ibGI">
    <img src="img/youtube.png">
</a>


[getbootstrap.com](https://getbootstrap.com/)

[getbootstrap.com/docs/4.5/examples](https://getbootstrap.com/docs/4.5/examples/)

[bulma.io](https://bulma.io/)

[bulmatemplates.github.io/bulma-templates](https://bulmatemplates.github.io/bulma-templates/)

[bulmathemes.com](https://bulmathemes.com/)

[colorlib.com](https://colorlib.com/)


# 12 - Imagens: pexels e unsplash

<a href="https://youtu.be/g95YG5RGGmE">
    <img src="img/youtube.png">
</a>


[pexels.com](https://www.pexels.com/pt-br/)

[unsplash.com](https://unsplash.com/)


# 13 - Cores

<a href="https://youtu.be/EcwxPzgwE4I">
    <img src="img/youtube.png">
</a>


[color.adobe.com/pt/create/color-wheel](https://color.adobe.com/pt/create/color-wheel)

[coolors.co](https://coolors.co/)

[materialuicolors.co](https://materialuicolors.co/)

[htmlcolorcodes.com](https://htmlcolorcodes.com/)

[clrs.cc](http://clrs.cc/)


# 14 - Herança de Templates e Arquivos estáticos

<a href="https://youtu.be/wSfuzUVnuzw">
    <img src="img/youtube.png">
</a>


[Video Introdução a Arquitetura do Django - Pyjamas 2019](https://www.youtube.com/watch?v=XjXpwZhOKOs)

<a href="https://www.youtube.com/watch?v=XjXpwZhOKOs">
    <img src="img/youtube.png">
</a>


![diagrama](templates-diagram.png)

![templates-pyjamas](https://raw.githubusercontent.com/rg3915/pyjamas2019-django/master/img/final.png)


# 15 - Busca por data no frontend

<a href="https://youtu.be/sqhQM5KUFHE">
    <img src="img/youtube.png">
</a>


Considere um template com os campos:

```html
<input class="form-control" name='start_date' type="date">
<input class="form-control" name='end_date' type="date">
```

Em `views.py` basta fazer:

```python
def article_list(request):
    template_name = 'core/article_list.html'
    object_list = Article.objects.all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        # Converte em data e adiciona um dia.
        end_date = parse(end_date) + timedelta(1)
        object_list = object_list.filter(
            published_date__range=[start_date, end_date]
        )

    context = {'object_list': object_list}
    return render(request, template_name, context)
```

Pra não precisar fazer o

```python
end_date = parse(end_date) + timedelta(1)
```

basta acrescentar `date` antes do `range`, dai fica assim:

```python
object_list = object_list.filter(
    published_date__date__range=[start_date, end_date]
)
```

Agradecimentos a [@walisonfilipe](https://twitter.com/walisonfilipe)


# 16 - Filtros com [django-filter](https://django-filter.readthedocs.io/en/stable/)

<a href="https://youtu.be/LZJjSeJC09A">
    <img src="img/youtube.png">
</a>


Instale o [django-filter](https://django-filter.readthedocs.io/en/stable/)

```
pip install django-filter
```

Acrescente-o ao `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    ...
    'django_filters',
]
```

Crie um arquivo `filters.py`

```python
import django_filters

from .models import Article


class ArticleFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    subtitle = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Article
        fields = ('title', 'subtitle')
```

Em `views.py`

```python
from .filters import ArticleFilter


def article_list(request):
    template_name = 'core/article_list.html'
    object_list = Article.objects.all()
    article_filter = ArticleFilter(request.GET, queryset=object_list)

    ...

    context = {
        'object_list': article_filter,
        'filter': article_filter
    }
    return render(request, template_name, context)
```

Em `article_list.html`

```html
  <div class="row">
    <div class="col-md-4">
      <form method="GET">
        {{ filter.form.as_p }}
        <input type="submit" />
      </form>
    </div>

    <div class="col-md-8">
      <table class="table">
        <thead>
          <tr>
            <th>Título</th>
            <th>Sub-título</th>
            <th>Data de publicação</th>
          </tr>
        </thead>
        <tbody>
          {% for obj in filter.qs %}
            <tr>
              <td>{{ obj.title }}</td>
              <td>{{ obj.subtitle }}</td>
              <td>{{ obj.published_date }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
```

# 17 - Criando comandos personalizados

<a href="https://youtu.be/tqr23jPrqrw">
    <img src="img/youtube.png">
</a>


Baseado em [Criando novos comandos no django-admin](http://pythonclub.com.br/criando-novos-comandos-no-django-admin.html) e na [Live 95 do Edu Live de Python](https://youtu.be/cyxky2QJlwg?t=3482).

### Criando as pastas

Para criarmos um novo comando precisamos das seguintes pastas:

```
core
├── management
│   ├── __init__.py
│   ├── commands
│   │   ├── __init__.py
│   │   ├── novocomando.py
```

No nosso caso, teremos 2 novos comandos, então digite, estando na pasta myproject

```
mkdir -p core/management/commands
touch core/management/__init__.py
touch core/management/commands/{__init__.py,hello.py,search.py}
```


```python
# hello.py
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Print hello world.'

    def add_arguments(self, parser):
        # Argumento nomeado (opcional)
        parser.add_argument(
            '--awards', '-a',
            action='store_true',
            help='Ajuda da opção aqui.'
        )

    def handle(self, *args, **options):
        self.stdout.write('Hello world.')
        if options['awards']:
            self.stdout.write('Awards')
```


```python
# search.py
from django.core.management.base import BaseCommand

from myproject.core.models import Article


class Command(BaseCommand):
    help = """Localiza um artigo pelo título ou sub-título."""

    def add_arguments(self, parser):
        parser.add_argument(
            '--title', '-t',
            dest='title',
            default=None,
            help='Localiza um artigo pelo título.'
        )
        parser.add_argument(
            '--subtitle', '-sub',
            dest='subtitle',
            default=None,
            help='Localiza um artigo pelo sub-título.'
        )

    def handle(self, title=None, subtitle=None, **options):
        """ dicionário de filtros """
        self.verbosity = int(options.get('verbosity'))

        filters = {
            'title__icontains': title,
            'subtitle__icontains': subtitle,
        }

        filter_by = {
            key: value for key,
            value in filters.items() if value is not None
        }
        queryset = Article.objects.filter(**filter_by)

        if self.verbosity > 0:
            for article in queryset:
                self.stdout.write("{0} {1}".format(
                    article.title, article.subtitle))
            self.stdout.write(f'\n{queryset.count()} artigos localizados.')
```

# 18 - bulk_create e bulk_update

<a href="https://youtu.be/U99VT4UwJ5k">
    <img src="img/youtube.png">
</a>


## bulk_create

O [bulk_create](https://docs.djangoproject.com/en/3.0/ref/models/querysets/#bulk-create) serve para inserir uma grande quantidade de dados num banco de forma super rápida.

Vamos usar o

`python manage.py shell_plus`

Primeiro vamos criar uns dados aleatórios

```python
import secrets
import string

N = 12
list_items = []

for i in range(100):
    res = ''.join(secrets.choice(string.ascii_lowercase) for i in range(N))
    list_items.append(res)
```

Agora vamos inserir os dados com bulk_create

```python
aux = []
for item in list_items:
    obj = Article(title=item, subtitle=item)
    aux.append(obj)

Article.objects.bulk_create(aux)
```

## bulk_update

Como o nome já diz, o [bulk_update](https://docs.djangoproject.com/en/3.0/ref/models/querysets/#bulk-update) serve para atualizar os dados.


```python
articles = Article.objects.all()
category = Category.objects.first()
for article in articles:
    article.category = category

Article.objects.bulk_update(articles, ['category'])
```

# 19 - Criando Issues por linha de comando com a api do github

<a href="https://youtu.be/XwT2CMrGfiE">
    <img src="img/youtube.png">
</a>


## [github cli](https://docs.github.com/en/rest/reference/issues#create-an-issue)

`pip install requests`

```python
import json

import requests
from decouple import config

# Autenticação
REPO_USERNAME = config('REPO_USERNAME')
REPO_PASSWORD = config('REPO_PASSWORD')

# O repositório para adicionar a issue
REPO_OWNER = config('REPO_OWNER')
REPO_NAME = config('REPO_NAME')


def make_github_issue(title, body=None, assignee=None, milestone=None, labels=None):
    '''
    Create an issue on github.com using the given parameters.
    '''
    url = 'https://api.github.com/repos/%s/%s/issues' % (REPO_OWNER, REPO_NAME)
    session = requests.Session()
    session.auth = (REPO_USERNAME, REPO_PASSWORD)
    # Create our issue
    issue = {
        'title': title,
        'body': body,
        'assignee': assignee,
        'milestone': milestone,
        'labels': labels
    }
    # Add the issue to our repository
    r = session.post(url, json.dumps(issue))
    if r.status_code == 201:
        print('Successfully created Issue "%s"' % title)
    else:
        print('Could not create Issue "%s"' % title)
        print('Response:', r.content)


if __name__ == '__main__':
    title = 'Criar github cli'
    body = 'API para criar issues por linha de comando.'
    make_github_issue(
        title=title,
        body=body,
        assignee='rg3915',
        milestone=None,
        labels=['enhancement']
    )
```


## 20 - api github e click

<a href="https://youtu.be/gwYpMKDAqBM">
    <img src="img/youtube.png">
</a>


`pip install click`

```python
import json

import click
import requests
from decouple import config

'''
https://docs.github.com/en/rest/reference/issues#create-an-issue

Usage: python github_cli2.py --title='Your title' \
            --body='Your description' \
            --assignee='Assignee name' \
            --labels='enhancement'
'''

# Autenticação
REPO_USERNAME = config('REPO_USERNAME')
REPO_PASSWORD = config('REPO_PASSWORD')

# O repositório para adicionar a issue
REPO_OWNER = config('REPO_OWNER')
REPO_NAME = config('REPO_NAME')


@click.command()
@click.option('--title', prompt='Title', help='Type the title.')
@click.option('--body', prompt='Description', help='Type the description.')
@click.option('--assignee', prompt='Assignee', help='Type the assignee name.')
@click.option('--labels', prompt='Labels', help='Type the labels.')
def make_github_issue(title, body=None, assignee=None, milestone=None, labels=None):
    '''
    Create an issue on github.com using the given parameters.
    '''
    url = 'https://api.github.com/repos/%s/%s/issues' % (REPO_OWNER, REPO_NAME)
    session = requests.Session()
    session.auth = (REPO_USERNAME, REPO_PASSWORD)
    # Create our issue
    issue = {
        'title': title,
        'body': body,
        'assignee': assignee,
        'milestone': milestone,
        'labels': [labels]
    }
    # Add the issue to our repository
    r = session.post(url, json.dumps(issue))
    if r.status_code == 201:
        print('Successfully created Issue "%s"' % title)
    else:
        print('Could not create Issue "%s"' % title)
        print('Response:', r.content)


if __name__ == '__main__':
    make_github_issue()
```

Como usar

```
python github_cli2.py --title='Your title' \
    --body='Your description' \
    --assignee='username' \
    --labels='enhancement'
```


# 21 - Criando issues por linha de comando com gitlab cli

<a href="https://youtu.be/mZezRjHv4Xg">
    <img src="img/youtube.png">
</a>


## Configuração

Primeiro precisamos criar um arquivo `/etc/myfile.cfg`

`sudo vim /etc/myfile.cfg  # precisa do sudo`

```
[global]
default = somewhere
ssl_verify = true
timeout = 5

[somewhere]
url = https://gitlab.com
private_token = your-token
api_version = 4
```

## Instalação

`pip install python-gitlab`


## Fazendo um teste no Python

```python
import gitlab

gl = gitlab.Gitlab.from_config('somewhere', ['/etc/myfile.cfg'])

issues = gl.issues.list()
for issue in issues:
    print(issue.iid, issue.title)
```

## Criando issues

```python
import gitlab

gl = gitlab.Gitlab.from_config('somewhere', ['/etc/myfile.cfg'])

issues = gl.issues.list()

project = gl.projects.get(ID-DO-PROJETO)

project.issues.create(
    {'title': 'I have a bug',
   'description': 'Lorem ipsum...'})

for issue in project.issues.list():
    print(issue.iid, issue.title)
```

## gitlab + click

```python
import click
import gitlab
from decouple import config

'''
Usage: python glab-cli.py --title='Your title' --description='Your description'
'''


gl = gitlab.Gitlab.from_config('somewhere', ['/etc/myfile.cfg'])
project = gl.projects.get(config('GITLAB_PROJECT_ID'))


@click.command()
@click.option('--title', prompt='Title', help='Type the title.')
@click.option('--description', prompt='Description', help='Type the description.')
def create_issue(title, description):
    response = project.issues.create(
        {"title": f"{title}",
         "description": f"{description}"})

    click.echo(response.iid)
    click.echo(response.title)


if __name__ == '__main__':
    create_issue()
```

# 22 - Criando issues por linha de comando com bitbucket cli

<a href="https://youtu.be/N2oYZxixcSU">
    <img src="img/youtube.png">
</a>


## Instalação

`pip install bitbucket-python`


## Usando com Python

> Lembre-se de habilitar a criação de issues no repositório.


```python
from bitbucket.client import Client
from decouple import config

email = config('BITBUCKET_EMAIL')
password = config('BITBUCKET_PASSWORD')
client = Client(email, password)

repository_slug = config('REPOSITORY_SLUG')

repo = client.get_repository(repository_slug)

data = {
    'title': 'Your title',
    'content': {'raw': 'Your description'},
    'kind': 'task'
}
# kind: task or bug

response = client.create_issue(repository_slug, data)
```

## Usando com click

```python
import click
from bitbucket.client import Client
from decouple import config

'''
Usage: python bitbucket_cli.py --title='Your title' --description='Your description' --kind='task'
'''


@click.command()
@click.option('--title', prompt='Title', help='Type the title.')
@click.option('--description', prompt='Description', help='Type the description.')
@click.option('--kind', prompt='Kind', help='Kind is task or bug.')
def create_issue(title, description, kind):
    email = config('BITBUCKET_EMAIL')
    password = config('BITBUCKET_PASSWORD')
    repository_slug = config('REPOSITORY_SLUG')

    client = Client(email, password)

    data = {
        'title': title,
        'content': {'raw': description},
        'kind': kind
    }
    response = client.create_issue(repository_slug, data)

    click.echo(response['title'])


if __name__ == '__main__':
    create_issue()
```


# 23 - Diferença entre JSON dump, dumps, load e loads

<a href="https://youtu.be/4AupIlLYkgE">
    <img src="img/youtube.png">
</a>


**Documentação:** [JSON](https://docs.python.org/3/library/json.html)

![json_loads_dumps.png](json_loads_dumps.png)

--

![json_load_dump.png](json_load_dump.png)

## [dumps](https://docs.python.org/3/library/json.html#json.dumps)

Serializa um objeto Python para uma string no formato JSON.

`json.dumps(obj)`

```python
import json

my_dict = {
    "name": "Elliot",
    "age": 25
}
json.dumps(my_dict)
```


## [dump](https://docs.python.org/3/library/json.html#json.dump)

Serializa um objeto Python para um arquivo no formato JSON.

`json.dump(obj, fp)`

onde *fp* significa *file-like object*.

```python
import json

my_dict = {
    "name": "Elliot",
    "age": 25
}
with open('/tmp/file.txt', 'w') as f:
    json.dump(my_dict, f)
```


## [loads](https://docs.python.org/3/library/json.html#json.loads)

Deserializa uma string no formato JSON para um arquivo.

`json.loads(s)`

```python
import json

text = """
{
    "name": "Darlene",
    "age": 27
}
"""
json.loads(text)
```

## [load](https://docs.python.org/3/library/json.html#json.load)

Deserializa um arquivo no formato JSON para um arquivo.

`json.load(fp)`

```python
import json

text = """
{
    "name": "Darlene",
    "age": 27
}
"""
with open('/tmp/file.txt', 'r') as f:
    data = json.load(f)

print(data)
```


**Exemplo**


```python
# json_example.py
import json
from io import StringIO
from pprint import pprint


def json_to_string_with_dumps(my_dict):
    '''
    Serializa (encode) objeto para string no formato JSON.
    '''
    return json.dumps(my_dict, indent=4)


def json_to_string_with_dump_stringio(my_dict):
    '''
    Serializa (encode) objeto para string no formato JSON usando StringIO.
    '''
    io = StringIO()
    json.dump(my_dict, io, indent=4)
    return io.getvalue()


def json_to_file_with_dump_open_file(filename, my_dict):
    '''
    Serializa (encode) objeto para arquivo no formato JSON usando open.
    '''
    with open(filename, 'w') as f:
        json.dump(my_dict, f, indent=4)


def string_to_json_with_loads(text):
    '''
    Deserializa (decode) string no formato JSON para objeto.
    '''
    return json.loads(text)


def string_to_json_with_load_stringio(text):
    '''
    Deserializa (decode) string no formato JSON para objeto usando StringIO.
    '''
    io = StringIO(text)
    return json.load(io)


def file_to_json_with_load_open_file(filename):
    '''
    Deserializa (decode) string no formato JSON para arquivo usando open.
    '''
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


if __name__ == '__main__':
    # Serialize (encode)

    my_dict = {
        "name": "Elliot",
        "age": 25
    }
    print(json_to_string_with_dumps(my_dict))
    print(type(json_to_string_with_dumps(my_dict)))

    my_dict = {
        "name": "Elliot",
        "full_name": {"first_name": "Elliot", "last_name": "Alderson"},
        "items": [1, 2.5, "a"],
        "pi": 3.14,
        "active": True,
        "nulo": None
    }
    print(json_to_string_with_dump_stringio(my_dict))
    print(type(json_to_string_with_dump_stringio(my_dict)))

    filename = '/tmp/file.txt'
    my_dict = {
        "name": "Elliot",
        "full_name": {"first_name": "Elliot", "last_name": "Alderson"},
        "items": [1, 2.5, "a"],
        "pi": 3.14,
        "active": True,
        "nulo": None
    }
    json_to_file_with_dump_open_file(filename, my_dict)

    # Deserialize (decode)

    text = """
    {
        "name": "Darlene",
        "age": 27
    }
    """
    pprint(string_to_json_with_load_stringio(text))
    print(type(string_to_json_with_load_stringio(text)))

    pprint(string_to_json_with_loads(text))
    print(type(string_to_json_with_loads(text)))

    pprint(file_to_json_with_load_open_file(filename))
```


[JsonResponse](https://docs.djangoproject.com/en/2.2/ref/request-response/#jsonresponse-objects) [[source](https://docs.djangoproject.com/en/2.2/_modules/django/http/response/#JsonResponse)]


```python
# core/views.py
import json

from django.http import JsonResponse


def article_json(request):
    text = '''
    {
        "title": "JSON",
        "subtitle": "Entendento JSON dumps e loads",
        "slug": "entendento-json-dumps-e-loads",
        "value": "42"
    }
    '''
    data = json.loads(text)
    pprint(data)
    print(type(data))
    print(data['value'], 'is', type(data['value']))

    data['title'] = 'Introdução ao JSON'
    data['value'] = int(data['value']) + 1
    data['pi'] = 3.14
    data['active'] = True
    data['nulo'] = None
    return JsonResponse(data)
```

```python
# core/urls.py
...
path('articles/json/', v.article_json, name='article_json'),
...
```

Leia mais em [Working With JSON Data in Python](https://realpython.com/python-json/).


# 24 - Barra de progresso

<a href="https://youtu.be/YQlwWn48eTw">
    <img src="img/youtube.png">
</a>


* [progress](https://pypi.org/project/progress/)
* [tqdm](https://tqdm.github.io/)
* [click](https://click.palletsprojects.com/en/7.x/) - [click progressbar](https://click.palletsprojects.com/en/7.x/utils/#showing-progress-bars)
* [progressbar 2](https://progressbar-2.readthedocs.io/en/latest/index.html)
* [clint](https://github.com/kennethreitz-archive/clint)
* [with sys](https://stackoverflow.com/a/3160819)
* [gist rg3915](https://gist.github.com/rg3915/b6368374f74d00d9ea045470718a8ddd)
* [progressbar on Jupyter notebook](https://opensource.com/article/20/12/tqdm-python)

Leia mais em [How to Easily Use a Progress Bar in Python](https://codingdose.info/posts/how-to-use-a-progress-bar-in-python/)


### [progress](https://pypi.org/project/progress/)

`pip install progress`


```python
# example01_progress.py
from time import sleep

from progress.bar import Bar

with Bar('Processing...') as bar:
    for i in range(100):
        sleep(0.02)
        bar.next()
```

```
$ python example01_progress.py
```




### [tqdm](https://tqdm.github.io/)

```
pip install tqdm
```

```python
from time import sleep

# example02_tqdm.py
from tqdm import tqdm

for i in tqdm(range(100)):
    sleep(0.02)
    # Do something
```

```
python example02_tqdm.py
```



### [click](https://click.palletsprojects.com/en/7.x/)

[click progressbar](https://click.palletsprojects.com/en/7.x/utils/#showing-progress-bars)


```
pip install click
```

```python
from time import sleep

# example03_click.py
import click

# Fill character is # by default, you can change it
# for any other char you want, or even change the color.
fill_char = click.style('=', fg='yellow')
with click.progressbar(range(100), label='Loading...', fill_char=fill_char) as bar:
    for i in bar:
        sleep(0.02)
```

```
python example03_click.py
```



### [progressbar 2](https://progressbar-2.readthedocs.io/en/latest/index.html)

```
pip install progressbar2
```

```python
# example04_progressbar2.py
from time import sleep

from progressbar import progressbar

for i in progressbar(range(100)):
    sleep(0.02)
```

```
python example04_progressbar2.py
```



### [clint](https://github.com/kennethreitz-archive/clint)

```
pip install clint
```

```python
# example05_clint.py
from time import sleep

from clint.textui import progress

print('Clint - Regular Progress Bar')
for i in progress.bar(range(100)):
    sleep(0.02)

print('Clint - Mill Progress Bar')
for i in progress.mill(range(100)):
    sleep(0.02)
```

```
python example05_clint.py
```



### [with sys](https://stackoverflow.com/a/3160819)

```python
import sys
# example06_sys.py
import time

toolbar_width = 40

# setup toolbar
sys.stdout.write("[%s]" % (" " * toolbar_width))
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

for i in range(toolbar_width):
    time.sleep(0.1) # do real work here
    # update the bar
    sys.stdout.write("-")
    sys.stdout.flush()

sys.stdout.write("]\n") # this ends the progress bar
```

```
python example06_sys.py
```


### [gist rg3915](https://gist.github.com/rg3915/b6368374f74d00d9ea045470718a8ddd)

```python
# example07_sys.py
import sys
import time


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


users = ['Regis', 'Abel', 'Eduardo', 'Elaine']


for user in progressbar(users, "Processing: "):
    time.sleep(0.1)
    # Do something.


for i in progressbar(range(42), "Processing: "):
    time.sleep(0.05)
    # Do something.
```


```
python example07_sys.py
```


### [progressbar on Jupyter notebook](https://opensource.com/article/20/12/tqdm-python)

```
$ jupyter notebook
```


```python
# progressbar_jupyter.ipynb
import sys

if hasattr(sys.modules["__main__"], "get_ipython"):
    from tqdm import notebook as tqdm
else:
    import tqdm

from time import sleep

n = 0
for i in tqdm.trange(100):
    n += 1
    sleep(0.01)

url = "https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tgz"
import httpx

with httpx.stream("GET", url) as response:
    total = int(response.headers["Content-Length"])
    with tqdm.tqdm(total=total) as progress:
        for chunk in response.iter_bytes():
            progress.update(len(chunk))
```

# 25 - Rodando Shell script dentro do Python

<a href="https://youtu.be/r3MIUX2QTEI">
    <img src="img/youtube.png">
</a>


Para rodar Shell script dentro do Python só precisamos do [subprocess](https://docs.python.org/3/library/subprocess.html).

```python
# subprocess01.py
import subprocess
from datetime import datetime

subprocess.call('echo "Hello"', shell=True)

subprocess.run('echo "Running"', shell=True)

now = datetime.now()

subprocess.run(f'notify-send --urgency=LOW "{now}"', shell=True)


def write_numbers(n):
    return ' '.join([str(i) for i in range(n)])


# print(write_numbers(5))

subprocess.run(f'echo {write_numbers(10)} > /tmp/numbers.txt', shell=True)
subprocess.run('cat /tmp/numbers.txt', shell=True)

subprocess.run('wc -l /tmp/out.log', shell=True)
```

```
$ python subprocess01.py
```



# 26 - Rodando Python dentro do Shell script

<a href="https://youtu.be/WjvVTqfUNMI">
    <img src="img/youtube.png">
</a>


Leia mais em:

[Grande Portal - Shell script 1](http://grandeportal.github.io/shell/2016/shell-script1/)

[Grande Portal - Shell script 2](http://grandeportal.github.io/shell/2016/shell-script2/)

[Grande Portal - Shell script 3](http://grandeportal.github.io/shell/2016/shell-script3/)


Assista também:

<a href="https://www.youtube.com/watch?v=NoQW5CGAGNA">
    <img src="img/youtube.png">
</a>

[Mini-curso Shell script 1](https://www.youtube.com/watch?v=NoQW5CGAGNA)

<a href="https://www.youtube.com/watch?v=aspwrDLSrPI">
    <img src="img/youtube.png">
</a>

[Mini-curso Shell script 2](https://www.youtube.com/watch?v=aspwrDLSrPI)


**Exemplo 1:**


```sh
# running_python01.sh
python -c "print('Rodando Python dentro do Shell script')"
```

```
$ source running_python01.sh
```

Ou

```
$ chmod +x running_python01.sh
$ ./running_python01.sh
```


**Exemplo 2:**

```sh
# ./running_python02.sh 1 2
# ./running_python02.sh 2 1
# ./running_python02.sh 2 2

a=${1}
b=${2}

if [[ $a -eq $b ]]; then
    python -c "print('${a} é igual a ${b}')"
elif [[ $a -lt $b ]]; then
    python -c "print('${a} é menor que ${b}')"
else
    python -c "print('${a} é maior que ${b}')"
fi
```

```
chmod +x running_python02.sh
./running_python02.sh 1 2
./running_python02.sh 2 1
./running_python02.sh 2 2
```

**Exemplo 3:**

```sh
# ./running_python03.sh 1 10
# ./running_python03.sh 35 42

start_value=${1}
end_value=${2}

function join { local IFS="$1"; shift; echo "$*"; }

if [[ $start_value -gt $end_value ]]; then
    python -c "print('O valor inicial não pode ser maior que o valor final.')"
else
    IDS=$(seq -s ' ' $start_value $end_value)

    for id in $IDS; do
        python -c "print('$id')"
    done

    python -c "print('$IDS')"
    python -c "print('$IDS'.split())"
    python -c "print([int(i) for i in '$IDS'.split()])"
    python -c "print(sum([int(i) for i in '$IDS'.split()]))"
    python -c "ids=[int(i) for i in '$IDS'.split()]; print(ids)"
    # Não dá pra usar o laço for do Python na mesma linha, então façamos
    echo "IDS:" $IDS
    result=$(join , ${IDS[@]})
    echo "result:" $result
    python running_python03.py -ids $result
fi
```

```python
# running_python03.py
import click


@click.command()
@click.option('-ids', prompt='Ids', help='Digite uma sequência de números separado por vírgula.')
def get_numbers(ids):
    print('>>>', ids)
    for id in ids.split(','):
        print(id)


if __name__ == '__main__':
    get_numbers()
```


```
chmod +x running_python03.sh
./running_python03.sh 1 10
./running_python03.sh 35 42
```

**Exemplo 4:** Não está no video.

```sh
# running_python04.sh
# Como pegar o resultado do Python e usar numa variável no Shell script.

result=$(python -c "result = 42; print(result)" | xargs echo $var1)
echo 'Resultado:' $result
echo 'Dobro:' $(( $result*2 ))

result2=$(python -c "result = sum([i for i in range(11)]); print(result)" | xargs echo $var2)
echo 'Resultado:' $result2
echo 'Dobro:' $(( $result2*2 ))


# Como usar comandos multilinha.

result=$(python << EOF
aux = []
for i in range(1, 11):
    aux.append(i)
print(sum(aux))
EOF
)
echo 'Resultado:' $result

python << EOF
aux = []
for i in range(1, 11):
    print(i)
    aux.append(i)
print(f'Total: {sum(aux)}')
EOF

result=$(python fibonacci.py | xargs echo $f)
echo 'Fibonacci'
echo $result
```

```python
# fibonacci.py
# Function for nth Fibonacci number

def Fibonacci(n):
    if n < 0:
        print("Incorrect input")
    # First Fibonacci number is 0
    elif n == 0:
        return 0
    # Second Fibonacci number is 1
    elif n == 1:
        return 1
    else:
        return Fibonacci(n - 1) + Fibonacci(n - 2)


print(Fibonacci(9))
# This code is contributed by Saket Modi
```

https://www.geeksforgeeks.org/program-for-nth-fibonacci-number/


# 27 - Retornando os nomes dos campos do model

<a href="https://youtu.be/lU2J5ZCJiyE">
    <img src="img/youtube.png">
</a>


```python
$ python manage.py shell_plus

>>> [field.name for field in User._meta.get_fields()]
['logentry',
 'id',
 'password',
 'last_login',
 'is_superuser',
 'username',
 'first_name',
 'last_name',
 'email',
 'is_staff',
 'is_active',
 'date_joined',
 'groups',
 'user_permissions']

>>> [field.name for field in Article._meta.get_fields()]
['id', 'title', 'subtitle', 'slug', 'category', 'published_date']
```


# 28 - Admin: Usando short description

<a href="https://youtu.be/Uwwr77SR8EE">
    <img src="img/youtube.png">
</a>


Quando não conseguimos usar o `dunder` no `list_display` do admin, então usamos o `short_description`.


```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'get_published_date', 'get_category')
    ...

    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    get_published_date.short_description = 'Data de Publicação'

    def get_category(self, obj):
        if obj.category:
            return obj.category.title

    get_category.short_description = 'Categoria'
```

# 29 - Django Admin: Criando actions no Admin

<a href="https://youtu.be/WofnItMvqKU">
    <img src="img/youtube.png">
</a>

https://docs.djangoproject.com/en/3.1/ref/contrib/admin/actions/

Em `models.py` considere

```python
# models.py
STATUS_CHOICES = (
    ('d', 'Rascunho'),
    ('p', 'Publicado'),
    ('w', 'Retirado'),
)


class Article(models.Model):
    ...
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
```

E em `admin.py`

```python
# admin.py
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    ...
    actions = ('make_published',)

    def make_published(self, request, queryset):
        count = queryset.update(status='p')

        if count == 1:
            msg = '{} artigo foi publicado.'
        else:
            msg = '{} artigos foram publicados.'

        self.message_user(request, msg.format(count))

    make_published.short_description = "Publicar artigos"
```


# 30 - Django Admin: Editando direto na listview do Admin

<a href="https://youtu.be/3skHZrRR1PE">
    <img src="img/youtube.png">
</a>

![img/editar_admin.png](img/editar_admin.png)

```python
# admin.py
...
list_editable = ('title', 'status')
...
```


# 31 - Django Admin: Pegando usuário logado no Admin

<a href="https://youtu.be/qP5-ZICzHyM">
    <img src="img/youtube.png">
</a>

Em `models.py` considere

```python
# models.py
from django.contrib.auth.models import User


class Article(models.Model):
    ...
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
```

E em `admin.py`

```python
# admin.py
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    ...

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
            obj.save()
        super(ArticleAdmin, self).save_model(request, obj, form, change)
```

# 32 - Django Admin: Sobreescrevendo os templates do Admin

<a href="https://youtu.be/0d9VcL8ssTg">
    <img src="img/youtube.png">
</a>

![img/botao_admin.png](img/botao_admin.png)

Se você olhar em 

https://github.com/django/django/tree/main/django/contrib/admin/templates/admin

verá todos os templates usados no Admin.

Na pasta da virtualenv do seu projeto também.

```
ls -l .venv/lib/python3.8/site-packages/django/contrib/admin/templates/admin/
cat .venv/lib/python3.8/site-packages/django/contrib/admin/templates/admin/change_list.html
```

Olhando na doc do Django em [Set up your projects admin template directories](https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#set-up-your-projects-admin-template-directories) nós vemos que devemos ter a seguinte estrutura de pastas:

```
myproject
├── core
│   ├── templates
│   │   ├── admin
│   │   │   ├── base_site.html
│   │   │   ├── login.html
│   │   │   ├── core
│   │   │   │   ├── article
│   │   │   │   │   └── change_list.html
│   │   │   │   └── change_list.html
```

Então vamos criar nossas pastas

```
mkdir -p myproject/core/templates/admin/core/article
```

Agora vamos criar o primeiro `change_list.html`

```
touch myproject/core/templates/admin/core/change_list.html
```

E seu conteúdo será:

```html
{% extends "admin/change_list.html" %}

{% block object-tools-items %}
  {{ block.super }}
  <li>
    <a href="botao-da-app/">
      Novo botão
    </a>
  </li>
{% endblock %}
```

Depois

```
touch myproject/core/templates/admin/core/article/change_list.html
```

Com o conteúdo:

```html
{% extends "admin/change_list.html" %}

{% block object-tools-items %}
  {{ block.super }}
  <li>
    <a href="botao-artigo/">
      Botão do Artigo
    </a>
  </li>
{% endblock %}
```

Para que o Django Admin reconheça esses templates precisamos configurar o `settings.py`

```python
# settings.py
TEMPLATES = [
    {
        ...
        'DIRS': [
            BASE_DIR,
            os.path.join(BASE_DIR, 'templates')
        ],
        ...
    },
]
```

Agora edite `admin.py`

```python
from django.contrib import admin, messages
# admin.py
from django.shortcuts import redirect
from django.urls import path


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    ...

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                'botao-artigo/',
                self.admin_site.admin_view(self.minha_funcao, cacheable=True)
            ),
        ]
        return my_urls + urls

    def minha_funcao(self, request):
        print('Ao clicar no botão, faz alguma coisa...')
        messages.add_message(
            request,
            messages.INFO,
            'Ação realizada com sucesso.'
        )
        return redirect('admin:core_article_changelist')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ...

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                'botao-da-app/',
                self.admin_site.admin_view(self.minha_funcao_category, cacheable=True)
            ),
        ]
        return my_urls + urls

    def minha_funcao_category(self, request):
        print('Ao clicar no botão, faz alguma coisa em category...')
        messages.add_message(
            request,
            messages.INFO,
            'Ação realizada com sucesso.'
        )
        return redirect('admin:core_category_changelist')
```

## Sobreescrevendo a tela de login do Admin

<a href="https://youtu.be/ci4LtLxDCRM">
    <img src="img/youtube.png">
</a>

![img/login.png](img/login.png)

Em [AdminSite attributes](https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#adminsite-attributes) nós temos o atributo [AdminSite.login_template](https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#django.contrib.admin.AdminSite.login_template).

A partir daí podemos fazer

```python
# admin.py
admin.site.login_template = 'myproject/core/templates/admin/login.html'
```

Vendo

```
cat .venv/lib/python3.8/site-packages/django/contrib/admin/templates/admin/login.html
cat .venv/lib/python3.8/site-packages/django/contrib/admin/templates/admin/base_site.html
```

E nos templates

```
touch myproject/core/templates/admin/login.html
```


```html
<!-- myproject/core/templates/admin/login.html -->
{% extends "admin/login.html" %}
{% load static %}

{% block branding %}
  <h1 id="site-name">
    <a href="{% url 'admin:index' %}">
      <img src="{% static 'img/django-logo-negative.png' %}" alt="django-logo-negative.png" width="100px">
    </a>
  </h1>
{% endblock %}

{% block extrastyle %}
  {{ block.super }}
  <link rel="stylesheet" type="text/css" href="{% static "css/login.css" %}" />
  {{ form.media }}
{% endblock %}
```

E pra caprichar no CSS

```css
/* myproject/core/static/css/login.css */
body.login {
    background: url("../img/headset.jpg") no-repeat center center;
    background-size: 100% auto;
}

html {
    min-height: 100%;
}
```

https://www.djangoadmintutorials.com/how-to-customize-django-admin-login-page/


## Inserindo um logo no header do Admin

<a href="https://youtu.be/7NcghC_eySs">
    <img src="img/youtube.png">
</a>

![img/header_admin.png](img/header_admin.png)

Basta criar `base_site.html`

```
touch myproject/core/templates/admin/base_site.html
```

```html
{% extends "admin/base_site.html" %}
{% load static %}

{% block branding %}
  <h1 id="site-name">
    <a href="{% url 'admin:index' %}">
      <img src="{% static 'img/django-logo-negative.png' %}" alt="django-logo-negative.png" width="70px">
    </a>
  </h1>
{% endblock %}
```

**Importante:** mude a ordem das `apps` em `settings.py`

```python
# settings.py
INSTALLED_APPS = [
    'myproject.core',
    'django.contrib.admin',
    ...
]
```

https://books.agiliq.com/projects/django-admin-cookbook/en/latest/logo.html


# 33 - Github cli

<a href="https://youtu.be/Y5VO3u2hp10">
    <img src="img/youtube.png">
</a>


https://cli.github.com/

```
gh auth login
gh repo clone rg3915/dicas-de-django
gh repo view
gh pr checks
gh pr create
gh pr status
gh pr merge
gh issue list
```

```
gh issue create --title "Github cli" --body "Experimentar Github cli https://cli.github.com" \
--label "enhancement" \
--assignee "@me"
```


```
gh issue create -t "Github cli" -b "Experimentar Github cli
https://cli.github.com" \
-l "enhancement" \
-a "@me"
```


Fechar issue

```
git commit -m 'Usando o github cli. close #34'
git push
```


# 34 - Django: custom template tags

<a href="https://youtu.be/ldMf8AW2h4Y">
    <img src="img/youtube.png">
</a>


https://docs.djangoproject.com/en/3.2/ref/templates/builtins/

### Built-in tags

```html
{% for obj in object_list %}
  <tr>
    <td>{{ forloop.counter }}</td>
    ...
    {% if obj.category.title == 'Django' %}
      <td>{{ obj.category }}</td>
    {% endif %}
  </tr>
{% endfor %}
```


### Built-in filter

```html
...
<td>{{ forloop.counter }}</td>
<td>{{ obj.title|slugify }}</td>
<td>{{ obj.title|truncatechars:13 }}</td>
<td>{{ obj.subtitle|safe|default:"---" }}</td>
<td>{{ obj.published_date|date:"d/m/Y" }}</td>
...
```

```
subtitle='<p>lorem</p>'
```


```html
{{ obj.subtitle|safe }}
```

### Writing custom template filters

#### Code layout

https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#code-layout

```
core
├── __init__.py
├── models.py
├── templatetags
│   ├── __init__.py
│   ├── model_name_tags.py
│   └── usergroup_tags.py
```

https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#writing-custom-template-filters

```
mkdir myproject/core/templatetags
touch myproject/core/templatetags/__init__.py
touch myproject/core/templatetags/usergroup_tags.py
```


```python
# usergroup_tags.py
from django import template

register = template.Library()


@register.filter('name_group')
def name_group(user):
    ''' Retorna o nome do grupo do usuário. '''
    _groups = user.groups.first()
    if _groups:
        return _groups.name
    return ''


@register.filter('has_group')
def has_group(user, group_name):
    ''' Verifica se este usuário pertence a um grupo. '''
    if user:
        groups = user.groups.all().values_list('name', flat=True)
        return True if group_name in groups else False
    return False
```

```html
{% load usergroup_tags %}

{% if request.user|has_group:"Autor" %}
É Autor.
{% endif %}
```

### Writing custom template tags

https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#writing-custom-template-tags

```
touch myproject/core/templatetags/model_name_tags.py
```

```python
# model_name_tags.py
from django import template

register = template.Library()


@register.simple_tag
def model_name(value):
    '''
    Django template filter which returns the verbose name of a model.
    '''
    if hasattr(value, 'model'):
        value = value.model

    return value._meta.verbose_name.title()


@register.simple_tag
def model_name_plural(value):
    '''
    Django template filter which returns the plural verbose name of a model.
    '''
    if hasattr(value, 'model'):
        value = value.model

    return value._meta.verbose_name_plural.title()
```

```html
{% load model_name_tags %}

Lista de {% model_name_plural model %}
```


# 35 - Django: passando usuário logado no formulário

<a href="https://youtu.be/69jPO_v6ldI">
    <img src="img/youtube.png">
</a>


```python
# forms.py
from django import forms

from .models import Person


class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = '__all__'

    def __init__(self, user=None, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        # my_field = MyModel.objects.filter(user=user)
        if user.is_authenticated:
            print(user)
        else:
            print('Não')
```


```python
# views.py
def person_create(request):
    template_name = 'core/person_form.html'
    # Não esquecer do request.user como primeiro parâmetro.
    form = PersonForm(request.user, request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('person:person_list')

    context = {'form': form}
    return render(request, template_name, context)
```

```python
# models.py
class Person(UuidModel):
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

# 36 - Django: visualizando seus modelos com graph models

<a href="https://youtu.be/99dOVsDBUxg">
    <img src="img/youtube.png">
</a>

```
sudo apt-get install -y graphviz libgraphviz-dev pkg-config
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pygraphviz
pip uninstall pyparsing
pip install -Iv https://pypi.python.org/packages/source/p/pyparsing/pyparsing-1.5.7.tar.gz#md5=9be0fcdcc595199c646ab317c1d9a709
pip install pydot
pip install django-extensions
```

E em `INSTALLED_APPS`

```
INSTALLED_APPS = [
    ...
    'django_extensions',
    ...
]
```

Depois rode

```
python manage.py graph_models -e -g -l dot -o core.png core # only app core
python manage.py graph_models -a -g -o models.png # all
```

### core

![core.png](img/core.png)

### models

![models.png](img/models.png)


# 37 - Faker

<a href="https://youtu.be/ubgVHtLhubw">
    <img src="img/youtube.png">
</a>


https://faker.readthedocs.io/en/master/

O Faker é uma biblioteca ideal para popular o seu banco de dados com dados aleatórios.

Vamos trabalhar em cima do model `Person`, e acrescentar mais uns campos no modelo.

```python
# models.py
class Person(UuidModel):
    first_name = models.CharField('nome', max_length=50)
    last_name = models.CharField('sobrenome', max_length=50, null=True, blank=True)  # noqa E501
    email = models.EmailField(null=True, blank=True)
    bio = models.TextField('biografia', null=True, blank=True)
    birthday = models.DateField('nascimento', null=True, blank=True)
```

Instale o Faker

```
pip install faker
```

E vamos criar um novo comando em `management`

```
touch myproject/core/management/commands/create_data.py
```

```python
# create_data.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker

from myproject.core.models import Person
from myproject.utils.progress_bar import progressbar

fake = Faker()


def gen_email(first_name: str, last_name: str):
    first_name = slugify(first_name)
    last_name = slugify(last_name)
    email = f'{first_name}.{last_name}@email.com'
    return email


def get_person():
    first_name = fake.first_name()
    last_name = fake.first_name()
    email = gen_email(first_name, last_name)
    bio = fake.paragraph(nb_sentences=5)
    birthday = fake.date()
    data = dict(
        first_name=first_name,
        last_name=last_name,
        email=email,
        bio=bio,
        birthday=birthday,
    )
    return data


def create_persons():
    aux_list = []
    for _ in progressbar(range(100), 'Persons'):
        data = get_person()
        obj = Person(**data)
        aux_list.append(obj)
    Person.objects.bulk_create(aux_list)


class Command(BaseCommand):
    help = 'Create data.'

    def handle(self, *args, **options):
        create_persons()
```

Editar `admin.py`

```
admin.site.register(Person)
```

Criar `progress_bar.py`

```
mkdir myproject/utils
touch myproject/utils/progress_bar.py
```

```python
# progress_bar.py
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

Editar `views.py`

```python
# views.py
from django.views.generic import ListView


class PersonListView(ListView):
    model = Person
    template_name = 'core/person_list.html'
```

Editar `urls.py`

```python
# urls.py
...
path('persons/', v.PersonListView.as_view(), name='person_list'),
```

Editar `person_list.html`

```html
# person_list.html
{% extends "base.html" %}

{% block content %}
  <h1>Lista de pessoas</h1>

  <div class="row">
    <div class="col">
      <form action="." method="GET">
        <div class="row">
          <div class="col">
            <input name="search" class="form-control mb-2" type="text" placeholder="Buscar..." />
          </div>
          <div class="col-auto">
            <button class="btn btn-success mb-2" type="submit">OK</button>
            <button class="btn btn-link mb-2">Limpar</button>
          </div>
        </div>
      </form>
    </div>
  </div>

  <table class="table">
    <thead>
      <tr>
        <th>Nome</th>
        <th>Sobrenome</th>
        <th>E-mail</th>
        <th>Biografia</th>
        <th>Nascimento</th>
      </tr>
    </thead>
    <tbody>
      {% for object in object_list %}
        <tr>
          <td>{{ object.first_name }}</td>
          <td>{{ object.last_name }}</td>
          <td>{{ object.email }}</td>
          <td>{{ object.bio }}</td>
          <td>{{ object.birthday|date:"d/m/Y" }}</td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
{% endblock content %}
```


# 38 - Django: Paginação + Filtros

<a href="https://youtu.be/eXipSfa-HOQ">
    <img src="img/youtube.png">
</a>


Primeiro vamos definir a paginação:

Edite `views.py`

```python
# views.py
class PersonListView(ListView):
    model = Person
    template_name = 'core/person_list.html'
    paginate_by = 5
```

Edite `person_list.html`

```html
<!-- person_list.html -->
...
{% include "includes/pagination.html" %}
```

Criar `includes/pagination.html`

```
mkdir myproject/core/templates/includes
touch myproject/core/templates/includes/pagination.html
```


```html
<!-- pagination.html -->
<!-- https://gist.github.com/rg3915/01ca76f099f431c24bc0536bef83076b -->
<!-- Use https://gist.github.com/rg3915/01ca76f099f431c24bc0536bef83076b#file-pagination02-html -->
<div class="row text-center">
  <div class="col-lg-12">
    <ul class="pagination">
      {% if page_obj.has_previous %}
        <li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}">&laquo;</a></li>
      {% endif %}

      {% for pg in page_obj.paginator.page_range %}
        <!-- Sempre mostra as 3 primeiras e 3 últimas páginas -->
          {% if pg == 1 or pg == 2 or pg == 3 or pg == page_obj.paginator.num_pages or pg == page_obj.paginator.num_pages|add:'-1' or pg == page_obj.paginator.num_pages|add:'-2' %}
            {% if page_obj.number == pg %}
              <li class="page-item active"><a class="page-link" href="?page={{ pg }}">{{ pg }}</a></li>
            {% else %}
              <li class="page-item"><a class="page-link" href="?page={{ pg }}">{{ pg }}</a></li>
            {% endif %}

          {% else %}

            {% if page_obj.number == pg %}
              <li class="page-item active"><a class="page-link" href="?page={{ pg }}">{{ pg }}</a></li>
            {% elif pg > page_obj.number|add:'-4' and pg < page_obj.number|add:'4' %} <!-- Mostra 3 páginas antes e 3 páginas depois da atual -->
              <li class="page-item"><a class="page-link" href="?page={{ pg }}">{{ pg }}</a></li>
            {% elif pg == page_obj.number|add:'-4' or pg == page_obj.number|add:'4' %}
              <li class="page-item"><a class="page-link" href="">...</a></li>
            {% endif %}
          {% endif %}
        {% endfor %}

        {% if page_obj.has_next %}
          <li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}">&raquo;</a></li>
        {% endif %}
    </ul>
  </div>
</div>
```

Editar novamente `views.py`

```python
# views.py
from django.db.models import Q


class PersonListView(ListView):
    model = Person
    template_name = 'core/person_list.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = super(PersonListView, self).get_queryset()

        data = self.request.GET
        search = data.get('search')

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(bio__icontains=search)
            )

        return queryset
```

Criar templatetags `url_replace.py`

```
touch myproject/core/templatetags/url_replace.py
```

```python
# url_replace.py
# https://stackoverflow.com/a/62587351/802542
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    query.pop('page', None)
    query.update(kwargs)
    return query.urlencode()
```

E finalmente edite `pagination.html` trocando todos os `href`

```html
<!-- pagination.html -->
{% load url_replace %}
...
href="?{% url_replace page=page_obj.previous_page_number %}"
...
href="?{% url_replace page=pg %}"
...
href="?{% url_replace page=page_obj.next_page_number %}"
```


# 39 - Django Admin: display decorator (Django 3.2+)

https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#the-display-decorator

**IMPORTANTE:** Usei um [boilerplate](https://github.com/rg3915/dicas-de-django#11---django-boilerplate) para mostrar essa feature num projeto separado. Assista o video no YouTube.

O Django 3.2+ tem uma feature chamada `display` decorator.

Antigamente você fazia `short_description` assim:

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_published_date')

    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    get_published_date.short_description = 'Data de Publicação'
```

... e ainda funciona.

Mas a partir do Django 3.2+ você pode usar o `display` decorator.

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_published_date', 'is_published')

    # Django 3.2+
    @admin.display(description='Data de Publicação')
    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    @admin.display(boolean=True, ordering='-published_date', description='Publicado')
    def is_published(self, obj):
        return obj.published_date is not None
```


# 40 - Formulários: date, datetime, duration e templatetags de data

Vamos falar sobre como trabalhar com date, datetime, duration. Para isso vamos usar os seguintes links como referência:

https://docs.djangoproject.com/en/3.2/ref/forms/fields/

https://docs.djangoproject.com/en/3.2/ref/utils/#django.utils.dateparse.parse_duration

https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#date

https://github.com/igorescobar/jQuery-Mask-Plugin

https://igorescobar.github.io/jQuery-Mask-Plugin/docs.html


Lib JS via CDN.

`<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.mask/1.14.16/jquery.mask.min.js"></script>`


Mas antes vamos criar uma nova app chamada `travel`.

Entre na pasta `myproject` e crie a nova app.

```
cd myproject
python ../manage.py startapp travel
```

Configure em `INSTALLED_APPS`.

```python
INSTALLED_APPS = [
    ...
    'myproject.travel',
]
```

Em `models.py` crie uma classe `Travel`.

```python
# travel/models.py
cat << EOF > travel/models.py
from django.db import models


class Travel(models.Model):
    destination = models.CharField('destino', max_length=200)
    date_travel = models.DateField('data', null=True, blank=True)
    datetime_travel = models.DateTimeField('data/hora', null=True, blank=True)
    time_travel = models.TimeField('tempo', null=True, blank=True)
    duration_travel = models.DurationField('duração', null=True, blank=True)

    class Meta:
        ordering = ('destination',)
        verbose_name = 'viagem'
        verbose_name_plural = 'viagens'

    def __str__(self):
        return self.destination

EOF
```

Em seguida rode o comando

```
cd ..
python manage.py makemigrations
python manage.py migrate
```

Agora vamos editar o `urls.py` principal.

```python
# urls.py
urlpatterns = [
    ...
    path('travel/', include('myproject.travel.urls', namespace='travel')),
    ...
]

```

Edite `travel/urls.py`.

```python
# travel/urls.py
cat << EOF > myproject/travel/urls.py
from django.urls import path

from myproject.travel import views as v

app_name = 'travel'


urlpatterns = [
    path('', v.TravelListView.as_view(), name='travel_list'),
    path('create/', v.TravelCreateView.as_view(), name='travel_create'),
]

EOF
```

Edite `travel/views.py`.

```python
# travel/views.py
cat << EOF > myproject/travel/views.py
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import TravelForm
from .models import Travel


class TravelListView(ListView):
    model = Travel
    paginate_by = 10


class TravelCreateView(CreateView):
    model = Travel
    form_class = TravelForm
    success_url = reverse_lazy('travel:travel_list')

EOF
```

Crie a pasta

```
mkdir -p myproject/travel/templates/travel
```


Edite `travel/templates/travel/travel_list.html`

```html
cat << EOF > myproject/travel/templates/travel/travel_list.html
<!-- travel_list.html -->
{% extends "base.html" %}

{% block content %}
  <h1>
    Viagens
    <a class="btn btn-primary" href="{% url 'travel:travel_create' %}">Adicionar</a>
  </h1>
  <table class="table">
    <thead>
      <tr>
        <th>Destino</th>
        <th>Data</th>
        <th>Data e Hora</th>
        <th>Time</th>
        <th>Duração</th>
      </tr>
    </thead>
    <tbody>
      {% for object in object_list %}
        <!-- https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#date -->
        <tr>
          <td>{{ object.destination }}</td>
          <td>{{ object.date_travel|default:'---' }}</td>
          <td>{{ object.datetime_travel|default:'---' }}</td>
          <td>{{ object.time_travel|default:'---' }}</td>
          <td>{{ object.duration_travel|default:'---' }}</td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
  {% include "includes/pagination.html" %}
{% endblock content %}
EOF
```

Edite `travel/templates/travel/travel_form.html`

```html
cat << EOF > myproject/travel/templates/travel/travel_form.html
<!-- travel_form.html -->
{% extends "base.html" %}

{% block content %}
  <h1>Formulário</h1>
  <div class="cols-6">
    <form class="form-horizontal" action="." method="POST">
      <div class="col-sm-6">
        {% csrf_token %}
        {{ form.as_p }}
        <div class="form-group">
          <button type="submit" class="btn btn-primary">Salvar</button>
        </div>
      </div>
    </form>
  </div>
{% endblock content %}
EOF
```


Edite `travel/forms.py`

```python
cat << EOF > myproject/travel/forms.py
from django import forms

from .models import Travel


class TravelForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Travel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TravelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
EOF
```

Edite `myproject/core/templates/nav.html`

```html
<li class="nav-item">
    <a class="nav-link" href="{% url 'travel:travel_list' %}">Viagens</a>
</li>
```

Rode a aplicação e cadastre uma viagem com os seguintes dados:

```
Destino: Japão
Data: 2021-07-18
Data/hora: 2021-07-18 01:59
Tempo: 23:01:58
Duração: 26:01:02
```


Edite `travel/admin.py`

```python
cat << EOF > myproject/travel/admin.py
from django.contrib import admin

from .models import Travel


@admin.register(Travel)
class TravelAdmin(admin.ModelAdmin):
    list_display = (
        'destination',
        'date_travel',
        'datetime_travel',
        'time_travel',
        'duration_travel',
    )
    search_fields = ('destination',)

EOF
```

E abra o Admin.


Edite `travel/templates/travel/travel_list.html` novamente

Vejamos os templatetags.

```html
...
<td>{{ object.date_travel|date:"d/m/Y"|default:'---' }}</td>
<td>{{ object.datetime_travel|date:"d/m/Y H:i:s"|default:'---' }}</td>
<td>{{ object.time_travel|time:"H:i:s"|default:'---' }}</td>
...
```


Edite `travel/forms.py` novamente

```python
# travel/forms.py
...
class TravelForm(forms.ModelForm):

    date_travel = forms.DateField(
        label='Data',
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
            }),
        input_formats=('%Y-%m-%d',),
    )
    datetime_travel = forms.DateTimeField(
        label='Data/Hora',
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={
                'type': 'datetime-local',
            }),
        input_formats=('%Y-%m-%dT%H:%M',),
    )
    time_travel = forms.TimeField(
        label='Tempo',
        widget=forms.TimeInput(
            format='%H:%M',
            attrs={
                'type': 'time',
            }),
        input_formats=('%H:%M',),
    )
...
```


Edite `core/base.html`

```html
{% block css %}{% endblock css %}
...
<!-- jQuery -->
<script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>

{% block js %}{% endblock js %}
```


Edite `travel/templates/travel/travel_form.html` novamente

```html
{% block css %}
  <style>
    p {
      color: #000;
    }
    label.required:after {
      content: "*";
      color: red;
    }
  </style>
{% endblock css %}
...
{% block js %}

<!-- https://github.com/igorescobar/jQuery-Mask-Plugin -->
<!-- https://igorescobar.github.io/jQuery-Mask-Plugin/docs.html -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.mask/1.14.16/jquery.mask.min.js"></script>

<script>
  $('#id_duration_travel').mask('00:00:00');
</script>

{% endblock js %}
```

Compare o formato do datetime no templatetags e no formulário:

```
date:"d/m/Y H:i:s"       # templatags
format='%Y-%m-%dT%H:%M'  # forms (ISOformat)
```

https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#date



