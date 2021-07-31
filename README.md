# Dicas de Django

Clique aqui para ver as [dicas de Django](SUMMARY.md).


## This project was done with:

* Python 3.8.2
* Django 2.2.20


## How to run project?

* Clone this repository.
* Create virtualenv with Python 3.
* Active the virtualenv.
* Install dependences.
* Run the migrations.

```
git clone https://github.com/rg3915/dicas-de-django.git
cd dicas-de-django
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python contrib/env_gen.py
python manage.py migrate
```

## Este projeto foi feito com:

* Python 3.8.2
* Django 2.2.20


## Como rodar o projeto?

* Clone esse repositório.
* Crie um virtualenv com Python 3.
* Ative o virtualenv.
* Instale as dependências.
* Rode as migrações.

```
git clone https://github.com/rg3915/dicas-de-django.git
cd dicas-de-django
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python contrib/env_gen.py
python manage.py migrate
```





# 33 - Github cli

<a href="https://youtu.be/Y5VO3u2hp10">
    <img src="../../img/youtube.png">
</a>


https://cli.github.com/

```
gh auth login
gh repo clone rg3915/dicas-de-django
gh repo view
gh pr checks
gh pr create
gh pr status
gh pr merge
gh issue list
```

```
gh issue create --title "Github cli" --body "Experimentar Github cli https://cli.github.com" \
--label "enhancement" \
--assignee "@me"
```


```
gh issue create -t "Github cli" -b "Experimentar Github cli
https://cli.github.com" \
-l "enhancement" \
-a "@me"
```


Fechar issue

```
git commit -m 'Usando o github cli. close #34'
git push
```


# 34 - Django: custom template tags

<a href="https://youtu.be/ldMf8AW2h4Y">
    <img src="../../img/youtube.png">
</a>


https://docs.djangoproject.com/en/3.2/ref/templates/builtins/

### Built-in tags

```html
{% for obj in object_list %}
  <tr>
    <td>{{ forloop.counter }}</td>
    ...
    {% if obj.category.title == 'Django' %}
      <td>{{ obj.category }}</td>
    {% endif %}
  </tr>
{% endfor %}
```


### Built-in filter

```html
...
<td>{{ forloop.counter }}</td>
<td>{{ obj.title|slugify }}</td>
<td>{{ obj.title|truncatechars:13 }}</td>
<td>{{ obj.subtitle|safe|default:"---" }}</td>
<td>{{ obj.published_date|date:"d/m/Y" }}</td>
...
```

```
subtitle='<p>lorem</p>'
```


```html
{{ obj.subtitle|safe }}
```

### Writing custom template filters

#### Code layout

https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#code-layout

```
core
├── __init__.py
├── models.py
├── templatetags
│   ├── __init__.py
│   ├── model_name_tags.py
│   └── usergroup_tags.py
```

https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#writing-custom-template-filters

```
mkdir myproject/core/templatetags
touch myproject/core/templatetags/__init__.py
touch myproject/core/templatetags/usergroup_tags.py
```


```python
# usergroup_tags.py
from django import template

register = template.Library()


@register.filter('name_group')
def name_group(user):
    ''' Retorna o nome do grupo do usuário. '''
    _groups = user.groups.first()
    if _groups:
        return _groups.name
    return ''


@register.filter('has_group')
def has_group(user, group_name):
    ''' Verifica se este usuário pertence a um grupo. '''
    if user:
        groups = user.groups.all().values_list('name', flat=True)
        return True if group_name in groups else False
    return False
```

```html
{% load usergroup_tags %}

{% if request.user|has_group:"Autor" %}
É Autor.
{% endif %}
```

### Writing custom template tags

https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#writing-custom-template-tags

```
touch myproject/core/templatetags/model_name_tags.py
```

```python
# model_name_tags.py
from django import template

register = template.Library()


@register.simple_tag
def model_name(value):
    '''
    Django template filter which returns the verbose name of a model.
    '''
    if hasattr(value, 'model'):
        value = value.model

    return value._meta.verbose_name.title()


@register.simple_tag
def model_name_plural(value):
    '''
    Django template filter which returns the plural verbose name of a model.
    '''
    if hasattr(value, 'model'):
        value = value.model

    return value._meta.verbose_name_plural.title()
```

```html
{% load model_name_tags %}

Lista de {% model_name_plural model %}
```


# 35 - Django: passando usuário logado no formulário

<a href="https://youtu.be/69jPO_v6ldI">
    <img src="../../img/youtube.png">
</a>


