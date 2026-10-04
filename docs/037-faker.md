# Dica 37 - Faker

**Versões usadas no vídeo:** Django 2.2, Faker 8.7.0, Python 3.8 e Bootstrap 4.
{: .versoes }

<a href="https://youtu.be/ubgVHtLhubw">
    <img src="../.gitbook/assets/youtube.png">
</a>


**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`). Se copiar código de lá, remova a `\`.

![](../.gitbook/assets/tags.png)


Documentação: [https://faker.readthedocs.io/en/master/](https://faker.readthedocs.io/en/master/)

O [Faker](https://faker.readthedocs.io/en/master/) é uma biblioteca para popular o seu banco de dados com dados aleatórios: nomes, sobrenomes, e-mails, textos, datas, endereços e muito mais. É ótimo para ter uma base de desenvolvimento com volume de dados parecido com o real, para testar listagens, paginação e buscas.

Neste tutorial vamos:

1. acrescentar dois campos ao modelo `Person`;
2. criar um comando personalizado `create_data` que usa o Faker para cadastrar 100 pessoas de uma vez, com `bulk_create` e uma barra de progresso;
3. trocar a view da lista de pessoas por uma `ListView` e montar a tabela no template.

## Pré-requisitos

O vídeo continua o projeto do repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django): um projeto `myproject` com a app `myproject/core`, um `base.html` com Bootstrap 4 e o modelo `Person`. Alguns assuntos usados aqui já foram vistos em outras dicas:

* [Dica 17 - Criando comandos personalizados](017-criando-comandos-personalizados.md);
* [Dica 18 - bulk_create e bulk_update](018-bulk_create-e-bulk_update.md);
* [Dica 24 - Barra de progresso](024-barra-de-progresso.md).

## O modelo Person

Este é o modelo `Person` do projeto. Ele herda de `UuidModel`, uma classe abstrata que acrescenta um `slug` do tipo UUID. Vamos acrescentar os campos `bio` (biografia) e `birthday` (data de nascimento), os dois opcionais:

```python
# myproject/core/models.py
import uuid

from django.db import models


class UuidModel(models.Model):
    slug = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


class Person(UuidModel):
    first_name = models.CharField('nome', max_length=50)
    last_name = models.CharField('sobrenome', max_length=50, null=True, blank=True)  # noqa E501
    email = models.EmailField(null=True, blank=True)
    bio = models.TextField('biografia', null=True, blank=True)
    birthday = models.DateField('nascimento', null=True, blank=True)

    class Meta:
        ordering = ('first_name',)
        verbose_name = 'pessoa'
        verbose_name_plural = 'pessoas'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name or ""}'.strip()

    def __str__(self):
        return self.full_name
```

Gere e aplique a migração:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Instalando o Faker

```bash
pip install faker
```

E acrescente no `requirements.txt` (no vídeo, a versão instalada foi a 8.7.0):

```
Faker==8.7.0
```

## Conhecendo os providers

Os dados do Faker são organizados em *providers*. Na documentação, em [Standard Providers](https://faker.readthedocs.io/en/master/providers.html), você encontra a lista completa. Os que vamos usar:

* [faker.providers.person](https://faker.readthedocs.io/en/master/providers/faker.providers.person.html): `first_name()`, `last_name()`, `name()`, `first_name_male()` etc.;
* [faker.providers.lorem](https://faker.readthedocs.io/en/master/providers/faker.providers.lorem.html): `paragraph(nb_sentences=5)` gera um parágrafo com aproximadamente 5 frases;
* [faker.providers.date_time](https://faker.readthedocs.io/en/master/providers/faker.providers.date_time.html): `date()` gera uma data aleatória no formato `'AAAA-MM-DD'`.

O uso é sempre o mesmo: crie uma instância de `Faker` e chame o método do provider.

```python
>>> from faker import Faker
>>> fake = Faker()
>>> fake.first_name()
'Alexis'
>>> fake.last_name()
'Aguilar'
>>> fake.date()
'2011-07-23'
```

Os valores mudam a cada chamada. Por padrão o Faker usa o idioma `en_US`, por isso os nomes e textos saem em inglês.

## A barra de progresso

Para acompanhar a criação dos registros vamos reaproveitar a barra de progresso da [Dica 24](024-barra-de-progresso.md). Crie a pasta `utils` dentro de `myproject` e o arquivo `progress_bar.py`:

```bash
mkdir myproject/utils
touch myproject/utils/progress_bar.py
```

```python
# myproject/utils/progress_bar.py
import sys


def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)

    def show(j):
        x = int(size * j / count)
        file.write("%s[%s%s] %i/%i\r" %
                   (prefix, "#" * x, "." * (size - x), j, count))
        file.flush()
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i + 1)
    file.write("\n")
    file.flush()
```

A função `progressbar` é um gerador: ela devolve cada item do iterável `it` e, a cada item, reescreve a mesma linha do terminal (por causa do `\r`) com a quantidade de `#` proporcional ao progresso.

## O comando create_data

Crie o comando dentro de `management/commands` da app `core` (as pastas `management` e `commands`, com seus `__init__.py`, já existem no projeto desde a [Dica 17](017-criando-comandos-personalizados.md)):

```bash
touch myproject/core/management/commands/create_data.py
```

