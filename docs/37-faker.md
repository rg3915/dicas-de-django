# 37 - Faker

<a href="https://youtu.be/ubgVHtLhubw">
    <img src="../.gitbook/assets/youtube.png">
</a>


https://faker.readthedocs.io/en/master/

O Faker é uma biblioteca ideal para popular o seu banco de dados com dados aleatórios.

Vamos trabalhar em cima do model `Person`, e acrescentar mais uns campos no modelo.

```python
# models.py
class Person(UuidModel):
    first_name = models.CharField('nome', max_length=50)
    last_name = models.CharField('sobrenome', max_length=50, null=True, blank=True)  # noqa E501
    email = models.EmailField(null=True, blank=True)
    bio = models.TextField('biografia', null=True, blank=True)
    birthday = models.DateField('nascimento', null=True, blank=True)
```

Instale o Faker

```
pip install faker
```

E vamos criar um novo comando em `management`

```
touch myproject/core/management/commands/create_data.py
```

```python
# create_data.py
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
    last_name = fake.first_name()
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

Editar `admin.py`

```
admin.site.register(Person)
```

Criar `progress_bar.py`

```
mkdir myproject/utils
touch myproject/utils/progress_bar.py
```

```python
# progress_bar.py
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

Editar `views.py`

```python
# views.py
from django.views.generic import ListView


class PersonListView(ListView):
    model = Person
    template_name = 'core/person_list.html'
```

Editar `urls.py`

```python
# urls.py
...
path('persons/', v.PersonListView.as_view(), name='person_list'),
```

Editar `person_list.html`

```html
# person_list.html
{% extends "base.html" %}

{% block content %}
  <h1>Lista de pessoas</h1>

  <div class="row">
    <div class="col">
      <form action="." method="GET">
        <div class="row">
          <div class="col">
            <input name="search" class="form-control mb-2" type="text" placeholder="Buscar..." />
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
