# Dica 45 - DRF: Scaffold django apis - Django REST framework

**Versões usadas no vídeo:** Django 3.2.6, Django REST framework 3.12.4, dr-scaffold 2.0.0 e Python 3.9.6.
{: .versoes }

<a href="https://youtu.be/UOW0CaFayFo">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/drf-example](https://github.com/rg3915/drf-example)

[https://github.com/Abdenasser/dr_scaffold](https://github.com/Abdenasser/dr_scaffold)


dr-scaffold é uma lib para criar models e uma API simples em Django REST framework.

Com **uma linha de comando** no terminal, o `dr_scaffold` cria um app (se ainda não existir) e gera para ele o model, o admin, o serializer, a viewset e as rotas, prontos para usar. O próprio autor, Abdenasser, apresentou a biblioteca no artigo "Scaffold django apis like a champion", no blog dele.

Neste tutorial vamos criar um projeto do zero e gerar três APIs: `blog` (autores e posts), `product` (produtos) e `ecommerce` (ordens de compra e seus itens).

## Pré-requisitos

* Python 3 (no vídeo, 3.9.6).
* Nenhum projeto Django prévio: começamos do zero, numa pasta vazia.

## Criando o projeto

Crie e ative um ambiente virtual e instale as bibliotecas. O `dr-scaffold` instala o Django como dependência. Junto vão o Django REST framework, o django-extensions e o python-decouple:

```bash
python -m venv .venv
source .venv/bin/activate
pip install dr-scaffold djangorestframework \
django-extensions python-decouple
```

Crie um arquivo `.env` com a `SECRET_KEY` (só para desenvolvimento):

```bash
cat << EOF > .env
SECRET_KEY=my-super-secret-key-dev-only
EOF
```

Crie um novo projeto chamado `backend`, na pasta atual:

```bash
django-admin startproject backend .
```

Em `backend/settings.py`, troque a `SECRET_KEY` fixa pela variável do `.env` (assim ela não fica exposta quando você versionar o projeto) e adicione o `rest_framework` e o `dr_scaffold` ao `INSTALLED_APPS`:

```python
# backend/settings.py
from pathlib import Path

from decouple import config

...

SECRET_KEY = config('SECRET_KEY')

...

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd apps
    'rest_framework',
    'dr_scaffold',
]
```

## Exemplo 1: blog

### Rodando o comando dr_scaffold

A sintaxe é:

```
python manage.py dr_scaffold <nome_do_app> <NomeDoModel> campo:tipo campo:tipo ...
```

Vamos criar o app `blog` com o model `Author`, que tem um campo `name` do tipo `CharField`:

```bash
python manage.py dr_scaffold blog Author name:charfield
```

Saída:

```
🎉 Your RESTful Author api resource is ready 🎉
```

No vídeo foi gerado só o `Author`. Se quiser também os posts, com uma chave estrangeira para o autor, use o tipo `foreignkey:Model`:

```bash
python manage.py dr_scaffold blog Post body:textfield author:foreignkey:Author
```

### O que o dr_scaffold gerou

O app `blog` foi criado com todos os arquivos. Rodando os dois comandos acima, o conteúdo fica assim (sem o `Post`, é só tirar as partes dele).

```python
# blog/models.py
from django.db import models

class Author(models.Model):    
    name = models.CharField(max_length=255, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Authors"


class Post(models.Model):    
    body = models.TextField(null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Posts"
```

Repare que, além dos campos que pedimos, ele acrescenta um `create_date` com `auto_now_add=True` e um `verbose_name_plural` no `Meta`.

```python
# blog/admin.py
from blog.models import Post
from blog.models import Author
from django.contrib import admin

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    exclude = ()

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    exclude = ()
```

```python
# blog/serializers.py
from blog.models import Post
from blog.models import Author
from rest_framework import serializers

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
```

Até a versão anterior da biblioteca, o serializer gerado era um `HyperlinkedModelSerializer`; na versão usada no vídeo, ele passou a ser um `ModelSerializer` simples.

```python
# blog/views.py
from blog.models import Post
from blog.serializers import PostSerializer
from blog.models import Author
from blog.serializers import AuthorSerializer
from rest_framework import mixins, permissions, viewsets
from rest_framework.response import Response

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
```

As views são `ModelViewSet`, que já implementam listar, criar, detalhar, editar e apagar. Os imports de `mixins`, `permissions` e `Response` não são usados (o autor provavelmente estava experimentando algo), mas não atrapalham.

```python
# blog/urls.py
from blog.views import PostViewSet
from blog.views import AuthorViewSet
from rest_framework import routers
from django.urls import include, path

router = routers.DefaultRouter()

router.register(r'authors', AuthorViewSet)

router.register(r'posts', PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
```

```python
# blog/apps.py
from django.apps import AppConfig

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
```

### Registrando o app e as rotas

Edite `settings.py`

```python
# backend/settings.py
INSTALLED_APPS = [
    ...
    # 3rd apps
    'rest_framework',
    'dr_scaffold',
    # my apps
    'blog',  # <--
]
```

Edite `urls.py`

```python
# backend/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('blog/', include('blog.urls')),
    path('admin/', admin.site.urls),
]
```

Rode as migrations e o servidor:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Abra `http://localhost:8000/blog/`. É a **Api Root** do `DefaultRouter`, com o link para os autores:

```json
{
    "authors": "http://localhost:8000/blog/authors/"
}
```

Em `http://localhost:8000/blog/authors/`, o formulário HTML do Django REST framework permite cadastrar um autor. No vídeo foi cadastrado o "Daniel Greenfeld", e a lista passou a mostrar:

```json
[
    {
        "id": 1,
        "name": "Daniel Greenfeld",
        "create_date": "2021-08-31T18:08:52.449361Z"
    }
]
```

## Exemplo 2: produtos e ordens de compra

Agora o app `product`, com o model `Product`:

```bash
python manage.py dr_scaffold product Product title:charfield price:decimalfield
```

E o app `ecommerce`, com dois models. Comandos longos podem ser quebrados em várias linhas com `\`:

```bash
python manage.py dr_scaffold ecommerce Order nf:charfield

python manage.py dr_scaffold ecommerce OrderItems \
order:foreignkey:Order \
product:foreignkey:Product \
quantity:integerfield \
price:decimalfield
```

Saída:

```
🎉 Your RESTful Order api resource is ready 🎉
⚠️ bare in mind that Product model doesn't exist yet!
🎉 Your RESTful OrderItems api resource is ready 🎉
```

O aviso é importante: o `Product` está em outro app, e o `dr_scaffold` não sabe disso. Os models gerados ficam assim:

```python
# product/models.py
from django.db import models

class Product(models.Model):    
    title = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0.0)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Products"
```

```python
# ecommerce/models.py
from django.db import models

class Order(models.Model):    
    nf = models.CharField(max_length=255, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Orders"


class OrderItems(models.Model):    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(null=True, default=0)
    price = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=0.0)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Orderitem"
```

Os demais arquivos (`admin.py`, `serializers.py`, `views.py`, `urls.py`) seguem o mesmo padrão do `blog`. As rotas geradas são `products` (em `product/urls.py`) e `orders` e `orderitem` (em `ecommerce/urls.py`).

Edite `settings.py`

```python
# backend/settings.py
INSTALLED_APPS = [
    ...
    # 3rd apps
    'rest_framework',
    'dr_scaffold',
    # my apps
    'blog',  # <--
    'product',  # <--
    'ecommerce',  # <--
]
```

Edite `urls.py`

```python
# backend/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('blog/', include('blog.urls')),
    path('product/', include('product.urls')),
    path('ecommerce/', include('ecommerce.urls')),
    path('admin/', admin.site.urls),
]
```

Se rodar o `makemigrations` agora, dá erro, porque o `ecommerce/models.py` usa o `Product` sem importá-lo. Não se esqueça de editar `ecommerce/models.py`:

```python
# ecommerce/models.py
from django.db import models

