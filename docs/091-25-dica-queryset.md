# Dica 25 - Criando Filtros poderosos no Django - Segredos do ORM

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, django-extensions 3.2, django-seed 0.3.1 e Jupyter Notebook.
{: .versoes }

<a href="https://youtu.be/jrqd_zNMhFk">
    <img src="../.gitbook/assets/youtube.png">
</a>

[http://pythonclub.com.br/django-introducao-queries.html](http://pythonclub.com.br/django-introducao-queries.html)

[https://docs.djangoproject.com/en/4.1/ref/models/querysets/](https://docs.djangoproject.com/en/4.1/ref/models/querysets/)

Github: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

Este vídeo faz parte da série **Segredos do ORM**. Vamos ver como escrever consultas eficientes e filtros poderosos com o ORM do Django:

* relacionamento direto (ForeignKey) e `select_related`;
* relacionamento reverso e `prefetch_related` (inclusive com ManyToMany);
* filtro direto e filtro reverso;
* filtro a partir de uma lista de dados (`__in`);
* ordenação com `order_by`;
* lista de valores com `values_list(..., flat=True)`.

Em todos os exemplos vamos contar quantas consultas o Django fez no banco com `connection.queries`. Como referência, usamos o artigo do Lucas Magnum no PythonClub (link acima), *Como otimizar suas consultas no Django - De N a 1 em 20 minutos*, e a documentação da [QuerySet API](https://docs.djangoproject.com/en/4.1/ref/models/querysets/).

No fim da página há um complemento com o campo de busca, `get` × `filter` e `get_or_create`, que não aparece neste vídeo.

## Pré-requisitos

O projeto é o do repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django), com:

* as apps `backend.product` (models `Category` e `Product`) e `backend.bookstore` (models `Author` e `Book`);
* `django-extensions` (para o `shell_plus`) e `django-seed` (para gerar dados falsos) instalados e no `INSTALLED_APPS`;
* o Jupyter Notebook instalado no virtualenv, para usar o `shell_plus --notebook`.

```bash
pip install django-extensions==3.2.* django-seed==0.3.1 notebook
```

```python
# backend/settings.py
INSTALLED_APPS = [
    ...
    'django_extensions',
    'django_seed',
    ...
    'backend.bookstore',
    'backend.product',
]
```

## Os models

```python
# backend/product/models.py
from django.db import models
from django.urls import reverse_lazy

from backend.core.models import TimeStampedModel


class Category(models.Model):
    title = models.CharField('título', max_length=255, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return f'{self.title}'


class Product(models.Model):
    title = models.CharField('título', max_length=255, unique=True)
    description = models.TextField('descrição', null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='categoria',
        related_name='products',
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse_lazy('product:product_detail', kwargs={'pk': self.pk})
```

Repare no `related_name='products'` da ForeignKey: ele vai ser importante no relacionamento reverso.

```python
# backend/bookstore/models.py
class Author(models.Model):
    first_name = models.CharField('nome', max_length=100)
    last_name = models.CharField('sobrenome', max_length=255, null=True, blank=True)  # noqa E501

    class Meta:
        ordering = ('first_name',)
        verbose_name = 'autor'
        verbose_name_plural = 'autores'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name or ""}'.strip()

    def __str__(self):
        return self.full_name


class Book(models.Model):
    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField('título', max_length=255)
    rating = models.DecimalField('pontuação', max_digits=5, decimal_places=2, default=5)
    authors = models.ManyToManyField(
        Author,
        verbose_name='autores',
        blank=True
    )
    price = models.DecimalField('preço', max_digits=5, decimal_places=2)
    stock_min = models.PositiveSmallIntegerField(default=0)
    stock = models.PositiveSmallIntegerField(default=0)
    publisher = models.ForeignKey(
        'Publisher',
        on_delete=models.SET_NULL,
        verbose_name='editora',
        related_name='books',
        null=True,
        blank=True
    )
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
        ordering = ('title',)
        verbose_name = 'livro'
        verbose_name_plural = 'livros'

    def __str__(self):
        return f'{self.title}'
```

O campo `authors` de `Book` é um ManyToMany **sem** `related_name`.

## Preparando os dados

Gere 500 produtos e 500 registros da bookstore com o `django-seed`:

```bash
python manage.py seed product --number=500
python manage.py seed bookstore --number=500

python manage.py shell_plus
```

O `seed` cria categorias com nomes aleatórios. Para ter categorias conhecidas, no `shell_plus` apagamos as categorias, criamos uma lista fixa e sorteamos uma categoria para cada produto:

```python
from random import choice

categories = (
    'Acessórios de Moda',
    'Artigos de Ginástica e Esportes',
    'Artigos de Praia e Piscina',
    'Artigos para Presente',
    'Calçado Feminino',
    'Calçado Masculino',
    'Cama, Mesa e Banho',
    'Roupa Feminina',
    'Roupa Infantil',
    'Roupa Masculina',
)

# Deleta as categorias
Category.objects.all().delete()
# (500, {'product.Category': 500})

# Cria as categorias com list comprehension
[Category.objects.create(title=title) for title in categories]

categories = Category.objects.all()
products = Product.objects.all()

for product in products:
    # Escolhe uma catetoria
    category = choice(categories)
    product.category = category

# Aplica a categoria em todos os produtos
Product.objects.bulk_update(products, ['category'])
```

Como a ForeignKey é `on_delete=models.SET_NULL`, apagar as categorias não apaga os produtos; eles só ficam sem categoria até o `bulk_update`, que grava a coluna `category` de todos os produtos de uma vez. Na lista de produtos da aplicação, agora aparecem categorias como Roupa Feminina, Roupa Infantil, Artigos de Ginástica e Esportes etc.

## Usando o Jupyter Notebook com o shell_plus

Para os experimentos, em vez do terminal, usamos o Jupyter:

```bash
python manage.py shell_plus --notebook
```

No Jupyter, crie um notebook escolhendo o kernel **Django Shell-Plus** (no canto direito, em *New*). Ele já faz todos os imports dos models automaticamente, como o `shell_plus`.

Em cada exemplo abaixo, importamos `connection` e, no fim, olhamos `len(connection.queries)`, que é a quantidade de consultas SQL feitas até ali. Para zerar a contagem entre um exemplo e outro, reinicie o kernel (*Kernel > Restart & Run All*). A lista `connection.queries` só é preenchida com `DEBUG = True`.

## Relacionamento direto (ForeignKey)

Vamos iterar por todos os produtos e imprimir a categoria de cada um.

```python
from django.db import connection

products = Product.objects.all()

for product in products:
    print(product.category)

len(connection.queries)
# 501
```

Foram feitas **501** consultas: uma para buscar os produtos e mais uma para buscar a categoria de **cada** produto. É o famoso problema do N+1. Com 500 produtos já é ruim; imagine com 5.000 ou 10.000.

## select_related

Agora faça:

```python
from django.db import connection

products = Product.objects.select_related('category').all()

for product in products:
    print(product.category)

len(connection.queries)
# 1
```

Passamos para o `select_related` o **nome do campo** ForeignKey (`category`). Antes eram 501 consultas; agora é **uma**.

O objetivo do `select_related` é realizar uma única query que une todos os models relacionados. Ele faz isso através de um JOIN na instrução SQL, então realiza o cache do atributo para que possa acessá-lo sem realizar uma nova consulta. Só que ele não funciona para **ManyToMany**, e nem para **Relacionamento Reverso**.

## Relacionamento reverso

Por padrão o Django adiciona um relacionamento reverso quando sua tabela é referenciada por uma chave estrangeira.

Se não passar o parâmetro `related_name`, irá seguir o padrão `<nome_do_model>_set` (em minúsculas). No nosso caso, definimos `related_name='products'`:

```python
# backend/product/models.py
class Product(models.Model):
    ...
    category = models.ForeignKey(
        Category,
        ...
        related_name='products',
    )
```

Então, a partir de uma categoria, acessamos os produtos dela com `category.products`:

```python
from django.db import connection

categories = Category.objects.all()

for category in categories:
    print(category.products.all())

len(connection.queries)
# 12
```

Significa que a partir da categoria eu consigo acessar todos os produtos, cada um na sua respectiva categoria. Mas, de novo, foi uma consulta para as categorias e mais uma para os produtos de **cada** categoria (12 no vídeo).

## prefetch_related

Para o relacionamento reverso usamos o `prefetch_related`, passando o `related_name`:

```python
from django.db import connection

categories = Category.objects.prefetch_related('products').all()

for category in categories:
    print(category.products.all())

len(connection.queries)
# 2
```

Agora são só **duas** consultas: uma para as categorias e outra para todos os produtos dessas categorias; o Django junta os resultados em Python.

Resumindo: **`select_related`** é para relacionamento direto (ForeignKey e OneToOne); **`prefetch_related`** é para relacionamento reverso e para ManyToMany.

### Exemplo com ManyToMany

Considere o `Book` com o campo `authors` (ManyToMany para `Author`), mostrado na seção "Os models".

A partir do livro, vamos acessar todos os autores dele. Aqui usamos o nome do campo, `authors`, porque estamos partindo do model que tem o ManyToMany:

```python
from django.db import connection

books = Book.objects.prefetch_related('authors')

for book in books:
    print(book.authors.all())

len(connection.queries)
# 2
```

A partir do autor, vamos acessar todos os livros dele. Agora estamos no lado reverso do ManyToMany, e como o campo `authors` não tem `related_name`, o nome é o do model em minúsculas mais `_set`: `book_set`.

```python
from django.db import connection

authors = Author.objects.prefetch_related('book_set')

for author in authors:
    print(author.book_set.all())

len(connection.queries)
# 2
```

O segredo aqui é usar o `prefetch_related` com o `book_set`.

## Filtro direto

Liste os **produtos** cuja categoria seja *Roupa Masculina*. E retorne o título da categoria e o título do produto.

```python
from django.db import connection

category = Category.objects.get(title='Roupa Masculina')

# Bad
# products = Product.objects.filter(category=category)

# Good
products = Product.objects.select_related('category').filter(category=category)

for product in products:
    print(product.category.title, product.title)

len(connection.queries)
# 2
```

Saída (trecho):

```
Roupa Masculina Act me or always weight.
Roupa Masculina Affect law chair before next certain.
Roupa Masculina At sister some appear.
...
```

O jeito "Bad" funciona, mas faria uma consulta extra para cada `product.category.title`. Com o `select_related` foram apenas duas consultas: o `get` da categoria e a dos produtos.

Também dá para filtrar direto pelo título da categoria, usando **dois underlines** (`__`) para atravessar a ForeignKey. O resultado é o mesmo:

```python
# Ou
products = Product.objects.select_related('category').filter(category__title='Roupa Masculina')
```

## Filtro reverso

Retorne todas as categorias, e a partir de cada categoria retorne todos os produtos desta categoria.

```python
from django.db import connection

categories = Category.objects.prefetch_related('products').all()

for category in categories:
    print(category.title, category.products.all(), '\n')
    # print(category.product_set.all())  # Caso você não tivesse definido o related_name.

print(len(connection.queries))
# 2
```

Saída (trecho):

```
Acessórios de Moda <QuerySet [<Product: Agency serious tend all out.>, <Product: Attorney person worry deal fill.>, ...]>

Artigos de Ginástica e Esportes <QuerySet [<Product: Across possible focus network forget.>, ...]>
...
```

Se a ForeignKey não tivesse `related_name`, o acesso reverso seria `category.product_set.all()` e o prefetch, `prefetch_related('product_set')`.

## Filtrando a partir de uma lista de dados

Para filtrar a partir de uma lista de dados usamos o lookup `__in`.

**Exemplo:**

Dada a lista de categorias

```python
categories = ['Roupa Feminina', 'Roupa Masculina']
```

Filtre todos os produtos dessas categorias.

Então, façamos

```python
products = Product.objects.filter(category__title__in=categories)
products.count()
# 111
products
```

`category__title__in` quer dizer: o `title` da `category` está **dentro** da lista. No vídeo vieram 111 produtos (o número muda a cada `seed`, porque as categorias foram sorteadas).

## Ordenando os itens

Para ordenar os itens da query usamos `order_by()`.

```python
Product.objects.all().order_by('title')  # ordem crescente
Product.objects.all().order_by('-title')  # ordem decrescente
```

Com `title`, a lista começa por "About...", "Accept..."; com `-title` (sinal de menos), começa pelo fim do alfabeto: "Yes...", "Worry...".

Para ordenar por data de criação, o `Product` precisa de um campo `created`. No vídeo ele não tinha, e `order_by('created')` deu erro. Então trocamos a herança de `models.Model` para o `TimeStampedModel`, que acrescenta `created` e `modified`:

```python
# backend/core/models.py
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
```

```python
# backend/product/models.py
class Product(TimeStampedModel):
    ...
```

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed product --number=500
```

Como o campo `created` tem `auto_now_add=True`, o `makemigrations` pede um valor padrão para os produtos que já existem; aceite o `timezone.now` sugerido. A migração gerada foi esta:

```python
# backend/product/migrations/0002_product_created_product_modified.py
# Generated by Django 4.1.3 on 2023-02-19 10:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='criado em'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='modified',
            field=models.DateTimeField(auto_now=True, verbose_name='modificado em'),
        ),
    ]