```python
# forms.py
from django import forms

from .models import Person


class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = '__all__'

    def __init__(self, user=None, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        # my_field = MyModel.objects.filter(user=user)
        if user.is_authenticated:
            print(user)
        else:
            print('Não')
```


```python
# views.py
def person_create(request):
    template_name = 'core/person_form.html'
    # Não esquecer do request.user como primeiro parâmetro.
    form = PersonForm(request.user, request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('person:person_list')

    context = {'form': form}
    return render(request, template_name, context)
```

```python
# models.py
class Person(UuidModel):
    first_name = models.CharField('nome', max_length=50)
    last_name = models.CharField('sobrenome', max_length=50, null=True, blank=True)  # noqa E501
    email = models.EmailField(null=True, blank=True)

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

# 36 - Django: visualizando seus modelos com graph models

<a href="https://youtu.be/99dOVsDBUxg">
    <img src="../../img/youtube.png">
</a>

```
sudo apt-get install -y graphviz libgraphviz-dev pkg-config
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pygraphviz
pip uninstall pyparsing
pip install -Iv https://pypi.python.org/packages/source/p/pyparsing/pyparsing-1.5.7.tar.gz#md5=9be0fcdcc595199c646ab317c1d9a709
pip install pydot
pip install django-extensions
```

E em `INSTALLED_APPS`

```
INSTALLED_APPS = [
    ...
    'django_extensions',
    ...
]
```

Depois rode

```
python manage.py graph_models -e -g -l dot -o core.png core # only app core
python manage.py graph_models -a -g -o models.png # all
```

### core

![core.png](img/core.png)

### models

![models.png](img/models.png)


# 37 - Faker

<a href="https://youtu.be/ubgVHtLhubw">
    <img src="../../img/youtube.png">
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


# 38 - Django: Paginação + Filtros

<a href="https://youtu.be/eXipSfa-HOQ">
    <img src="../../img/youtube.png">
</a>


Primeiro vamos definir a paginação:

Edite `views.py`

```python
# views.py
class PersonListView(ListView):
    model = Person
    template_name = 'core/person_list.html'
    paginate_by = 5
```

Edite `person_list.html`

```html
<!-- person_list.html -->
...
{% include "includes/pagination.html" %}
```

Criar `includes/pagination.html`

```
mkdir myproject/core/templates/includes
touch myproject/core/templates/includes/pagination.html
```


```html
<!-- pagination.html -->
<!-- https://gist.github.com/rg3915/01ca76f099f431c24bc0536bef83076b -->
<!-- Use https://gist.github.com/rg3915/01ca76f099f431c24bc0536bef83076b#file-pagination02-html -->
<div class="row text-center">
  <div class="col-lg-12">
    <ul class="pagination">
      {% if page_obj.has_previous %}
        <li class="page-item"><a class="page-link" href="?page={{ page_obj.previous_page_number }}">&laquo;</a></li>
      {% endif %}

      {% for pg in page_obj.paginator.page_range %}
        <!-- Sempre mostra as 3 primeiras e 3 últimas páginas -->
          {% if pg == 1 or pg == 2 or pg == 3 or pg == page_obj.paginator.num_pages or pg == page_obj.paginator.num_pages|add:'-1' or pg == page_obj.paginator.num_pages|add:'-2' %}
            {% if page_obj.number == pg %}
              <li class="page-item active"><a class="page-link" href="?page={{ pg }}">{{ pg }}</a></li>
            {% else %}
              <li class="page-item"><a class="page-link" href="?page={{ pg }}">{{ pg }}</a></li>
            {% endif %}

          {% else %}

            {% if page_obj.number == pg %}
              <li class="page-item active"><a class="page-link" href="?page={{ pg }}">{{ pg }}</a></li>
            {% elif pg > page_obj.number|add:'-4' and pg < page_obj.number|add:'4' %} <!-- Mostra 3 páginas antes e 3 páginas depois da atual -->
              <li class="page-item"><a class="page-link" href="?page={{ pg }}">{{ pg }}</a></li>
            {% elif pg == page_obj.number|add:'-4' or pg == page_obj.number|add:'4' %}
              <li class="page-item"><a class="page-link" href="">...</a></li>
            {% endif %}
          {% endif %}
        {% endfor %}

        {% if page_obj.has_next %}
          <li class="page-item"><a class="page-link" href="?page={{ page_obj.next_page_number }}">&raquo;</a></li>
        {% endif %}
    </ul>
  </div>
</div>
```

Editar novamente `views.py`

```python
# views.py
from django.db.models import Q


