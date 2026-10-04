# Dica 29 - Importando CSV

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10 e django-extensions 3.2.
{: .versoes }

<a href="https://youtu.be/jHCK_izrQa0">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

Nesta dica vamos importar para o banco os produtos do arquivo `/tmp/products.csv`, gerado na [Dica 28 - Gerando dados aleatórios com Faker](094-28-faker-commerce.md). Faremos isso de duas formas:

1. pelo shell do Django (`shell_plus`);
2. com um **comando de gerenciamento** próprio, `import_data`, com barra de progresso e uma opção de "câmera lenta".

O CSV tem duas colunas, `title` e `price`:

```
title,price
Table 95d9d2f9,99.73
Gloves 511bae99,89.01
...
```

## Pré-requisitos

* O projeto do repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django), com a app `backend.product` e o model `Product`.
* O `django-extensions` instalado e no `INSTALLED_APPS` (para os comandos `create_command` e `shell_plus`).
* O arquivo `/tmp/products.csv` da Dica 28.

## Criando um novo comando no Django

O `django-extensions` tem o comando `create_command`, que cria a estrutura de pastas e um arquivo de comando inicial. Vamos criar o comando `import_data` na app `core`:

```bash
python manage.py create_command core -n import_data
```

Ele cria as pastas `management/commands` (com os `__init__.py`) e o arquivo:

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

Todo comando é uma classe `Command` que herda de `BaseCommand`, com:

* `help`: a descrição que aparece no `--help`;
* `add_arguments`: onde declaramos os argumentos do comando (usa o `argparse` do Python);
* `handle`: o que o comando executa.

Vamos voltar a ele daqui a pouco.

## O campo price no Product

Vamos acrescentar o campo `price` em `Product`.

```python
# backend/product/models.py
class Product(TimeStampedModel):
    title = models.CharField('título', max_length=255, unique=True)
    description = models.TextField('descrição', null=True, blank=True)
    price = models.DecimalField('preço', max_digits=9, decimal_places=2, null=True, blank=True)
    ...
```

```bash
python manage.py makemigrations
python manage.py migrate
```

Saída do `makemigrations` no vídeo. Ela inclui também o campo `slug` da [Dica 27 - Signals](093-27-signals.md), cuja migração ainda não tinha sido criada:

```
Migrations for 'product':
  backend/product/migrations/0003_product_price_product_slug.py
    - Add field price to product
    - Add field slug to product
```

## Importando CSV pelo shell do Django

Digite

```bash
python manage.py shell_plus
```

O `shell_plus` já importa os models do projeto, inclusive o `Product`. Primeiro, uma função que lê o CSV e devolve uma lista de dicionários:

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
```

O `csv.DictReader` usa a primeira linha do arquivo (o cabeçalho) como chaves; cada linha vira um dicionário `{'title': ..., 'price': ...}`. A *list comprehension* junta todas as linhas numa lista.

```python
data = csv_to_list('/tmp/products.csv')

data

[...
 {'title': 'Concrete Towels 83dd6d58', 'price': '39.8'},
 {'title': 'Fantastic Granite Gloves c99b8084', 'price': '73.09'},
 {'title': 'Handmade Soft Bike 0460adec', 'price': '67.67'},
 {'title': 'Tuna edbc4d12', 'price': '42.94'},
 ...
 {'title': 'Gorgeous Ball e51b0ec6', 'price': '44.38'}]
```

Repare que os valores vêm todos como **texto** (`'39.8'`); o Django converte o preço para `Decimal` ao salvar.

Agora uma função que salva os dados no banco:

```python
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

Para cada linha criamos um objeto `Product` **em memória** (sem salvar) e o guardamos na lista auxiliar `aux`. No fim, o `bulk_create` insere todos de uma vez, numa única consulta. É super rápido.

**Atenção:** o `bulk_create` não chama o método `save()` de cada objeto, e por isso **não dispara** os signals `pre_save` e `post_save`. No nosso projeto, isso quer dizer que o signal da [Dica 27](093-27-signals.md), que preenche o `slug`, não roda para os produtos importados assim.

