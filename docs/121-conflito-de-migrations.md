# Como resolver conflito de migrations no Django

Publicado em 03/10/2026.

<a href="https://youtu.be/OypqG84JKHQ">
    <img src="../.gitbook/assets/youtube.png">
</a>

Documentação: [https://docs.djangoproject.com/en/stable/topics/migrations/#version-control](https://docs.djangoproject.com/en/stable/topics/migrations/#version-control)

Dois times, duas branches, e cada uma criou a sua migration `0012` no mesmo app. O git mesclou sem reclamar; quem reclamou foi o Django, no `migrate`:

```
Conflicting migrations detected; multiple leaf nodes in the migration graph
```

Neste tutorial vamos reproduzir esse cenário do zero, com git de verdade, entender por que renomear a migration é o conserto errado, resolver com `makemigrations --merge` e deixar na suíte um teste com `MigrationLoader.detect_conflicts()` para que o próximo conflito apareça nos testes, e não no deploy.

## Pré-requisitos

* Python 3.12 ou superior e Django 5.x ou 6.x (os exemplos foram rodados com o Django 6.0.8).
* git.
* Para o teste em estilo pytest: `pytest` e `pytest-django`.

## O cenário

Um app de vendas, `sales`, e dois times:

* **Comercial**, na branch `feature/order-discount`: adiciona um campo de desconto no pedido (`AddField`).
* **Financeiro**, na branch `feature/archive-cancelled-orders`: uma migration de dados que marca os pedidos cancelados como arquivados (`RunPython`).

Os dois saíram do mesmo ponto da `develop` e os dois precisaram de migration na mesma semana. No vídeo, o app estava na `0011`, e as duas branches criaram uma `0012`. Aqui, para reproduzir do zero, o ponto comum é a `0001`, então as duas criam uma `0002` e o merge será a `0003`. O mecanismo é exatamente o mesmo.

```
                 ┌── 0002_order_discount            (comercial)
0001_initial ────┤
                 └── 0002_archive_cancelled_orders  (financeiro)
```

Cada migration está certa sozinha, e as duas declaram a mesma dependência: `('sales', '0001_initial')`. O grafo de migrations passa a ter **duas folhas** (dois nós sem filhos), e o Django não sabe qual roda por último.

## Montando o projeto

```bash
python -m venv .venv
source .venv/bin/activate
pip install django pytest pytest-django

django-admin startproject config .
python manage.py startapp sales
```

Adicione `'sales'` ao `INSTALLED_APPS` em `config/settings.py`.

```python
# sales/models.py
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        PAID = 'paid', 'Pago'
        CANCELLED = 'cancelled', 'Cancelado'

    customer = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.customer} - {self.status}'
```

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = test_*.py tests.py
```

```bash
python manage.py makemigrations sales
python manage.py migrate

git init -b develop
printf '.venv/\n__pycache__/\ndb.sqlite3\n' > .gitignore
git add .
git commit -m "app sales com Order"
```

## A branch do financeiro: RunPython

```bash
git checkout -b feature/archive-cancelled-orders develop
python manage.py makemigrations sales --empty --name archive_cancelled_orders
```

O `--empty` cria uma migration sem operações, que preenchemos com a migração de dados:

```python
# sales/migrations/0002_archive_cancelled_orders.py
from django.db import migrations


def archive_cancelled(apps, schema_editor):
    Order = apps.get_model('sales', 'Order')
    Order.objects.filter(status='cancelled', archived=False).update(archived=True)


def unarchive_cancelled(apps, schema_editor):
    Order = apps.get_model('sales', 'Order')
    Order.objects.filter(status='cancelled', archived=True).update(archived=False)


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(archive_cancelled, unarchive_cancelled),
    ]
```

Repare no `apps.get_model()`: dentro de uma migration, use sempre o model "histórico", com o estado do banco naquele ponto, e não o import direto de `sales.models`. A segunda função é o caminho de volta, usado se alguém desfizer a migration.

```bash
git add .
git commit -m "arquiva pedidos cancelados"
```

## A branch do comercial: AddField

```bash
git checkout -b feature/order-discount develop
```

Acrescente o campo no model:

```python
# sales/models.py (trecho)
    archived = models.BooleanField(default=False)
    discount = models.PositiveSmallIntegerField('desconto (%)', default=0)