class PersonListView(ListView):
    model = Person
    template_name = 'core/person_list.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = super(PersonListView, self).get_queryset()

        data = self.request.GET
        search = data.get('search')

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(bio__icontains=search)
            )

        return queryset
```

Criar templatetags `url_replace.py`

```
touch myproject/core/templatetags/url_replace.py
```

```python
# url_replace.py
# https://stackoverflow.com/a/62587351/802542
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    query.pop('page', None)
    query.update(kwargs)
    return query.urlencode()
```

E finalmente edite `pagination.html` trocando todos os `href`

```html
<!-- pagination.html -->
{% load url_replace %}
...
href="?{% url_replace page=page_obj.previous_page_number %}"
...
href="?{% url_replace page=pg %}"
...
href="?{% url_replace page=page_obj.next_page_number %}"
```


# 39 - Django Admin: display decorator (Django 3.2+)

<a href="https://youtu.be/lKEPuwBjHss">
    <img src="../../img/youtube.png">
</a>

https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#the-display-decorator

**IMPORTANTE:** Usei um [boilerplate](https://github.com/rg3915/dicas-de-django#11---django-boilerplate) para mostrar essa feature num projeto separado. Assista o video no YouTube.

O Django 3.2+ tem uma feature chamada `display` decorator.

Antigamente você fazia `short_description` assim:

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_published_date')

    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    get_published_date.short_description = 'Data de Publicação'
```

... e ainda funciona.

Mas a partir do Django 3.2+ você pode usar o `display` decorator.

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_published_date', 'is_published')

    # Django 3.2+
    @admin.display(description='Data de Publicação')
    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    @admin.display(boolean=True, ordering='-published_date', description='Publicado')
    def is_published(self, obj):
        return obj.published_date is not None
```


# 40 - Formulários: date, datetime, duration e templatetags de data

Vamos falar sobre como trabalhar com date, datetime, duration. Para isso vamos usar os seguintes links como referência:

https://docs.djangoproject.com/en/3.2/ref/forms/fields/

https://docs.djangoproject.com/en/3.2/ref/utils/#django.utils.dateparse.parse_duration

https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#date

https://github.com/igorescobar/jQuery-Mask-Plugin

https://igorescobar.github.io/jQuery-Mask-Plugin/docs.html


Lib JS via CDN.

`<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.mask/1.14.16/jquery.mask.min.js"></script>`


Mas antes vamos criar uma nova app chamada `travel`.

Entre na pasta `myproject` e crie a nova app.

```
cd myproject
python ../manage.py startapp travel
```

Configure em `INSTALLED_APPS`.

```python
INSTALLED_APPS = [
    ...
    'myproject.travel',
]
```

Em `models.py` crie uma classe `Travel`.

```python
# travel/models.py
cat << EOF > travel/models.py
from django.db import models


class Travel(models.Model):
    destination = models.CharField('destino', max_length=200)
    date_travel = models.DateField('data', null=True, blank=True)
    datetime_travel = models.DateTimeField('data/hora', null=True, blank=True)
    time_travel = models.TimeField('tempo', null=True, blank=True)
    duration_travel = models.DurationField('duração', null=True, blank=True)

    class Meta:
        ordering = ('destination',)
        verbose_name = 'viagem'
        verbose_name_plural = 'viagens'

    def __str__(self):
        return self.destination

EOF
```

Em seguida rode o comando

```
cd ..
python manage.py makemigrations
python manage.py migrate
```

Agora vamos editar o `urls.py` principal.

```python
# urls.py
urlpatterns = [
    ...
    path('travel/', include('myproject.travel.urls', namespace='travel')),
    ...
]

```

Edite `travel/urls.py`.

```python
# travel/urls.py
cat << EOF > myproject/travel/urls.py
from django.urls import path

from myproject.travel import views as v

app_name = 'travel'


urlpatterns = [
    path('', v.TravelListView.as_view(), name='travel_list'),
    path('create/', v.TravelCreateView.as_view(), name='travel_create'),
]

EOF
```

Edite `travel/views.py`.

```python
# travel/views.py
cat << EOF > myproject/travel/views.py
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import TravelForm
from .models import Travel


class TravelListView(ListView):
    model = Travel
    paginate_by = 10


class TravelCreateView(CreateView):
    model = Travel
    form_class = TravelForm
    success_url = reverse_lazy('travel:travel_list')

EOF
```

Crie a pasta

```
mkdir -p myproject/travel/templates/travel
```


Edite `travel/templates/travel/travel_list.html`

