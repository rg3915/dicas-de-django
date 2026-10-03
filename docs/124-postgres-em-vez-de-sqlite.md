# Postgres em vez de SQLite, até no dev

<!--agendado-->

> 📅 **Vídeo agendado:** será publicado no YouTube em **14/10/2026, às 10:00**.

<!--/agendado-->

<!--yt-block ikCqYsBHr6k short-->

O SQLite ignora o `max_length`: um `CharField(max_length=10)` aceita 18 letras, calado. O PostgreSQL dá `DataError` na hora, e é esse erro que você quer ver na sua máquina, não no seu cliente.

* O banco da sua máquina tem que ser igual ao da produção.
* De brinde: `django.contrib.postgres` (unaccent, SearchVector, ArrayField).
* E subir é um comando: `docker compose up -d`.

Neste tutorial você vai reproduzir o bug na sua máquina: o mesmo código, o mesmo comando, e o SQLite aceitando o que o PostgreSQL recusa. Depois, vai configurar o Django para usar o Postgres no desenvolvimento e ver o que o `django.contrib.postgres` oferece que o SQLite não tem.

## Pré-requisitos

* Python 3.14 e o `uv` (ou o `pip`, se preferir).
* Docker com o Docker Compose, para subir o PostgreSQL.

Documentação de apoio:

