# Dica 29 - Importando CSV

VIDEO EM BREVE.

## Criando um novo comando no Django

```
python manage.py create_command core -n import_data
```

```python
# backend/core/management/commands/import_data.py
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('sample', nargs='+')

    def handle(self, *args, **options):
        raise NotImplementedError()

```

## Importando CSV pelo shell do Django

Vamos acrescentar o campo `price` em `product`.

```python
# product/models.py

class Product(TimeStampedModel):
    ...
    price = models.DecimalField('preço', max_digits=9, decimal_places=2, null=True, blank=True)

```

```
python manage.py makemigrations
python manage.py migrate
```

Digite

```
python manage.py shell_plus
```

```python
import csv

from backend.product.models import Product


def csv_to_list(filename: str) -> list:
    '''
    Lê um csv e retorna um OrderedDict.
    '''
    with open(filename) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        csv_data = [line for line in reader]
    return csv_data

data = csv_to_list('/tmp/products.csv')

data

[{'title': 'Pizza 03f6be37', 'price': '10.16'},
 {'title': 'Pizza fced66c2', 'price': '52.8'},
 {'title': 'Gently Used Shoes 7e7b5f9f', 'price': '72.97'},
 {'title': 'Fish 57f5b41a', 'price': '33.1'},
 {'title': 'Cheese 5355253b', 'price': '66.99'},
 ...
]

def save_data(data):
    '''
    Salva os dados no banco.
    '''
    aux = []
    for item in data:
        title = item.get('title')
        price = item.get('price')
        obj = Product(
            title=title,
            price=price,
        )
        aux.append(obj)
    Product.objects.bulk_create(aux)


save_data(data)

```

## Importando CSV com o novo comando import_data

```python
# backend/core/management/commands/import_data.py
from django.core.management.base import BaseCommand


def import_csv(filename):
    print(filename)


class Command(BaseCommand):
    help = 'Importa dados de um CSV.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename_csv',
            '-fcsv',
            dest='filename_csv',
            help='Importa arquivo CSV.'
        )

    def handle(self, *args, **options):
        filename = options['filename_csv']
        import_csv(filename)

```

```
python manage.py import_data --help

python manage.py import_data --filename_csv '/tmp/products.csv'
```

Continuando

```python
import csv
import sys

from django.core.management.base import BaseCommand

from backend.product.models import Product


def csv_to_list(filename: str) -> list:
    '''
    Lê um csv e retorna um OrderedDict.
    '''
    with open(filename) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        csv_data = [line for line in reader]
    return csv_data


def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)

    def show(j):
        x = int(size * j / count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#" * x, "." * (size - x), j, count))  # noqa E501
        file.flush()
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i + 1)
    file.write("\n")
    file.flush()


def save_data(data):
    '''
    Salva os dados no banco.
    '''
    aux = []
    for item in progressbar(data, 'Importando dados'):
        title = item.get('title')
        price = item.get('price')
        obj = Product(
            title=title,
            price=price,
        )
        aux.append(obj)
    Product.objects.bulk_create(aux)


def import_csv(filename):
    data = csv_to_list(filename)
    save_data(data)


class Command(BaseCommand):
    help = 'Importa dados de um CSV.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename_csv',
            '-fcsv',
            dest='filename_csv',
            help='Importa arquivo CSV.'
        )

    def handle(self, *args, **options):
        filename_csv = options['filename_csv']

        Product.objects.all().delete()
        import_csv(filename_csv)

```

```
python manage.py import_data -fcsv '/tmp/products.csv'
```

Simulando o progressbar um pouco mais lento.

```python
from time import sleep


def save_data(data, slow_motion=None):
    '''
    Salva os dados no banco.
    '''
    aux = []
    for item in progressbar(data, 'Importando dados'):
        title = item.get('title')
        price = item.get('price')
        obj = Product(
            title=title,
            price=price,
        )
        if slow_motion:  # <---
            obj.save()
            sleep(.02)
        else:
            aux.append(obj)

    if not slow_motion:  # <---
        Product.objects.bulk_create(aux)


def import_csv(filename, slow_motion=None):  # <---
    data = csv_to_list(filename)
    save_data(data, slow_motion)  # <---


class Command(BaseCommand):
    help = 'Importa dados de um CSV.'

    def add_arguments(self, parser):
        ...
        parser.add_argument(
            '--slow_motion',
            '-slow',
            action='store_true',
            help='Simula camera lenta.'
        )

    def handle(self, *args, **options):
        filename_csv = options['filename_csv']
        slow_motion = options['slow_motion']  # <---

        Product.objects.all().delete()
        import_csv(filename_csv, slow_motion)  # <---

```

```
python manage.py import_data -fcsv '/tmp/products.csv' -slow
```