from product.models import Product
...
```

Agora sim:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Saída do `makemigrations`:

```
Migrations for 'blog':
  blog/migrations/0001_initial.py
    - Create model Author
    - Create model Post
Migrations for 'product':
  product/migrations/0001_initial.py
    - Create model Product
Migrations for 'ecommerce':
  ecommerce/migrations/0001_initial.py
    - Create model Order
    - Create model OrderItems
```

(No vídeo, as migrations do `blog` já tinham sido criadas no exemplo 1, então só aparecem as de `product` e `ecommerce`.)

## Testando a API

* Em `http://localhost:8000/product/products/`, cadastre um produto. No vídeo: título "Two Scoops of Django" e preço 145.
* Em `http://localhost:8000/ecommerce/`, a Api Root mostra as duas rotas:

```json
{
    "orders": "http://localhost:8000/ecommerce/orders/",
    "orderitem": "http://localhost:8000/ecommerce/orderitem/"
}
```

* Em `http://localhost:8000/ecommerce/orders/`, cadastre uma ordem com a nota fiscal 101.
* Em `http://localhost:8000/ecommerce/orderitem/`, cadastre um item: quantidade 2, preço 150 (você pode redefinir o preço na ordem, se quiser), a ordem e o produto escolhidos nas listas do formulário (aparecem como "Order object (1)" e "Product object (1)", porque os models gerados não têm `__str__`).

O resultado do item cadastrado:

```json
{
    "id": 1,
    "quantity": 2,
    "price": "150.00",
    "create_date": "...",
    "order": 1,
    "product": 1
}
```

Pronto: a API está funcionando. A parte mais interessante do `dr_scaffold` é gerar os models a partir da linha de comando, mas ele também cria o admin, os serializers, as views e as rotas, tudo de uma vez. Depois é só ajustar o que precisar (por exemplo, acrescentar um `__str__` nos models).