```

Depois do novo `seed`, os produtos antigos ficaram com a data da migração e os novos com datas aleatórias geradas pelo django-seed (a partir de 1970). Usando `.values('created')` para ver só as datas:

```python
Product.objects.all().order_by('created').values('created')  # mais antigo primeiro
# <QuerySet [{'created': datetime.datetime(1970, 4, 14, 14, 8, 2, tzinfo=datetime.timezone.utc)}, ...]>

Product.objects.all().order_by('-created').values('created')  # mais recente primeiro
# <QuerySet [{'created': datetime.datetime(2023, 2, 19, 10, 21, 13, 319402, tzinfo=datetime.timezone.utc)}, ...]>
```

Resumindo:

```python
Product.objects.all().order_by('title')  # ordem crescente
Product.objects.all().order_by('-title')  # ordem decrescente
Product.objects.all().order_by('created')  # mais antigo primeiro
Product.objects.all().order_by('-created')  # mais recente primeiro
```

## Retornando uma lista de registros

O `values_list` devolve tuplas:

```python
Product.objects.all().values_list('id')
# <QuerySet [(1118,), (1470,), (1006,), (1433,), (709,), ...]>
```

Para ter uma lista simples de valores, usamos o `flat=True`:

```python
Product.objects.all().values_list('id', flat=True)
# <QuerySet [1118, 1470, 1006, 1433, 709, ...]>
```

O `flat=True` só funciona quando você pede **um** campo. Funciona com qualquer campo, por exemplo `values_list('title', flat=True)` devolve a lista de títulos.

Os ids não estão em ordem porque o `Meta.ordering` do `Product` é por `title`.

## Complemento: campo de busca no Django

Esta parte não aparece no vídeo; ela completa a dica com o campo de busca da lista de produtos.

### O operador `AND`

Para usar o `AND` basta separar os parâmetros do filtro com vírgula.

```python
products = Product.objects.filter(title__icontains='camera', category__title__icontains='feminina')
products.count()
products
```

### O operador `OR` com `Q()`

Para usar o `OR` vamos precisar do `Q()`.

```python
from django.db.models import Q

