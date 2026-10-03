# N+1 no Django 6.1: o fim do select_related?

Publicado em 20/09/2026.

**Testado com:** Django 6.1.1 e Python 3.12.
{: .versoes }

<a href="https://youtu.be/Tiyg4H519x0">
    <img src="../.gitbook/assets/youtube.png">
</a>

Doc: [https://docs.djangoproject.com/en/6.1/topics/db/fetch-modes/](https://docs.djangoproject.com/en/6.1/topics/db/fetch-modes/)

O problema de N+1 queries é o gargalo de performance mais comum em projetos Django: uma listagem que parece inocente dispara uma query para cada linha. Neste tutorial vamos reproduzir o problema, detectá-lo de três formas (teste, log de SQL e Debug Toolbar), corrigi-lo com `select_related` e `prefetch_related` e, por fim, usar a novidade do Django 6.1: os **fetch modes** (`FETCH_ONE`, `FETCH_PEERS` e `FETCH_RAISE`).

## Pré-requisitos

* Python 3.12, 3.13 ou 3.14.
* Django 6.1 (`pip install "django>=6.1"`). Os exemplos foram rodados com o Django 6.1.1.

## O projeto de exemplo

```bash
python -m venv .venv
source .venv/bin/activate
pip install "django>=6.1"

django-admin startproject config .
python manage.py startapp books
```

Adicione `'books'` ao `INSTALLED_APPS` em `config/settings.py`.

```python
# books/models.py
from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='books')
    tags = models.ManyToManyField(Tag, blank=True, related_name='books')

    def __str__(self):
        return self.title
```

```bash
python manage.py makemigrations
python manage.py migrate
```

## O problema

Este loop parece uma linha só de trabalho:

```python
for book in Book.objects.all():
    print(book.title, book.author.name)
```

Mas o `Book.objects.all()` busca apenas as colunas da tabela `books_book`. O `author` não veio junto; quando você acessa `book.author`, o Django vai ao banco buscar aquele autor. Com 100 livros são **1 query** para os livros **+ 100 queries** para os autores: 1+N. Isso é o N+1.

O mesmo acontece no template, onde é ainda mais difícil de enxergar:

```django
{# books/templates/books/book_list.html #}
<ul>
  {% for book in object_list %}
    <li>{{ book.title }} - {{ book.author.name }} ({{ book.publisher.name }})</li>
  {% endfor %}
</ul>
```

Com uma `ListView` simples (`model = Book`), essa página faz 1 + 2N queries: uma para autor e outra para editora em cada livro.

## Como detectar

### 1. No teste, com assertNumQueries

É a forma mais confiável, porque trava a regressão: se alguém reintroduzir o N+1, o teste quebra.

```python
# books/tests.py
from django.test import TestCase

from books.models import Author, Book, Publisher, Tag


class BookQueriesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        publisher = Publisher.objects.create(name='Novatec')
        python = Tag.objects.create(name='python')
        for i in range(5):
            author = Author.objects.create(name=f'Autor {i}')
            book = Book.objects.create(title=f'Livro {i}', author=author, publisher=publisher)
            book.tags.add(python)

    def test_n_mais_1(self):
        # 1 query para os livros + 5 para os autores
        with self.assertNumQueries(6):
            names = [book.author.name for book in Book.objects.all()]
        self.assertEqual(len(names), 5)
```

O `assertNumQueries(n)` conta as queries executadas dentro do bloco `with` e falha se o número for diferente de `n`.

### 2. Durante o desenvolvimento, com o logger do banco

O logger `django.db.backends` registra cada SQL executado, mas só quando `DEBUG = True`:

```python
# config/settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

Rode o `runserver`, abra a listagem e veja no terminal a mesma query `SELECT ... FROM "books_author" WHERE "books_author"."id" = ...` repetida várias vezes. Repetição é o sintoma.

### 3. Com o Django Debug Toolbar

A [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/) mostra no navegador, no painel SQL, quantas queries a página fez e marca as duplicadas ("similar" e "duplicated"). Siga a instalação da documentação dela (`pip install django-debug-toolbar`, app, middleware e URLs).

## A correção clássica: select_related e prefetch_related

Quando você sabe de antemão quais relacionamentos vai usar, peça-os explicitamente.

* **`select_related`**: para `ForeignKey` e `OneToOneField`. Faz um `JOIN` e traz tudo numa query só.
* **`prefetch_related`**: para `ManyToManyField` e relacionamentos reversos (`author.books`). Faz uma query extra por relacionamento e junta os resultados em Python.

```python
# books/tests.py (continuação)
    def test_select_related(self):
        with self.assertNumQueries(1):
            names = [book.author.name for book in Book.objects.select_related('author')]
        self.assertEqual(len(names), 5)

    def test_prefetch_related(self):
        with self.assertNumQueries(2):
            tags = [
                [tag.name for tag in book.tags.all()]
                for book in Book.objects.prefetch_related('tags')
            ]
        self.assertEqual(len(tags), 5)
```

Na view:

```python
# books/views.py
from django.views.generic import ListView

from books.models import Book


class BookListView(ListView):
    model = Book

    def get_queryset(self):
        return Book.objects.select_related('author', 'publisher').prefetch_related('tags')
```

Atenção à mudança do Django 6.1: chamar `select_related()` **sem argumentos** (que seguia todas as FKs não nulas) foi depreciado e emite um aviso de depreciação (o comportamento sai na próxima versão maior, a Django 2028). Passe os campos explicitamente, como acima, ou use o `FETCH_PEERS`.

## Fetch modes no Django 6.1

Até o Django 6.0 existia só um comportamento: ao acessar um campo que não foi carregado, buscar aquele campo daquela instância. O Django 6.1 dá nome a esse comportamento e oferece alternativas. O modo é definido por queryset, com o novo método `QuerySet.fetch_mode()`, e as constantes ficam em `django.db.models`.

| Modo | O que faz | Queries no loop de livros e autores |
|---|---|---|
| `models.FETCH_ONE` | Busca o campo só para a instância atual. É o padrão (o comportamento de sempre). | 1 + N |
| `models.FETCH_PEERS` | Busca o campo para a instância atual e para todas as "pares", as instâncias que vieram do mesmo queryset. | 2 |
| `models.FETCH_RAISE` | Não busca: levanta `FieldFetchBlocked`. | exceção |

Os fetch modes valem para `ForeignKey`, `OneToOneField` (e o acesso reverso dele), campos adiados com `defer()` ou `only()` e relações genéricas. Não valem para `ManyToManyField` nem para relacionamentos reversos de FK (`author.books.all()`): nesses casos, o `prefetch_related` continua sendo a ferramenta. O modo também é copiado para os objetos relacionados que o Django busca, então vale para a árvore toda de relacionamentos.

### FETCH_RAISE: transformando o N+1 em erro

```python
# books/tests.py (continuação)
from django.core.exceptions import FieldFetchBlocked
from django.db import models

    def test_fetch_raise(self):
        books = Book.objects.fetch_mode(models.FETCH_RAISE)
        with self.assertRaises(FieldFetchBlocked):
            for book in books:
                book.author.name

    def test_fetch_raise_com_select_related(self):
        books = Book.objects.select_related('author').fetch_mode(models.FETCH_RAISE)
        with self.assertNumQueries(1):
            names = [book.author.name for book in books]
        self.assertEqual(len(names), 5)
```

No primeiro teste, o acesso a `book.author` levanta:

```
django.core.exceptions.FieldFetchBlocked: Fetching of Book.author blocked.
```

No segundo, o autor já veio pelo `select_related`, então nada é bloqueado. É uma ótima forma de proteger trechos críticos: se alguém esquecer um `select_related`, o código quebra em vez de ficar lento em silêncio.

### FETCH_PEERS: o N+1 vira 2 queries

```python
# books/tests.py (continuação)
    def test_fetch_peers(self):
        with self.assertNumQueries(2):
            names = [book.author.name for book in Book.objects.fetch_mode(models.FETCH_PEERS)]
        self.assertEqual(len(names), 5)
```

Na primeira vez em que o loop acessa `book.author`, o Django percebe que o campo não foi carregado e busca os autores de **todos** os livros daquele queryset numa query só (um `WHERE id IN (...)`). Do segundo livro em diante, o autor já está lá. É como um `prefetch_related` sob demanda, sem precisar listar os campos antes.

### Tornando o FETCH_PEERS o padrão de um model

Com um manager customizado, todo queryset do model já nasce com o modo definido:

```python
# books/models.py (trecho)
class BookManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().fetch_mode(models.FETCH_PEERS)


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='books')
    tags = models.ManyToManyField(Tag, blank=True, related_name='books')

    objects = BookManager()