```html
cat << EOF > myproject/travel/templates/travel/travel_list.html
<!-- travel_list.html -->
{% extends "base.html" %}

{% block content %}
  <h1>
    Viagens
    <a class="btn btn-primary" href="{% url 'travel:travel_create' %}">Adicionar</a>
  </h1>
  <table class="table">
    <thead>
      <tr>
        <th>Destino</th>
        <th>Data</th>
        <th>Data e Hora</th>
        <th>Time</th>
        <th>Duração</th>
      </tr>
    </thead>
    <tbody>
      {% for object in object_list %}
        <!-- https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#date -->
        <tr>
          <td>{{ object.destination }}</td>
          <td>{{ object.date_travel|default:'---' }}</td>
          <td>{{ object.datetime_travel|default:'---' }}</td>
          <td>{{ object.time_travel|default:'---' }}</td>
          <td>{{ object.duration_travel|default:'---' }}</td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
  {% include "includes/pagination.html" %}
{% endblock content %}
EOF
```

Edite `travel/templates/travel/travel_form.html`

```html
cat << EOF > myproject/travel/templates/travel/travel_form.html
<!-- travel_form.html -->
{% extends "base.html" %}

{% block content %}
  <h1>Formulário</h1>
  <div class="cols-6">
    <form class="form-horizontal" action="." method="POST">
      <div class="col-sm-6">
        {% csrf_token %}
        {{ form.as_p }}
        <div class="form-group">
          <button type="submit" class="btn btn-primary">Salvar</button>
        </div>
      </div>
    </form>
  </div>
{% endblock content %}
EOF
```


Edite `travel/forms.py`

```python
cat << EOF > myproject/travel/forms.py
from django import forms

from .models import Travel


class TravelForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Travel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TravelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
EOF
```

Edite `myproject/core/templates/nav.html`

```html
<li class="nav-item">
    <a class="nav-link" href="{% url 'travel:travel_list' %}">Viagens</a>
</li>
```

Rode a aplicação e cadastre uma viagem com os seguintes dados:

```
Destino: Japão
Data: 2021-07-18
Data/hora: 2021-07-18 01:59
Tempo: 23:01:58
Duração: 26:01:02
```


Edite `travel/admin.py`

```python
cat << EOF > myproject/travel/admin.py
from django.contrib import admin

from .models import Travel


@admin.register(Travel)
class TravelAdmin(admin.ModelAdmin):
    list_display = (
        'destination',
        'date_travel',
        'datetime_travel',
        'time_travel',
        'duration_travel',
    )
    search_fields = ('destination',)

EOF
```

E abra o Admin.


Edite `travel/templates/travel/travel_list.html` novamente

Vejamos os templatetags.

```html
...
<td>{{ object.date_travel|date:"d/m/Y"|default:'---' }}</td>
<td>{{ object.datetime_travel|date:"d/m/Y H:i:s"|default:'---' }}</td>
<td>{{ object.time_travel|time:"H:i:s"|default:'---' }}</td>
...
```


Edite `travel/forms.py` novamente

```python
# travel/forms.py
...
class TravelForm(forms.ModelForm):

    date_travel = forms.DateField(
        label='Data',
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
            }),
        input_formats=('%Y-%m-%d',),
    )
    datetime_travel = forms.DateTimeField(
        label='Data/Hora',
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={
                'type': 'datetime-local',
            }),
        input_formats=('%Y-%m-%dT%H:%M',),
    )
    time_travel = forms.TimeField(
        label='Tempo',
        widget=forms.TimeInput(
            format='%H:%M',
            attrs={
                'type': 'time',
            }),
        input_formats=('%H:%M',),
    )
...
```


Edite `core/base.html`

```html
{% block css %}{% endblock css %}
...
<!-- jQuery -->
<script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>

{% block js %}{% endblock js %}
```


Edite `travel/templates/travel/travel_form.html` novamente

```html
{% block css %}
  <style>
    p {
      color: #000;
    }
    label.required:after {
      content: "*";
      color: red;
    }
  </style>
{% endblock css %}
...
{% block js %}

<!-- https://github.com/igorescobar/jQuery-Mask-Plugin -->
<!-- https://igorescobar.github.io/jQuery-Mask-Plugin/docs.html -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.mask/1.14.16/jquery.mask.min.js"></script>

<script>
  $('#id_duration_travel').mask('00:00:00');
</script>

{% endblock js %}
```

Compare o formato do datetime no templatetags e no formulário:

```
date:"d/m/Y H:i:s"       # templatags
format='%Y-%m-%dT%H:%M'  # forms (ISOformat)
```

https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#date