search = 'camera'

# depois com
# search = 'artigos'

products = Product.objects.filter(
    Q(title__icontains=search)
    | Q(description__icontains=search)
    | Q(category__title__icontains=search)
)
products.count()
products
```

### Diferença entre `get` e `filter`

O `get` retorna **um objeto**.

```python
category = Category.objects.get(title='Roupa Masculina')
type(category)
category
category.title
```

O `filter` retorna **um QuerySet** (uma "lista" de objetos).

```python
categories = Category.objects.filter(title__icontains='Roupa')
type(categories)
categories
```

#### Tratando o erro DoesNotExist

```python
try:
    category = Category.objects.get(title='Roupa')
except Category.DoesNotExist:
    print('Item não existe')
```

#### Evitando o erro DoesNotExist

```python
category = Category.objects.filter(title='Roupa')
category
# <QuerySet []>
```

Retorna um QuerySet vazio.

Você também pode experimentar

```python
category = Category.objects.filter(title='Roupa Masculina').first()  # retorna um objeto
category = Category.objects.filter(title='Roupa').first()  # retorna None
```

### get_or_create

[https://docs.djangoproject.com/en/4.1/ref/models/querysets/#get-or-create](https://docs.djangoproject.com/en/4.1/ref/models/querysets/#get-or-create)

```python
obj, created = Category.objects.get_or_create(title='Eletrônicos')
```

Na primeira vez teremos `created=True` (a categoria foi criada). Na segunda teremos `created=False` (a categoria já existia e foi só buscada).

### Criando o campo de busca

Edite `product/views.py`

```python
# backend/product/views.py
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Product


