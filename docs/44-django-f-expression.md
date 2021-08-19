# 44 - Django: F() expression

O (F() expression)[https://docs.djangoproject.com/en/3.2/ref/models/expressions/#f-expressions] é uma expressão que retorna a representação do valor do campo, ou seja, é o valor do campo propriamente dito.

Vamos criar 3 novas apps:

```
cd myproject
python ../manage.py event
python ../manage.py product
python ../manage.py ecommerce
```

Edite `event/apps.py`

```python
from django.apps import AppConfig


class EventConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myproject.event'
```

Edite `event/models.py`

```python
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
from django.contrib import admin

from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_participants', 'num_chairs')
    search_fields = ('name',)
```

Rode

```
python manage.py shell_plus
```

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



# Filtra as salas cuja quantidade de participantes seja maior que a quantidade de cadeiras.
rooms = Room.objects.filter(num_participants__gt=F('num_chairs'))

for room in rooms:
    print(room.num_participants, room.num_chairs, room.num_participants - room.num_chairs)

# Calcula a diferença entre participantes e cadeiras.
rooms = Room.objects.annotate(difference=F('num_participants') - F('num_chairs')).filter(num_participants__gt=F('num_chairs'))

for room in rooms:
    print(room.num_participants, room.num_chairs, room.difference)


# Filtra as salas cuja quantidade de participantes seja maior que o dobro da quantidade de cadeiras.
rooms = Room.objects.filter(num_participants__gt=F('num_chairs') * 2)

for room in rooms:
    print(room.num_participants, room.num_chairs, room.num_chairs * 2)
```


Edite `product/apps.py`

```python
from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myproject.product'
```


Edite `product/models.py`

```python
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
from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'manufacturing_date', 'due_date')
    search_fields = ('title',)
```

Rode

```
python manage.py shell_plus
```

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


from datetime import timedelta

# Retorna os produtos cuja data de validade seja inferior a 5 dias.
Product.objects.annotate(expiration_days=F('due_date') - F('manufacturing_date')).filter(expiration_days__lt=timedelta(days=5))

products = Product.objects.all()

for product in products:
    print(product.title, (product.due_date - product.manufacturing_date).days)
```


Edite `ecommerce/apps.py`

```python
from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myproject.ecommerce'
```


Edite `ecommerce/models.py`

```python
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
from django.contrib import admin

from .models import Order, OrderItems

admin.site.register(Order)


@admin.register(OrderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'quantity', 'price')
```

Rode

```
python manage.py seed product ecommerce --number=10
```

Depois abra o shell_plus

```
python manage.py shell_plus
```


```python
# Retorna o subtotal do preço vezes a quantidade de cada produto.
items = OrderItems.objects.annotate(subtotal=F('product__price') * F('quantity'))

for item in items:
    print(f'{item.quantity}\t{item.product.price}\t{round(item.subtotal, 2)}')
```
