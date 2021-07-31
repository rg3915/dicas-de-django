# 40 - Formulários: date, datetime, duration e templatetags de data

<a href="https://youtu.be/RxECiVYUh5U">
    <img src="../.gitbook/assets/youtube.png">
</a>


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