def product_list(request):
    template_name = 'product/product_list.html'
    object_list = Product.objects.all()

    search = request.GET.get('search')

    if search:
        object_list = object_list.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(category__title__icontains=search)
        )

    context = {'object_list': object_list}
    return render(request, template_name, context)
```

A busca vem pela query string (`?search=...`), e o filtro procura o termo no título, na descrição ou no título da categoria.

O template `product_list.html` já inclui o formulário de busca com `{% include "./includes/search.html" %}`. O campo se chama `search` e o formulário usa `GET`. Nele acrescentamos o botão **Limpar**, um link para `.`, que volta à lista sem filtro:

```html
<!-- backend/product/templates/product/includes/search.html -->
<div class="hidden sm:flex items-center sm:divide-x sm:divide-gray-100 mb-3 sm:mb-0">
  <form class="lg:pr-3" action="#" method="GET">
    <label for="users-search" class="sr-only">Busca</label>
    <div class="mt-1 relative lg:w-64 xl:w-96">
      <input id="id_search" name="search" type="text" class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5" placeholder="Busca...">
    </div>
  </form>
  <div class="flex space-x-1 pl-0 sm:pl-2 mt-3 sm:mt-0">
    <a href="." class="w-1/2 text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center sm:w-auto">
      Limpar
    </a>
    ...
  </div>
</div>
```

O `...` são os botões de ícones que já existiam no layout.

Com isso você tem os principais segredos para consultas eficientes: `select_related` no relacionamento direto, `prefetch_related` no reverso e no ManyToMany, `__` para atravessar relacionamentos, `__in` para listas, `order_by` e `values_list(..., flat=True)`.