Na lista de produtos da aplicação, havia 5 produtos; depois do `save_data`, passaram a ser 105.

## Importando CSV com o novo comando import_data

Agora vamos fazer o mesmo com um comando. Primeiro, só o argumento com o nome do arquivo, para ver se ele chega no `handle`:

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

* `--filename_csv` é o nome longo do argumento e `-fcsv`, o curto.
* `dest='filename_csv'` é a chave em que o valor fica guardado no dicionário `options`.
* O `help` aparece na ajuda do comando.

```bash
python manage.py import_data --help

python manage.py import_data --filename_csv '/tmp/products.csv'
```

O segundo comando só imprime o nome do arquivo:

```
/tmp/products.csv
```

Continuando, o comando completo, com a leitura do CSV, uma barra de progresso e a gravação no banco:

```python
# backend/core/management/commands/import_data.py
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

* `csv_to_list` e `save_data` são as mesmas funções do shell.
* `progressbar` é um gerador que envolve a lista: a cada item entregue no `for`, ele redesenha a barra (`#` para o que já foi, `.` para o que falta) e o contador `j/count`. O `\r` volta o cursor para o início da linha, então a barra é reescrita no mesmo lugar.
* No `save_data`, em vez de `for item in data`, usamos `for item in progressbar(data, 'Importando dados')`.
* O `handle` apaga todos os produtos antes de importar, para podermos rodar o comando várias vezes sem repetir títulos (o `title` é único).

```bash
python manage.py import_data -fcsv '/tmp/products.csv'
```

Saída:

```
Importando dados[############################################################] 100/100
```

Foi tão rápido que nem dá para ver a barra andando.

## Simulando o progressbar um pouco mais lento

Só para fins didáticos, vamos criar uma opção de "câmera lenta": em vez do `bulk_create`, salvar um produto por vez, com uma pausa de 0,02 s. As linhas novas estão marcadas com `# <---`.

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

O argumento `--slow_motion` é um booleano: com `action='store_true'`, ele não recebe valor; basta passar `-slow` para ele valer `True`.

O arquivo completo ficou assim:

```python
# backend/core/management/commands/import_data.py
import csv
import sys
from time import sleep

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
        if slow_motion:
            obj.save()
            sleep(.02)
        else:
            aux.append(obj)

    if not slow_motion:
        Product.objects.bulk_create(aux)


def import_csv(filename, slow_motion=None):
    data = csv_to_list(filename)
    save_data(data, slow_motion)


class Command(BaseCommand):
    help = 'Importa dados de um CSV.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename_csv',
            '-fcsv',
            dest='filename_csv',
            help='Importa arquivo CSV.'
        )
        parser.add_argument(
            '--slow_motion',
            '-slow',
            action='store_true',
            help='Simula camera lenta.'
        )

    def handle(self, *args, **options):
        filename_csv = options['filename_csv']
        slow_motion = options['slow_motion']

        Product.objects.all().delete()
        import_csv(filename_csv, slow_motion)
```

A ajuda do comando agora mostra as duas opções:

```bash
python manage.py import_data --help
```

```
usage: manage.py import_data [-h] [--filename_csv FILENAME_CSV]
                             [--slow_motion] [--version] [-v {0,1,2,3}]
                             ...

Importa dados de um CSV.

options:
  -h, --help            show this help message and exit
  --filename_csv FILENAME_CSV, -fcsv FILENAME_CSV
                        Importa arquivo CSV.
  --slow_motion, -slow  Simula camera lenta.
  ...
```

E rodando em câmera lenta:

```bash
python manage.py import_data -fcsv '/tmp/products.csv' -slow
```

Agora dá para ver a barra de progresso evoluindo:

```
Importando dados[########################################################....] 94/100
```

até chegar em `100/100`. Como nesse modo cada produto é gravado com `obj.save()`, os signals rodam e o `slug` é preenchido.

Pronto: vimos como ler um CSV com `csv.DictReader`, gravar em lote com `bulk_create` e empacotar tudo num comando do Django com argumentos e barra de progresso.
