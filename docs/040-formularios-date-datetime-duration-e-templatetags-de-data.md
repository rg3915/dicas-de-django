# Dica 40 - Formulários: date, datetime, duration e templatetags de data

**Versões usadas no vídeo:** Django 2.2.24, Python 3.8, Bootstrap 4, jQuery 3.4.1 e jQuery Mask Plugin 1.14.16.
{: .versoes }

<a href="https://youtu.be/RxECiVYUh5U">
    <img src="../.gitbook/assets/youtube.png">
</a>


**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`). Se copiar código de lá, remova a `\`.

![](../.gitbook/assets/tags.png)


Vamos ver como trabalhar com datas e tempos no Django: os campos `DateField`, `DateTimeField`, `TimeField` e `DurationField` no modelo, como formatá-los no template com os filtros `date` e `time`, e como deixar o formulário fácil de preencher com os widgets nativos do HTML5 (`type="date"`, `type="datetime-local"` e `type="time"`) e uma máscara de jQuery para a duração.

Links de referência:

* [https://docs.djangoproject.com/en/3.2/ref/forms/fields/](https://docs.djangoproject.com/en/3.2/ref/forms/fields/)
* [https://docs.djangoproject.com/en/3.2/ref/utils/#django.utils.dateparse.parse_duration](https://docs.djangoproject.com/en/3.2/ref/utils/#django.utils.dateparse.parse_duration)
* [https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#date](https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#date)
* [https://github.com/igorescobar/jQuery-Mask-Plugin](https://github.com/igorescobar/jQuery-Mask-Plugin)
* [https://igorescobar.github.io/jQuery-Mask-Plugin/docs.html](https://igorescobar.github.io/jQuery-Mask-Plugin/docs.html)

Lib JS via CDN:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.mask/1.14.16/jquery.mask.min.js"></script>
```

## Pré-requisitos

Continuamos o projeto do repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django): o pacote `myproject` com a app `core`, um `base.html` com Bootstrap 4, um `nav.html` com a barra de navegação e o template de paginação `includes/pagination.html` criado na [Dica 38 - Paginação + Filtros](038-django-paginacao-filtros.md). O projeto usa `LANGUAGE_CODE = 'en-us'`, `TIME_ZONE = 'UTC'` e `USE_TZ = True`.

## Criando a app travel

Vamos criar uma app nova, `travel` (viagens). Entre na pasta `myproject` e crie a app a partir dali, para ela ficar dentro do pacote:

```bash
cd myproject
python ../manage.py startapp travel
cd ..
```

Configure em `INSTALLED_APPS`:

```python
# myproject/settings.py
INSTALLED_APPS = [
    ...
    'django_filters',
    'myproject.travel',
]
```

## O modelo Travel

Em `models.py` crie a classe `Travel`, com um campo de cada tipo de data e tempo:

```python
# myproject/travel/models.py
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
```

* `DateField`: só a data (no Python, um `datetime.date`).
* `DateTimeField`: data e hora (`datetime.datetime`).
* `TimeField`: só a hora (`datetime.time`).
* `DurationField`: um intervalo de tempo (`datetime.timedelta`). Diferente do `TimeField`, ele pode passar de 24 horas: `26:01:02` é 1 dia, 2 horas, 1 minuto e 2 segundos.

Em seguida rode:

```bash
python manage.py makemigrations
python manage.py migrate
```

```
Migrations for 'travel':
  myproject/travel/migrations/0001_initial.py
    - Create model Travel
```

No vídeo, o `makemigrations` acusou primeiro um conflito em migrações antigas da app `core` (`Conflicting migrations detected; multiple leaf nodes`), que vinham de branches diferentes do repositório. A solução é a que o próprio Django sugere, `python manage.py makemigrations --merge`, respondendo `y`. Isso é particular daquele repositório; num projeto sem conflito, os dois comandos acima bastam.

## URLs e views

No `urls.py` principal, inclua as URLs da app com o namespace `travel`:

```python
# myproject/urls.py
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('myproject.core.urls', namespace='core')),
    path('travel/', include('myproject.travel.urls', namespace='travel')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

Crie o `travel/urls.py`:

```python
# myproject/travel/urls.py
from django.urls import path

from myproject.travel import views as v

app_name = 'travel'


