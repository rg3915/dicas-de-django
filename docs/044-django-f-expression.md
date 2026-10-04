# Dica 44 - Django: F() expression

**Versões usadas no vídeo:** Django 3.2.6, Python 3.9.6, django-extensions 2.2.9 e django-seed 0.2.2.
{: .versoes }

<a href="https://youtu.be/YDCeA3rNcno">
    <img src="../.gitbook/assets/youtube.png">
</a>

Doc: [https://docs.djangoproject.com/en/3.2/ref/models/expressions/#f-expressions](https://docs.djangoproject.com/en/3.2/ref/models/expressions/#f-expressions)

Lista de produtos usada no exemplo: [https://gist.github.com/rg3915/3958acf4242ecae6508622d0a8164a42](https://gist.github.com/rg3915/3958acf4242ecae6508622d0a8164a42)

O [F() expression](https://docs.djangoproject.com/en/3.2/ref/models/expressions/#f-expressions) é uma expressão que retorna a representação do valor do campo, ou seja, é o valor do campo propriamente dito.

Com o `F()` dá para comparar um campo com **outro campo do mesmo registro**, fazer contas entre campos e seguir relacionamentos, tudo **dentro do banco de dados**, numa única query, sem trazer os registros para a memória do Python.

Neste tutorial vamos criar três apps, cada uma com um exemplo:

* `event`: salas de eventos, comparando a quantidade de participantes com a quantidade de cadeiras;
* `product`: produtos, calculando quantos dias faltam entre a data de fabricação e a de vencimento;
* `ecommerce`: itens de uma ordem de compra, calculando o subtotal (preço do produto vezes a quantidade).

## Pré-requisitos

O vídeo usa o projeto do repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django) (pasta `myproject`), já atualizado para o Django 3.2 na [Dica 43](043-django-admin-rangefilter.md). Usamos também:

* o `shell_plus` do [django-extensions](002-django-extensions.md), que já importa os models e o `F` automaticamente;
* o [django-seed](041-django-seed.md), para gerar dados aleatórios no último exemplo;
* o model abstrato `TimeStampedModel`, criado em `myproject/core/models.py` na Dica 43:

```python
# myproject/core/models.py (trecho)
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

## Criando as apps

As apps ficam dentro da pasta `myproject`, então entramos nela e chamamos o `manage.py` da pasta de cima:

```bash
cd myproject
python ../manage.py startapp event
python ../manage.py startapp product
python ../manage.py startapp ecommerce
cd ..
```

Como as apps estão dentro de `myproject`, o `name` de cada `AppConfig` precisa do caminho completo. Sem isso, o `makemigrations` dá o erro:

```
django.core.exceptions.ImproperlyConfigured: Cannot import 'event'. Check that 'myproject.event.apps.EventConfig.name' is correct.
```

Edite `event/apps.py`

```python
# myproject/event/apps.py
from django.apps import AppConfig


class EventConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myproject.event'
```

Edite `product/apps.py`

```python
# myproject/product/apps.py
from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myproject.product'
```

Edite `ecommerce/apps.py`

```python
# myproject/ecommerce/apps.py
from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myproject.ecommerce'
```

E registre as três em `settings.py` (no vídeo elas foram entrando uma de cada vez, conforme cada exemplo):

```python
# myproject/settings.py
INSTALLED_APPS = [
    'myproject.core',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd partys
    'debug_toolbar',
    'django_extensions',
    'rangefilter',
    'django_filters',
    'django_seed',
    # my apps
    'myproject.travel',
    'myproject.ecommerce',
    'myproject.event',
    'myproject.product',
]
```

## Exemplo 1: salas de eventos

### O model

Cada sala tem um nome, uma quantidade de participantes e uma quantidade de cadeiras.

Edite `event/models.py`

```python
# myproject/event/models.py
from django.db import models


class Room(models.Model):
    name = models.CharField('nome', max_length=100, unique=True)
    num_participants = models.PositiveSmallIntegerField('quantidade de participantes')  # noqa E501
    num_chairs = models.PositiveSmallIntegerField('quantidade de cadeiras')

    class Meta:
        ordering = ('name',)
        verbose_name = 'sala'
        verbose_name_plural = 'salas'

    def __str__(self):
        return self.name
```

Edite `event/admin.py`

```python
# myproject/event/admin.py
from django.contrib import admin

from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_participants', 'num_chairs')
    search_fields = ('name',)
```

Rode as migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Usando o F() no shell

Rode

```bash
python manage.py shell_plus
```

O `shell_plus` já importa os models (`Room`) e o `F` (`from django.db.models import ... F ...`), por isso não precisamos importar nada. Se você usar o `shell` normal, faça `from django.db.models import F` e `from myproject.event.models import Room`.

Primeiro, cadastre algumas salas:

```python
# Room.objects.all().delete()
rooms = [
    ('Evento 1', 500, 400),
    ('Evento 2', 500, 550),
    ('Evento 3', 600, 500),
    ('Evento 4', 680, 700),
    ('Evento 5', 1000, 990),
    ('Evento 6', 1200, 500),
    ('Evento 7', 1000, 450),
]

for room in rooms:
    Room.objects.create(name=room[0], num_participants=room[1], num_chairs=room[2])
```

**Filtrar comparando dois campos.** Queremos as salas em que há mais participantes do que cadeiras. Sem o `F()`, o lado direito do filtro teria que ser um número fixo. Com o `F('num_chairs')`, comparamos com o valor do campo `num_chairs` de cada registro:

```python
# Filtra as salas cuja quantidade de participantes seja maior que a quantidade de cadeiras.
rooms = Room.objects.filter(num_participants__gt=F('num_chairs'))

for room in rooms:
    print(room.num_participants, room.num_chairs, room.num_participants - room.num_chairs)
```

Saída:

```
500 400 100
600 500 100
1000 990 10
1200 500 700
1000 450 550
```

Os eventos 2 e 4, que têm mais cadeiras do que participantes, ficaram de fora.

**Calcular no banco com annotate.** No exemplo acima a diferença foi calculada no Python, dentro do `print`. Com `annotate`, o próprio banco calcula a diferença e devolve num atributo novo, `difference`:

```python
# Calcula a diferença entre participantes e cadeiras.
rooms = Room.objects.annotate(difference=F('num_participants') - F('num_chairs')).filter(num_participants__gt=F('num_chairs'))

for room in rooms:
    print(room.num_participants, room.num_chairs, room.difference)
```

Saída (a mesma de antes, agora vinda do banco):

```
500 400 100
600 500 100
1000 990 10
1200 500 700
1000 450 550
```

**Fazer contas dentro do filtro.** O `F()` aceita operações aritméticas. Salas em que há mais participantes do que o **dobro** de cadeiras:

```python
# Filtra as salas cuja quantidade de participantes seja maior que o dobro da quantidade de cadeiras.
rooms = Room.objects.filter(num_participants__gt=F('num_chairs') * 2)

for room in rooms:
    print(room.num_participants, room.num_chairs, room.num_chairs * 2)
```

Saída:

```
1200 500 1000
1000 450 900
```

Mesmo com o dobro de cadeiras, a quantidade de participantes ainda é maior. Se quiser ver o SQL gerado, rode `print(rooms.query)`: a conta é feita no `WHERE`, no próprio banco.

```sql
SELECT "event_room"."id", "event_room"."name", "event_room"."num_participants", "event_room"."num_chairs" FROM "event_room" WHERE "event_room"."num_participants" > ("event_room"."num_chairs" * 2) ORDER BY "event_room"."name" ASC
```

## Exemplo 2: produtos e datas

### O model

Edite `product/models.py`

```python
# myproject/product/models.py
from django.db import models


class Product(models.Model):
    title = models.CharField('título', max_length=100, unique=True)
    price = models.DecimalField('preço', max_digits=7, decimal_places=2)
    manufacturing_date = models.DateField('data de fabricação', null=True, blank=True)  # noqa E501
    due_date = models.DateField('data de vencimento', null=True, blank=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        return self.title
```

Edite `product/admin.py`

```python
# myproject/product/admin.py
from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'manufacturing_date', 'due_date')
    search_fields = ('title',)
```

```bash
python manage.py makemigrations
python manage.py migrate
```

### Usando o F() com datas

Rode

```bash
python manage.py shell_plus
```

Cole a lista de produtos (a mesma do [gist](https://gist.github.com/rg3915/3958acf4242ecae6508622d0a8164a42)) e cadastre tudo de uma vez com `bulk_create`:

```python
products = [
    {
        'title': 'queijo fresco',
        'price': '8.99',
        'manufacturing_date': '2021-08-01',
        'due_date': '2021-08-03',
    },
    {
        'title': 'sorvete de manga',
        'price': '12',
        'manufacturing_date': '2021-08-10',
        'due_date': '2021-10-10',
    },
    {
        'title': 'leite integral',
        'price': '5.12',
        'manufacturing_date': '2021-08-02',
        'due_date': '2021-08-06',
    },
    {
        'title': 'pão de forma',
        'price': '7.45',
        'manufacturing_date': '2021-08-01',
        'due_date': '2021-08-06',
    },
]

Product.objects.all().delete()
aux_list = []
for item in products:
    obj = Product(
        title=item['title'],
        price=item['price'],
        manufacturing_date=item['manufacturing_date'],
        due_date=item['due_date'],
    )
    aux_list.append(obj)

Product.objects.bulk_create(aux_list)
```

Saída:

```
[<Product: queijo fresco>, <Product: sorvete de manga>, <Product: leite integral>, <Product: pão de forma>]
```

A subtração de dois campos de data (`F('due_date') - F('manufacturing_date')`) resulta numa duração, que comparamos com um `timedelta`:

```python
from datetime import timedelta

# Retorna os produtos cuja data de validade seja inferior a 5 dias.
Product.objects.annotate(expiration_days=F('due_date') - F('manufacturing_date')).filter(expiration_days__lt=timedelta(days=5))
```

Saída:

```
<QuerySet [<Product: leite integral>, <Product: queijo fresco>]>
```

Para conferir, calcule a validade de todos os produtos no Python:

```python
products = Product.objects.all()

for product in products:
    print(product.title, (product.due_date - product.manufacturing_date).days)
```

Saída:

```
leite integral 4
pão de forma 5
queijo fresco 2
sorvete de manga 61
```

Só o leite integral (4 dias) e o queijo fresco (2 dias) têm validade menor que 5 dias. O pão de forma tem exatamente 5, então não entra no `__lt`.

## Exemplo 3: ordem de compra e subtotal

### Os models

Uma ordem de compra (`Order`) tem uma nota fiscal e vários itens (`OrderItems`). Cada item aponta para um produto e tem quantidade e preço. A `Order` herda do `TimeStampedModel` do app `core`.

Edite `ecommerce/models.py`

```python
# myproject/ecommerce/models.py
from django.db import models

from myproject.core.models import TimeStampedModel
from myproject.product.models import Product


class Order(TimeStampedModel):
    nf = models.CharField('nota fiscal', max_length=100, unique=True)

    class Meta:
        ordering = ('nf',)
        verbose_name = 'ordem de compra'
        verbose_name_plural = 'ordens de compra'

    def __str__(self):
        return self.nf


class OrderItems(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        verbose_name='ordem',
        related_name='order_items',
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        verbose_name='produto',
        related_name='product_items',
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField('quantidade')
    price = models.DecimalField('preço', max_digits=7, decimal_places=2)

    class Meta:
        ordering = ('pk',)

    def __str__(self):
        return f'{self.pk} - {self.order.pk} - {self.product}'
```

Edite `ecommerce/admin.py`

```python
# myproject/ecommerce/admin.py
from django.contrib import admin

from .models import Order, OrderItems

admin.site.register(Order)


@admin.register(OrderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'quantity', 'price')
```

```bash
python manage.py makemigrations
python manage.py migrate
```

Saída:

```
Migrations for 'ecommerce':
  myproject/ecommerce/migrations/0001_initial.py
    - Create model Order
    - Create model OrderItems
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, core, ecommerce, event, product, sessions, travel
Running migrations:
  Applying ecommerce.0001_initial... OK
```

### Gerando dados com o django-seed

Para não cadastrar ordens e itens na mão, use o `seed` do django-seed para inserir 10 registros aleatórios em cada model dos apps `product` e `ecommerce`:

```bash
python manage.py seed product ecommerce --number=10
```

### Usando o F() através de um relacionamento

Depois abra o shell_plus

```bash
python manage.py shell_plus
```

O `F()` também segue relacionamentos com `__`, como nos filtros. Aqui multiplicamos o preço do **produto** (`product__price`, campo de outra tabela) pela quantidade do **item**:

```python
# Retorna o subtotal do preço vezes a quantidade de cada produto.
items = OrderItems.objects.annotate(subtotal=F('product__price') * F('quantity'))

for item in items:
    print(f'{item.quantity}\t{item.product.price}\t{round(item.subtotal, 2)}')
```

Saída no vídeo (os seus números serão outros, porque o seed gera valores aleatórios):

```
24672   0.40    9868.80
32680   0.40    13072.00
20056   0.93    18652.08
11172   0.40    4468.80
8659    0.51    4416.09
2038    0.69    1406.22
13334   0.40    5333.60
27997   0.26    7279.22
19788   0.69    13653.72
26599   0.20    5319.80
```

Conferindo a primeira linha: 24672 × 0,40 = 9868,80. O cálculo foi feito pelo banco, com um `JOIN` na tabela de produtos, numa única query.

Esse é o exemplo mais clássico de uso do `F()`: calcular valores a partir de campos, inclusive de tabelas relacionadas, sem trazer os dados para o Python.