* `django.contrib.postgres`: [https://docs.djangoproject.com/en/6.1/ref/contrib/postgres/](https://docs.djangoproject.com/en/6.1/ref/contrib/postgres/)
* Imagem oficial do PostgreSQL: [https://hub.docker.com/_/postgres](https://hub.docker.com/_/postgres)
* dj-database-url: [https://github.com/jazzband/dj-database-url](https://github.com/jazzband/dj-database-url)

## Passo 1: o projeto

Crie o projeto com o uv:

```
mkdir projeto && cd projeto
uv init --bare
uv add django "psycopg[binary]" python-decouple
uv run django-admin startproject config .
uv run python manage.py startapp produtos
```

O `pyproject.toml` fica assim:

```toml
# pyproject.toml
[project]
name = "postgres-vs-sqlite"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = [
    "django>=6.1.1",
    "psycopg[binary]>=3.3.6",
    "python-decouple>=3.8",
]
```

* `psycopg[binary]` é o driver do PostgreSQL (psycopg 3).
* `python-decouple` vai servir para trocar de banco com uma variável de ambiente.

O model tem um único campo de texto de **no máximo 10 caracteres**:

```python
# produtos/models.py
from django.db import models


class Produto(models.Model):
    nome = models.CharField(max_length=10)

    def __str__(self):
        return self.nome
```

Coloque a app no `INSTALLED_APPS`:

```python
# config/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'produtos',
]
```

## Passo 2: o banco com Docker Compose

```yaml
# compose.yaml
services:
  db:
    image: postgres:18-alpine
    environment:
      POSTGRES_DB: loja
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
```

* `POSTGRES_DB` cria o banco `loja` na primeira vez que o container sobe.
* `POSTGRES_PASSWORD` define a senha do usuário `postgres` (que é o usuário padrão da imagem).
* `ports` expõe a porta 5432 para a sua máquina, onde o Django roda.

Subir é um comando:

```
docker compose up -d
```

O `-d` deixa o container rodando em segundo plano. Para ver os logs, `docker compose logs -f db`; para parar, `docker compose down`.

Este compose é para desenvolvimento: a senha está no arquivo e não há volume nomeado. Se quiser que os dados sobrevivam a um `docker compose down`, adicione um volume (no PostgreSQL 18, monte em `/var/lib/postgresql`):

```yaml
# compose.yaml (com volume)
services:
  db:
    image: postgres:18-alpine
    environment:
      POSTGRES_DB: loja
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql

volumes:
  pgdata:
```

## Passo 3: configurando o Django

### Opção 1: o dicionário DATABASES

No projeto do vídeo, o Postgres é o padrão, e uma variável `DB=sqlite` troca para o SQLite. É isso que permite rodar o mesmo comando nos dois bancos e comparar:

```python
# config/settings.py
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# ...

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'loja',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

if config('DB', default='postgres') == 'sqlite':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
```

### Opção 2: dj-database-url

Em um projeto real, o mais prático é guardar a conexão inteira em uma URL no `.env`. Instale o pacote:

```
uv add dj-database-url
```

```python
# config/settings.py
import dj_database_url
from decouple import config

DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL')),
}
```

```
# .env
DATABASE_URL=postgres://postgres:postgres@localhost:5432/loja
```

A URL segue o formato `postgres://usuario:senha@host:porta/banco`. Em produção você muda só o `.env`, e o `settings.py` continua o mesmo. Para usar o SQLite com a mesma configuração, a URL seria `sqlite:///db.sqlite3`.

Com qualquer uma das opções, crie as tabelas:

```
uv run python manage.py makemigrations produtos
uv run python manage.py migrate
```

E, para comparar, crie também o banco SQLite:

```
DB=sqlite uv run python manage.py migrate
```

## Passo 4: o bug do max_length no SQLite

Abra o shell usando o SQLite e salve um nome com 18 letras num campo de no máximo 10:

```
DB=sqlite uv run python manage.py shell
```

```python
>>> Produto.objects.create(nome="Parafuso sextavado")
<Produto: Parafuso sextavado>
>>> len(Produto.objects.get().nome)
18
```

O SQLite aceitou, calado, e gravou as 18 letras. O motivo: o Django cria a coluna como `varchar(10)`, mas o SQLite ignora o tamanho declarado. Para ele, é só um texto, de qualquer tamanho.

Agora o mesmo comando no PostgreSQL:

```
uv run python manage.py shell
```

```python
>>> Produto.objects.create(nome="Parafuso sextavado")
Traceback (most recent call last):
  ...
psycopg.errors.StringDataRightTruncation: value too long for type character varying(10)

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  ...
django.db.utils.DataError: value too long for type character varying(10)
```

O PostgreSQL respeita o `varchar(10)` e recusa o valor com um `DataError`. É esse erro que você quer ver na sua máquina, e não no servidor do seu cliente, depois do deploy.

Repare que nenhum dos dois passou pela validação do Django: o `max_length` só é validado em formulários (`ModelForm`) ou quando você chama `full_clean()` no objeto. O `create()` manda direto para o banco, e aí cada banco se comporta de um jeito.

O `max_length` é só um exemplo. Outras diferenças que o SQLite esconde:

* Tipos: o SQLite tem tipagem flexível; um texto que chegue por SQL direto (um script, outro sistema) entra numa coluna `integer` sem reclamar.
* Ordenação e comparação de texto com acentos e maiúsculas.
* Concorrência: o SQLite bloqueia o arquivo inteiro na escrita; `select_for_update()` não tem efeito nele.
* Funções e lookups que só existem no Postgres (os do próximo passo).

Por isso a regra: **o banco da sua máquina tem que ser igual ao da produção**.

## Passo 5: o pró, django.contrib.postgres

Usando o PostgreSQL, você ganha um pacote inteiro do Django feito só para ele. Adicione-o ao `INSTALLED_APPS`:

```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'produtos',
]
```

Para os exemplos, crie um model `Livro` com um `ArrayField`, um campo que guarda uma lista de verdade numa coluna só:

```python
# produtos/models.py
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Produto(models.Model):
    nome = models.CharField(max_length=10)

    def __str__(self):
        return self.nome


class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    resumo = models.TextField(blank=True)
    tags = ArrayField(models.CharField(max_length=30), default=list, blank=True)

    def __str__(self):
        return self.titulo
```

O `default=list` (a função, sem parênteses) garante que cada livro novo ganhe uma lista vazia própria.

### Ativando a extensão unaccent

A busca sem acento usa a extensão `unaccent` do PostgreSQL, que precisa ser instalada no banco. O Django tem uma operação de migration para isso. Gere as migrations, sendo a segunda vazia:

```
uv run python manage.py makemigrations produtos
uv run python manage.py makemigrations produtos --empty -n unaccent
```

E edite a migration vazia:

```python
# produtos/migrations/0003_unaccent.py
from django.contrib.postgres.operations import UnaccentExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0002_livro'),
    ]

    operations = [
        UnaccentExtension(),
    ]
```

```
uv run python manage.py migrate
```

O usuário do banco precisa ter permissão para criar extensões. Com o usuário `postgres` da imagem do Docker, tem.

### Testando no shell

```
uv run python manage.py shell
```

Crie alguns livros:

```python
Livro.objects.create(titulo='Programação em Python', resumo='Do básico ao Django.', tags=['python', 'django'])
Livro.objects.create(titulo='Ação e reação', resumo='Um romance.', tags=['romance'])
Livro.objects.create(titulo='Banco de dados', resumo='PostgreSQL na prática, com Django.', tags=['sql', 'postgres'])
```

**Busca sem acento** (lookup `unaccent`), que pode ser encadeado com outros lookups:

```python
>>> Livro.objects.filter(titulo__unaccent__icontains='programacao')
<QuerySet [<Livro: Programação em Python>]>
>>> Livro.objects.filter(titulo__unaccent__icontains='acao')
<QuerySet [<Livro: Programação em Python>, <Livro: Ação e reação>]>
```

O usuário digitou sem acento e mesmo assim encontrou "Programação" e "Ação".

**Busca por texto** (full text search) com `SearchVector`:

```python
>>> from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
>>> Livro.objects.annotate(
...     busca=SearchVector('titulo', 'resumo', config='portuguese'),
... ).filter(busca='django')
<QuerySet [<Livro: Programação em Python>, <Livro: Banco de dados>]>
```

O `SearchVector` junta os campos e os transforma em um vetor de palavras normalizadas; `config='portuguese'` aplica as regras do português (radicais, palavras como "de" e "com" ignoradas). Para buscar num campo só, existe o atalho `__search`:

```python
>>> Livro.objects.filter(resumo__search='prática')
<QuerySet [<Livro: Banco de dados>]>
```

Para ordenar por relevância, dê pesos aos campos e use o `SearchRank`:

```python
vetor = (
    SearchVector('titulo', weight='A', config='portuguese')
    + SearchVector('resumo', weight='B', config='portuguese')
)
consulta = SearchQuery('django', config='portuguese')
Livro.objects.annotate(
    rank=SearchRank(vetor, consulta),
).filter(rank__gt=0).order_by('-rank')
```

Com o peso `A`, uma palavra encontrada no título vale mais que a mesma palavra no resumo.

**Campo de lista** (`ArrayField`) com lookups próprios:

```python
>>> Livro.objects.filter(tags__contains=['django'])       # tem todas estas tags
<QuerySet [<Livro: Programação em Python>]>
>>> Livro.objects.filter(tags__overlap=['sql', 'romance'])  # tem pelo menos uma
<QuerySet [<Livro: Ação e reação>, <Livro: Banco de dados>]>
>>> Livro.objects.filter(tags__len=2)                      # tamanho da lista
<QuerySet [<Livro: Programação em Python>, <Livro: Banco de dados>]>
>>> Livro.objects.filter(tags__0='python')                 # primeiro item
<QuerySet [<Livro: Programação em Python>]>
```

Nada disso funciona no SQLite: o `ArrayField` é exclusivo do PostgreSQL, e os lookups `unaccent` e `search` não existem lá. O pacote ainda traz `JSONB` com índices `GinIndex`, `HStoreField`, campos de intervalo (`DateRangeField`, `IntegerRangeField`) e restrições de exclusão (`ExclusionConstraint`).

## Resumo

* O SQLite ignora o `max_length`; o PostgreSQL dá `DataError`. Teste no mesmo banco que vai para a produção.
* Subir o Postgres no desenvolvimento é um `compose.yaml` de poucas linhas e um `docker compose up -d`.
* Configure com o dicionário `DATABASES` ou, melhor, com uma `DATABASE_URL` lida pelo `dj-database-url`.
* De brinde, o `django.contrib.postgres` traz busca sem acento, busca por texto e campo de lista.