```python
# myproject/core/management/commands/create_data.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker

from myproject.core.models import Person
from myproject.utils.progress_bar import progressbar

fake = Faker()


def gen_email(first_name: str, last_name: str):
    first_name = slugify(first_name)
    last_name = slugify(last_name)
    email = f'{first_name}.{last_name}@email.com'
    return email


def get_person():
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = gen_email(first_name, last_name)
    bio = fake.paragraph(nb_sentences=5)
    birthday = fake.date()
    data = dict(
        first_name=first_name,
        last_name=last_name,
        email=email,
        bio=bio,
        birthday=birthday,
    )
    return data


def create_persons():
    aux_list = []
    for _ in progressbar(range(100), 'Persons'):
        data = get_person()
        obj = Person(**data)
        aux_list.append(obj)
    Person.objects.bulk_create(aux_list)


class Command(BaseCommand):
    help = 'Create data.'

    def handle(self, *args, **options):
        create_persons()
```

Entendendo cada parte:

* `fake = Faker()`: uma única instância, criada no nível do módulo, usada por todas as funções.
* `gen_email()`: em vez de usar `fake.email()`, montamos o e-mail a partir do nome e do sobrenome da própria pessoa, assim os dados ficam coerentes (Alexis Aguilar → `alexis.aguilar@email.com`). O `slugify` passa para minúsculas, tira acentos e espaços. As anotações `: str` são só *type hints*.
* `get_person()`: gera os dados de **uma** pessoa e devolve um dicionário cujas chaves são os nomes dos campos do modelo.
* `create_persons()`: repete 100 vezes, criando objetos `Person(**data)` **sem salvar**, e guarda numa lista auxiliar. No fim, `bulk_create` grava todos de uma vez, numa única query de insert, em vez de 100 `save()`. O `progressbar(range(100), 'Persons')` envolve o `range` para mostrar o progresso.
* `Command.handle()`: é o que roda quando você chama `python manage.py create_data`.

## Registrando o Person no Admin

Para conferir os dados (e apagá-los quando quiser gerar de novo), registre o modelo no Admin. No `admin.py` da app, acrescente o `Person` no import e o registro no final do arquivo:

```python
# myproject/core/admin.py
from .models import Article, Category, Person

...

admin.site.register(Person)
```

## A view, a URL e o template

A lista de pessoas era uma view de função que só renderizava o template. Vamos trocá-la por uma `ListView` (vamos precisar dela na próxima dica, para a paginação):

```python
# myproject/core/views.py
from django.views.generic import ListView

from .models import Article, Person


class PersonListView(ListView):
    model = Person
    template_name = 'core/person_list.html'
```

A `ListView` busca `Person.objects.all()` e entrega a lista no contexto como `object_list` (e também como `person_list`).

Em `urls.py`, troque `v.person_list` por `v.PersonListView.as_view()`:

```python
# myproject/core/urls.py
from django.urls import path

from myproject.core import views as v

app_name = 'core'


urlpatterns = [
    path('', v.index, name='index'),
    path('persons/', v.PersonListView.as_view(), name='person_list'),
    path('persons/create/', v.person_create, name='person_create'),
    path('articles/', v.article_list, name='article_list'),
    path('articles/filter/', v.article_filter_list, name='article_filter_list'),
    path('articles/json/', v.article_json, name='article_json'),
]
```

E o template, com um formulário de busca (que vamos fazer funcionar na [Dica 38](038-django-paginacao-filtros.md)) e a tabela com os dados:

```html
<!-- myproject/core/templates/core/person_list.html -->
{% extends "base.html" %}

{% block content %}
  <h1>Lista de pessoas</h1>

  <div class="row">
    <div class="col">
      <form action="." method="GET">
        <div class="row">
          <div class="col">
            <input name="search" class="form-control mb-2" type="text" placeholder="Buscar...">
          </div>
          <div class="col-auto">
            <button class="btn btn-success mb-2" type="submit">OK</button>
            <button class="btn btn-link mb-2">Limpar</button>
          </div>
        </div>
      </form>
    </div>
  </div>

  <table class="table">
    <thead>
      <tr>
        <th>Nome</th>
        <th>Sobrenome</th>
        <th>E-mail</th>
        <th>Biografia</th>
        <th>Nascimento</th>
      </tr>
    </thead>
    <tbody>
      {% for object in object_list %}
        <tr>
          <td>{{ object.first_name }}</td>
          <td>{{ object.last_name }}</td>
          <td>{{ object.email }}</td>
          <td>{{ object.bio }}</td>
          <td>{{ object.birthday|date:"d/m/Y" }}</td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
{% endblock content %}
```

O filtro `date:"d/m/Y"` mostra a data de nascimento no formato brasileiro.

## Gerando os dados

Rode o comando:

```bash
python manage.py create_data
```

A barra de progresso vai enchendo até o fim:

```
Persons[############################################################] 100/100
```

Depois suba o servidor e acesse `http://localhost:8000/persons/`:

```bash
python manage.py runserver
```

A tabela mostra as 100 pessoas, em ordem de nome, com e-mails no formato `nome.sobrenome@email.com`, um parágrafo de biografia e a data de nascimento, por exemplo:

| Nome | Sobrenome | E-mail | Nascimento |
| --- | --- | --- | --- |
| Alexis | Aguilar | alexis.aguilar@email.com | 23/07/2011 |
| Alfred | Mills | alfred.mills@email.com | 06/07/2003 |
| Andrea | Brown | andrea.brown@email.com | 20/02/2008 |

No vídeo, os registros foram apagados pelo Admin (ação "Delete selected pessoas", já que o projeto está com `LANGUAGE_CODE = 'en-us'`) e o comando foi rodado de novo, gerando outras 100 pessoas diferentes. Cada execução do `create_data` acrescenta mais 100 registros.

## Conclusão

Com o Faker e um comando personalizado você popula o banco em segundos, com dados de aparência real. Na próxima dica, [Dica 38 - Paginação + Filtros](038-django-paginacao-filtros.md), vamos paginar essa lista e fazer a busca funcionar.

Observação: para gerar dados em português, passe o idioma na criação da instância: `Faker('pt_BR')`.