```

Agora `Book.objects.all()` num loop que acessa `author` e `publisher` faz 3 queries (livros, autores, editoras), não importa quantos livros existam.

Se preferir manter o padrão e ter o modo como opção, declare os dois managers (`objects = models.Manager()` e `peers = BookManager()`) e use `Book.peers.all()` onde quiser.

## Rodando os testes

```bash
python manage.py test books -v 2
```

Todos os testes acima devem passar, confirmando a contagem de queries de cada abordagem.

## Então é o fim do select_related?

Não. Cada ferramenta tem o seu lugar:

* **`select_related('author')`**: quando o acesso é previsível. Continua sendo o mais eficiente para FK, porque resolve tudo num único `JOIN`.
* **`prefetch_related('tags')`**: para many-to-many e reversos, que os fetch modes não cobrem.
* **`FETCH_PEERS`**: brilha em código genérico, onde a lista de campos é um chute e envelhece mal: admin, serializers, templates reaproveitados por várias views.
* **`FETCH_RAISE`**: em trechos críticos e nos testes, para que um N+1 novo apareça como erro.

Em resumo: detecte com `assertNumQueries` (ou com `FETCH_RAISE`), continue usando `select_related` onde o acesso é previsível e use `FETCH_PEERS` onde manter a lista de campos não se sustenta.

Documentação:

* [Fetch modes](https://docs.djangoproject.com/en/6.1/topics/db/fetch-modes/)
* [select_related](https://docs.djangoproject.com/en/6.1/ref/models/querysets/#select-related) e [prefetch_related](https://docs.djangoproject.com/en/6.1/ref/models/querysets/#prefetch-related)
* [assertNumQueries](https://docs.djangoproject.com/en/6.1/topics/testing/tools/#django.test.TransactionTestCase.assertNumQueries)
* [Logger django.db.backends](https://docs.djangoproject.com/en/6.1/ref/logging/#django-db-backends)
* [Notas de lançamento do Django 6.1](https://docs.djangoproject.com/en/6.1/releases/6.1/)

## Shorts relacionados

* [Django 6.1 parte 1](https://youtube.com/shorts/VDFvS34mL9A) (15/09/2026)
* [Django 6.1 parte 2](https://youtube.com/shorts/B35bLdqLGqE) (17/09/2026)
* [select_related vs prefetch_related - Junior vs Senior](https://youtube.com/shorts/_VV1Odkk0Wo) (01/10/2026)