```

```bash
python manage.py makemigrations sales --name order_discount
```

```python
# sales/migrations/0002_order_discount.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discount',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='desconto (%)'),
        ),
    ]
```

```bash
git add .
git commit -m "adiciona desconto no pedido"
```

## As duas chegam na develop

A primeira entra sem problema:

```bash
git checkout develop
git merge --no-ff feature/order-discount -m "Merge feature/order-discount"
python manage.py migrate
#   Applying sales.0002_order_discount... OK
```

Agora a segunda. O git não reclama: são dois arquivos com nomes diferentes, não há conflito de texto.

```bash
git merge --no-ff feature/archive-cancelled-orders -m "Merge feature/archive-cancelled-orders"
# Merge made by the 'ort' strategy.

python manage.py migrate
```

```
CommandError: Conflicting migrations detected; multiple leaf nodes in the migration graph: (0002_archive_cancelled_orders, 0002_order_discount in sales).
To fix them run 'python manage.py makemigrations --merge'
```

A própria mensagem diz o conserto. Mas antes, a tentação.

## Por que não renomear

A primeira ideia de todo mundo é renomear a do financeiro para `0003` e seguir. Não faça isso.

* A `0002_archive_cancelled_orders` já está publicada na branch do financeiro com esse nome, e o ambiente de homologação deles pode já tê-la aplicado.
* O Django identifica uma migration aplicada pelo par (app, nome) na tabela `django_migrations`. Renomeando só na `develop`, a mesma migration passa a ter dois nomes em duas branches.
* No próximo merge do financeiro, o arquivo `0002_archive_cancelled_orders` volta para a `develop` ao lado da cópia renomeada, e o mesmo `RunPython` roda duas vezes.

Migration publicada é imutável: não renomeie, não apague, não edite.

## O conserto: makemigrations --merge

```bash
python manage.py makemigrations sales --merge --no-input \
    --name merge_order_discount_and_archive_cancelled
```

```
Merging sales
  Branch 0002_archive_cancelled_orders
    p Raw Python operation
  Branch 0002_order_discount
    + Add field discount to order

Created new merge migration sales/migrations/0003_merge_order_discount_and_archive_cancelled.py
```

Dê um nome descritivo com `--name`; o padrão é um carimbo de data e hora que não diz nada. O `--no-input` dispensa a confirmação interativa. O arquivo gerado:

```python
# sales/migrations/0003_merge_order_discount_and_archive_cancelled.py
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_archive_cancelled_orders'),
        ('sales', '0002_order_discount'),
    ]

    operations = [
    ]
```

A migration de merge tem as duas folhas em `dependencies` e `operations` vazio: ela não altera o banco, só diz ao grafo "as duas vêm antes de mim". As duas `0002` continuam exatamente como foram publicadas.

```
                 ┌── 0002_order_discount ───────────┐
0001_initial ────┤                                  ├── 0003_merge_...
                 └── 0002_archive_cancelled_orders ─┘
```

O `--merge` só resolve o grafo. Se as duas migrations mexessem no mesmo campo de formas incompatíveis, você teria de resolver isso numa migration nova, depois do merge.

## Conferindo antes de aplicar

```bash
python manage.py makemigrations sales --check --dry-run
# No changes detected in app 'sales'

python manage.py migrate sales --plan
```

```
Planned operations:
sales.0002_archive_cancelled_orders
    Raw Python operation
sales.0003_merge_order_discount_and_archive_cancelled
```

* `--check --dry-run`: confirma que os models e as migrations estão em sincronia (sai com código diferente de zero se faltar migration, o que é útil no CI).
* `migrate --plan`: mostra o que vai rodar sem aplicar. Aqui, a `0002_order_discount` já estava aplicada nesta base; faltam a do financeiro e a de merge.

Aplicando:

```bash
python manage.py migrate sales
#   Applying sales.0002_archive_cancelled_orders... OK
#   Applying sales.0003_merge_order_discount_and_archive_cancelled... OK

