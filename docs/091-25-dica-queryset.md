# Dica 25 - Criando Filtros poderosos no Django - Segredos do ORM

http://pythonclub.com.br/django-introducao-queries.html

https://docs.djangoproject.com/en/4.1/ref/models/querysets/

## Preparando os dados

```
python manage.py seed product --number=500
python manage.py seed bookstore --number=500

python manage.py shell_plus
```

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



## Relacionamento OneToOne e ForeignKey

Considere o models de `Product` e `Category`.

```python
# product/models.py
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
```

Vamos iterar por todos os produtos. E imprimir o nome da categoria.

```python
from django.db import connection

products = Product.objects.all()

for product in products:
    print(product.category)

print(len(connection.queries))
# 500
```

Note que foram feitas 500 consultas no banco de dados. E isso torna a nossa query lenta.

## select_related

Agora faça

```python
from django.db import connection

products = Product.objects.select_related('category').all()

for product in products:
    print(product.category)

print(len(connection.queries))
# 1
```

O objetivo do `select_related` é realizar uma única query que une todos os models relacionados. Ele faz isso através de um JOIN na instrução SQL, então realiza o cache do atributo para que possa acessá-lo sem realizar uma nova consulta. Só que ele não funciona para **ManyToMany**, e nem para **Relacionamento Reverso**.


## Relacionamento Reverso

Por padrão o Django adiciona um relacionamento reverso quando sua tabela é referenciada por uma chave estrangeira.

Se não passar o parâmetro `related_name`, irá seguir o padrão `<nome_tabela>_set`.

```python
class Product(models.Model):
    ...
    category = models.ForeignKey(
        Category,
        ...
        related_name='products',
    )
```

```python
categories = Category.objects.all()

for category in categories:
    print(category.products.all())

len(connection.queries)
# 12
```

Significa que a partir da categoria eu consigo acessar todos os produtos.


## prefetch_related

```python
categories = Category.objects.prefetch_related('products').all()

for category in categories:
    print(category.products.all())

len(connection.queries)
# 2
```

### Exemplo com ManyToMany

Considere o `bookstore/models.py`

```python
class Author(models.Model):
    first_name = models.CharField('nome', max_length=100)
    last_name = models.CharField('sobrenome', max_length=255, null=True, blank=True)  # noqa E501

class Book(models.Model):
    title = models.CharField('título', max_length=255)
    authors = models.ManyToManyField(
        Author,
        verbose_name='autores',
        blank=True
    )
    ...
```

A partir do Livro, vamos acessar todos os autores dele.

```python
from django.db import connection

books = Book.objects.prefetch_related('authors')

for book in books:
    print(book.authors.all())

len(connection.queries)
# 2
```

A partir do Autor, vamos acessar todos os livros dele.

```python
from django.db import connection

authors = Author.objects.prefetch_related('book_set')

for author in authors:
    print(author.book_set.all())

len(connection.queries)
# 2
```


## Filtro Direto

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

print(len(connection.queries))

# Ou
products = Product.objects.select_related('category').filter(category__title='Roupa Masculina')
```



## Filtro Reverso

Retorne todas as categorias, e a partir de cada categoria retorne todos os produtos desta categoria.

```python
from django.db import connection

categories = Category.objects.prefetch_related('products').all()

for category in categories:
    print(category.title, category.products.all(), '\n')
    # print(category.category_set.all())  # Caso você não tivesse definido o related_name.

print(len(connection.queries))
```


# Filtrando a partir de uma lista de dados

Para filtrar a partir de uma lista de dados usamos o subcomando `__in`.

**Exemplo:**

Dada a lista de categorias

```python
categories = ['Roupa Feminina', 'Roupa Masculina']
```

Filtre todas as roupas dessas categorias.

Então, façamos

```python
products = Product.objects.filter(category__title__in=categories)
products.count()
products
```


# Ordenando os items

Para ordenar os items da query usamos `order_by()`.

**Exemplo:**

```python
Product.objects.all().order_by('title')  # ordem crescente
Product.objects.all().order_by('-title')  # ordem decrescente
Product.objects.all().order_by('created')  # mais antigo primeiro
Product.objects.all().order_by('-created')  # mais recente primeiro
```


# Retornando uma lista de registros

Para retornar uma lista de registros usamos o `flat = True`.

**Exemplo:**

```python
Product.objects.all().values_list('id', flat=True)
```

# Campo de Busca no Django

## O Operador `AND`

Para usar o `AND` basta separar os parâmetros do filtro com vírgula.

```python
products = Product.objects.filter(title__icontains='camera', category__title__icontains='feminina')
products.count()
products
```

## O Operador `OR`

### Método `Q()`

Para usar o `OR` vamos precisar do método `Q()`.

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

## Diferença entre `get` e `filter`.

O `get` retorna **um objeto**.

```python
category = Category.objects.get(title='Roupa Masculina')
type(category)
category
category.title
```

O `filter` retorna **uma lista**.

```python
categories = Category.objects.filter(title__icontains='Roupa')
type(categories)
categories
```

### Tratando o erro DoesNotExists

```python
try:
    category = Category.objects.get(title='Roupa')
except Category.DoesNotExist:
    print('Item não existe')
```

### Evitando o erro DoesNotExists

```python
category = Category.objects.filter(title='Roupa')
category
```

Retorna um QuerySet vazio.

Você também pode experimentar

```python
category = Category.objects.filter(title='Roupa Masculina').first()  # retorna um objeto
category = Category.objects.filter(title='Roupa').first()  # retorna None
```


## get_or_create

https://docs.djangoproject.com/en/4.1/ref/models/querysets/#get-or-create

```python
obj, created = Category.objects.get_or_create(title='Eletrônicos')
```

Na primeira teremos `created=True`. Na segunda teremos `created=False`.


# Criando o campo de busca

Edite `product/views.py`

```python
from django.db.models import Q

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

Edite `product/templates/product/includes/search.html`

```html
<div class="flex space-x-1 pl-0 sm:pl-2 mt-3 sm:mt-0">
    <a href="." class="w-1/2 text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center sm:w-auto">
      Limpar
    </a>
```