urlpatterns = [
    path('', v.TravelListView.as_view(), name='travel_list'),
    path('create/', v.TravelCreateView.as_view(), name='travel_create'),
]
```

E as views, uma lista paginada e um formulário de cadastro, as duas com class based views:

```python
# myproject/travel/views.py
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
```

Sem `template_name`, as views procuram os templates padrão `travel/travel_list.html` e `travel/travel_form.html`.

## O formulário (primeira versão)

```python
# myproject/travel/forms.py
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
```

* `required_css_class = 'required'`: o Django acrescenta a classe `required` no `<label>` dos campos obrigatórios. Vamos usar isso para colocar um asterisco vermelho.
* O `__init__` percorre todos os campos e coloca a classe `form-control` do Bootstrap em cada widget.

## Os templates

Crie a pasta e os dois arquivos:

```bash
mkdir -p myproject/travel/templates/travel
touch myproject/travel/templates/travel/travel_list.html
touch myproject/travel/templates/travel/travel_form.html
```

A lista, por enquanto mostrando os valores sem formatação nenhuma:

```html
<!-- myproject/travel/templates/travel/travel_list.html -->
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
          <td>{{ object.date_travel }}</td>
          <td>{{ object.datetime_travel }}</td>
          <td>{{ object.time_travel }}</td>
          <td>{{ object.duration_travel }}</td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
  {% include "includes/pagination.html" %}
{% endblock content %}
```

O formulário:

```html
<!-- myproject/travel/templates/travel/travel_form.html -->
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
```

E um link para a lista de viagens na barra de navegação:

```html
<!-- myproject/core/templates/nav.html -->
...
<li class="nav-item">
    <a class="nav-link" href="{% url 'travel:travel_list' %}">Viagens</a>
</li>
...
```

## Cadastrando pelo Admin

Para ter dados para olhar, registre o modelo no Admin:

```python
# myproject/travel/admin.py
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
```

Rode a aplicação, abra o Admin e cadastre uma viagem. O Admin já tem os widgets de calendário e relógio, com os atalhos "Today" e "Now". No vídeo foram usados estes dados:

```
Destino: Japão
Data: 2021-07-19
Data/hora: 2021-07-19 09:18:55
Tempo: 09:19:01
Duração: 26:01:02
```

Repare que a duração aceita mais de 24 horas: `26:01:02` é guardado como 1 dia, 2 horas, 1 minuto e 2 segundos.

Abra `/travel/`. Sem nenhuma formatação, o Django usa os formatos padrão do idioma `en-us`:

| Destino | Data | Data e Hora | Time | Duração |
| --- | --- | --- | --- | --- |
| Japão | July 19, 2021 | July 19, 2021, 9:18 a.m. | 9:19 a.m. | 1 day, 2:01:02 |

## Os filtros de template date e time

Para mostrar as datas no formato brasileiro, use os filtros [`date`](https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#date) e `time`. Edite `travel_list.html` novamente:

```html
<!-- myproject/travel/templates/travel/travel_list.html -->
...
<td>{{ object.destination }}</td>
<td>{{ object.date_travel|date:"d/m/Y"|default:"---" }}</td>
<td>{{ object.datetime_travel|date:"d/m/Y H:i:s"|default:"---" }}</td>
<td>{{ object.time_travel|time:"H:i:s"|default:"---" }}</td>
<td>{{ object.duration_travel|default:"---" }}</td>
...
```

Os caracteres de formato usados:

| Caractere | Significado | Exemplo |
| --- | --- | --- |
| `d` | dia do mês com 2 dígitos | `19` |
| `m` | mês com 2 dígitos | `07` |
| `Y` | ano com 4 dígitos | `2021` |
| `H` | hora de 00 a 23 | `09` |
| `i` | minutos | `18` |
| `s` | segundos | `55` |

O filtro `default:"---"` mostra `---` quando o campo está vazio (lembre que todos os campos de data do modelo são opcionais). A duração ficou sem filtro: o formato padrão (`1 day, 2:01:02`) é bom o suficiente. Agora a tabela fica assim:

| Destino | Data | Data e Hora | Time | Duração |
| --- | --- | --- | --- | --- |
| Japão | 19/07/2021 | 19/07/2021 09:18:55 | 09:19:01 | 1 day, 2:01:02 |

## O problema do formulário

Acesse `/travel/create/`. Os campos de data e hora são simples caixas de texto, e você precisa saber o formato exato que o Django espera. No vídeo foi cadastrada uma viagem assim:

```
Destino: Itália
Data: 2021-07-20
Data/hora: 2021-07-20 01:59
Tempo: 23:01:58
Duração: 27:01:02
```

Funciona (a lista mostra `20/07/2021`, `20/07/2021 01:59:00`, `23:01:58` e `1 day, 3:01:02`), mas ninguém quer digitar data assim.

## Widgets de data e hora do HTML5

O HTML5 tem inputs próprios para datas e horas, com calendário e relógio do navegador. Para usá-los, declare os campos no formulário com o widget certo. Edite `travel/forms.py`:

```python
# myproject/travel/forms.py
from django import forms

from .models import Travel