python manage.py showmigrations sales
```

```
sales
 [X] 0001_initial
 [X] 0002_order_discount
 [X] 0002_archive_cancelled_orders
 [X] 0003_merge_order_discount_and_archive_cancelled
```

## O passo a passo completo

```bash
# 1. mesclar
git checkout develop
git merge feature/archive-cancelled-orders

# 2. resolver os conflitos de texto (CHANGELOG, docs, testes)
#    pela união das regras dos dois lados, sem mudar nenhuma asserção

# 3. gerar a migration de merge, com nome
python manage.py makemigrations sales --merge --no-input \
    --name merge_order_discount_and_archive_cancelled

# 4. conferir
python manage.py makemigrations sales --check --dry-run
python manage.py migrate sales --plan

# 5. rodar a suíte inteira do app: as duas features têm de passar juntas
pytest sales/tests

# 6. aplicar e publicar
python manage.py migrate sales
git add sales/migrations/0003_merge_order_discount_and_archive_cancelled.py
git commit -m "Merge das migrations de desconto e de arquivamento"
git push origin develop
```

As branches de feature não mudam; só a `develop` ganha a migration de merge.

## Um teste para pegar o próximo conflito

O `MigrationLoader` é a classe que o próprio `migrate` usa para montar o grafo. Criado com `None` no lugar da conexão, ele lê só os arquivos de migration e não toca no banco. O `detect_conflicts()` devolve um dicionário `{app: [folhas]}` com os apps que têm mais de uma folha.

```python
# sales/tests/test_migrations_graph.py
from django.db.migrations.loader import MigrationLoader


def test_o_app_tem_uma_folha_so():
    # sem conexão, o loader lê só os arquivos e não toca no banco
    conflicts = MigrationLoader(None, ignore_no_migrations=True).detect_conflicts()

    assert 'sales' not in conflicts, conflicts['sales']
```

Crie também o `sales/tests/__init__.py` vazio (e apague o `sales/tests.py` gerado pelo `startapp`, que conflitaria com a pasta). Para ver o teste falhar, rode-o antes de gerar a migration de merge (ou esconda temporariamente a `0003`):

```bash
pytest -q sales/tests
```

```
E       AssertionError: ['0002_archive_cancelled_orders', '0002_order_discount']
E       assert 'sales' not in {'sales': ['0002_archive_cancelled_orders', '0002_order_discount']}
FAILED sales/tests/test_migrations_graph.py::test_o_app_tem_uma_folha_so
```

Com a `0003` no lugar, `1 passed`. Se o projeto usa o test runner do Django em vez do pytest, a mesma ideia vale para todos os apps de uma vez:

```python
# sales/tests/test_migrations_conflicts.py
from django.db.migrations.loader import MigrationLoader
from django.test import SimpleTestCase


class MigrationConflictsTest(SimpleTestCase):
    def test_nenhum_app_tem_duas_folhas(self):
        conflicts = MigrationLoader(None, ignore_no_migrations=True).detect_conflicts()
        self.assertEqual(conflicts, {})
```

```bash
python manage.py test sales
```

O `SimpleTestCase` não cria banco de teste, então o teste roda em milissegundos. Com ele no CI, o pull request que trouxer a segunda folha fica vermelho antes do merge na `develop`.

## Três regras para não repetir

1. Antes de criar migration na sua branch, olhe a `develop`:

    ```bash
    git fetch
    git ls-tree --name-only origin/develop sales/migrations/ | grep -v __init__ | tail -3
    ```

2. Duas folhas: migration de merge. Nunca renomear, nunca apagar.
3. Avise o outro time: a migration de merge já está pronta na `develop`.

Migration publicada é imutável. Conflito de folhas se resolve com merge.

## Short

* [Conflito de migrations no Django: não renomeie!](https://youtube.com/shorts/7rDSpRgUq3k) (03/10/2026)
