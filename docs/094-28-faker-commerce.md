# Dica 28 - Gerando dados aleatórios com Faker - faker-commerce

**Versões usadas no vídeo:** Python 3.10, Faker 15.3.4 e faker-commerce 1.0.3 (script Python avulso, sem usar o Django).
{: .versoes }

<a href="https://youtu.be/otT4fVdsECc">
    <img src="../.gitbook/assets/youtube.png">
</a>

faker-commerce: [https://github.com/nicobritos/python-faker-commerce](https://github.com/nicobritos/python-faker-commerce)

Github: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

Nesta dica vamos gerar um arquivo CSV com 100 produtos aleatórios (título e preço) usando o [Faker](https://faker.readthedocs.io/) com o provider **faker-commerce**, que acrescenta ao Faker nomes de produtos de e-commerce ("Ergonomic Soft Bike", "Rustic Hat" etc.). Esse CSV serve de entrada para a próxima dica, [Importando CSV](095-29-import-csv.md).

## Instalação

Com o virtualenv ativo, na pasta do projeto, crie o arquivo `gen_products.py` em `backend/product`.

```bash
touch backend/product/gen_products.py
```

E instale

```bash
pip install faker-commerce

pip freeze | grep faker-commerce >> requirements.txt
```

O `faker-commerce` instala o `Faker` como dependência. No vídeo, o `pip freeze` mostrou:

```
faker-commerce==1.0.3
```

## O script

```python
# backend/product/gen_products.py
'''
Gera 100 produtos (título e preço) randomicamente com faker-commerce.

pip install faker-commerce
'''

import csv
import random
import uuid

import faker_commerce
from faker import Faker

fake = Faker()
fake.add_provider(faker_commerce.Provider)


QUANTITY = 100


with open('/tmp/products.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['title', 'price'])
    for _ in range(QUANTITY):
        short_uuid = uuid.uuid4().hex[:8]
        title = f'{fake.ecommerce_name()} {short_uuid}'
        price = round(random.uniform(1, 100), 2)
        writer.writerow([title, price])
```

Passo a passo:

* `fake.add_provider(faker_commerce.Provider)` acrescenta ao Faker os métodos do faker-commerce, entre eles o `ecommerce_name()`, que devolve um nome de produto.
* `QUANTITY = 100` é a quantidade de registros.
* O arquivo é gravado em `/tmp/products.csv`, fora da pasta do projeto, porque ele não precisa ser versionado. O `newline=''` é o recomendado pela documentação do módulo `csv` ao abrir o arquivo, para não gerar linhas em branco extras.
* `writer.writerow(['title', 'price'])` escreve o cabeçalho; o `writerow` recebe uma lista.
* No `for _ in range(QUANTITY)`, o `_` indica que não vamos usar a variável do laço.
* `uuid.uuid4().hex[:8]` gera um UUID, pega a forma `hex` (sem os tracinhos) e usa só os 8 primeiros caracteres. Ele é colocado no fim do título para garantir que **não haja títulos repetidos**: o faker-commerce pode sortear o mesmo nome de produto mais de uma vez, e o campo `title` do model `Product` é `unique=True`.
* `round(random.uniform(1, 100), 2)` sorteia um preço entre 1 e 100, com duas casas decimais.

## Rodando

E finalmente rodamos

```bash
python backend/product/gen_products.py
```

O resultado fica em `/tmp/products.csv`:

```bash
cat /tmp/products.csv
```

```
title,price
Table 95d9d2f9,99.73
Gloves 511bae99,89.01
Gorgeous Shoes eeb71af3,51.24
Generic Cotton Car 38dbcb9c,83.57
Cotton Towels 4d6326c3,32.99
Licensed Steel Chicken f9855203,72.14
Rustic Hat 99b40a72,13.14
...
```

São 101 linhas: o cabeçalho e 100 produtos. Como os dados são aleatórios, o seu arquivo terá outros nomes e preços.

Pronto: com poucas linhas temos um CSV de produtos para testar a importação de dados no Django.