class TravelForm(forms.ModelForm):
    required_css_class = 'required'

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

    class Meta:
        model = Travel
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TravelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
```

Para cada campo há três peças:

* `attrs={'type': ...}`: muda o `type` do `<input>`, que é o que faz o navegador mostrar o seletor de data (`date`), de data e hora (`datetime-local`) ou de hora (`time`).
* `format` no widget: o formato em que o Django **escreve** o valor no `<input>` (por exemplo, ao editar um registro). Precisa ser o formato que o HTML5 entende: `2021-07-19` para `date`, `2021-07-19T06:32` para `datetime-local` (com a letra `T` literal separando data e hora) e `06:32` para `time`.
* `input_formats`: os formatos que o Django aceita ao **ler** o valor enviado pelo navegador. São os mesmos, porque o navegador envia nesse formato, independentemente de como mostra a data na tela.

Como estes campos foram declarados à mão no formulário, eles são obrigatórios (o padrão de um campo de formulário é `required=True`), mesmo sendo opcionais no modelo. Por isso os rótulos Data, Data/Hora e Tempo passam a ter o asterisco.

No vídeo, o teste foi feito no Chrome, onde o `datetime-local` mostra o seletor de data e hora. Na época (julho de 2021), o Firefox ainda não tinha suporte a esse tipo de input; ele chegou na versão 93 do Firefox.

Teste cadastrando, por exemplo, Canadá com data 19/07/2021, data/hora 19/07/2021 06:28 e tempo 08:16, escolhendo tudo pelos seletores.

## Blocos de CSS e JS no base.html

O `DurationField` não tem um widget nativo no HTML. Para ajudar o usuário, vamos colocar uma máscara no campo com o [jQuery Mask Plugin](https://github.com/igorescobar/jQuery-Mask-Plugin). Antes, prepare o `base.html` com um bloco para CSS no `<head>`, o jQuery e um bloco para JS no fim do `<body>`:

```html
<!-- myproject/core/templates/base.html -->
{% load static %}
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="shortcut icon" href="https://www.djangoproject.com/favicon.ico">
  <!-- Bootstrap core CSS -->
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
  <!-- Font-awesome -->
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
  <title>Dicas de Django</title>

  <link rel="stylesheet" href="{% static 'css/style.css' %}">

  {% block css %}{% endblock css %}

  <style>
    body {
      margin-top: 60px;
    }
  </style>
</head>

<body>
  <div class="container">

    {% include "nav.html" %}

    {% block content %}{% endblock content %}
  </div>

  <!-- { include "footer.html" %} -->

  <!-- jQuery -->
  <script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>

  <script src="{% static 'js/main.js' %}"></script>

  {% block js %}{% endblock js %}

</body>

</html>
```

O jQuery precisa vir **antes** do `{% block js %}`, porque o plugin de máscara depende dele. No vídeo, a máscara só funcionou depois de incluir o jQuery no `base.html`.

## A máscara da duração e o asterisco dos obrigatórios

A versão final do `travel_form.html`:

```html
<!-- myproject/travel/templates/travel/travel_form.html -->
{% extends "base.html" %}

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

{% block js %}
<!-- https://github.com/igorescobar/jQuery-Mask-Plugin -->
<!-- https://igorescobar.github.io/jQuery-Mask-Plugin/docs.html -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.mask/1.14.16/jquery.mask.min.js"></script>

<script>
  $('#id_duration_travel').mask('00:00:00');
</script>

{% endblock js %}
```

* No bloco `css`, `label.required:after` coloca um `*` vermelho depois do rótulo de todo campo obrigatório (a classe `required` vem do `required_css_class` do formulário). O `p { color: #000; }` foi acrescentado no vídeo para deixar o texto do formulário preto, porque algum CSS do projeto estava deixando os campos vermelhos.
* No bloco `js`, o plugin é carregado pela CDN e a máscara é aplicada no campo de duração. O Django gera o `id` dos campos como `id_` + nome do campo, por isso `#id_duration_travel`. Na máscara, cada `0` aceita um dígito, então o campo só aceita algo como `49:01:59`.

Cadastre uma viagem, por exemplo Portugal, data 19/07/2021, data/hora 19/07/2021 06:32, tempo 07:35 e duração `49:01:59`. Na lista, a duração aparece como `2 days, 1:01:59`: o Django converte o texto em `timedelta` (com a função [`parse_duration`](https://docs.djangoproject.com/en/3.2/ref/utils/#django.utils.dateparse.parse_duration)), e 49 horas viram 2 dias e 1 hora.

## Formato no template x formato no formulário

Compare o formato do datetime no filtro de template e no formulário:

```
date:"d/m/Y H:i:s"       # templatetags
format='%Y-%m-%dT%H:%M'  # forms (ISO format)
```

São duas sintaxes diferentes:

* no template, o filtro `date` usa os caracteres de formato do Django (parecidos com os do PHP), sem `%`: `d`, `m`, `Y`, `H`, `i` (minutos) e `s` (segundos);
* no formulário, `format` e `input_formats` usam os códigos do `strftime` do Python, com `%`: `%Y`, `%m`, `%d`, `%H`, `%M` (minutos, com M maiúsculo) e `%S` (segundos). E o `T` é literal, exigido pelo formato ISO do `datetime-local`.

A tabela completa dos caracteres do filtro está em [https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#date](https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#date).

## Conclusão

Os campos de data do modelo são simples; o trabalho está na interface. Com os filtros `date` e `time` você controla como as datas aparecem, e com os widgets do HTML5 (definindo `type`, `format` e `input_formats`) o usuário escolhe data e hora no seletor do navegador, sem precisar conhecer o formato que o Django espera. Para a duração, que não tem widget nativo, a máscara de jQuery resolve.
