# Dica 15 - Busca por data no frontend

**Versões usadas no vídeo:** Django 2.2.13, Python 3.8 e Bootstrap 4.0.
{: .versoes }

<a href="https://youtu.be/sqhQM5KUFHE">
    <img src="../.gitbook/assets/youtube.png">
</a>

Na [Dica 5](005-django-admin-date-range-filter.md) aplicamos um filtro de datas no Django Admin com o `django-daterange-filter`: você escolhe "de 14/06/2020 até 14/06/2020" e ele devolve os registros daquele dia. A pergunta que muita gente fez foi: como fazer isso na página da minha aplicação, no frontend?

Neste tutorial vamos colocar dois campos, **Data Inicial** e **Data Final**, na lista de artigos e filtrar os artigos publicados entre essas datas, com uma função na `views.py`. No caminho vamos ver por que a busca "de 15/08 até 15/08" não retorna nada, e duas formas de resolver isso.

## Pré-requisitos

O projeto é o mesmo das dicas anteriores (repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django)), com o app `core` dentro da pasta `myproject` e o `base.html` com Bootstrap 4 da [Dica 14](014-heranca-de-templates-e-arquivos-estaticos.md).

O modelo `Article` tem um campo `published_date` do tipo `DateTimeField`, ou seja, data **e hora**. Isso vai ser importante daqui a pouco.

```python
# myproject/core/models.py
class Article(models.Model):
    id = HashidAutoField(primary_key=True)
    title = models.CharField('título', max_length=200)
    subtitle = models.CharField('sub-título', max_length=200)
    slug = AutoSlugField(populate_from='title')
    category = models.ForeignKey(
        'Category',
        related_name='categories',
        verbose_name='categoria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    published_date = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'artigo'
        verbose_name_plural = 'artigos'

    def __str__(self):
        return self.title
```

(O `HashidAutoField` e o `AutoSlugField` vêm de dicas anteriores; para esta dica só importam `title`, `subtitle` e `published_date`.)

A rota e a view da lista de artigos já existem:

```python
# myproject/core/urls.py
from django.urls import path
from myproject.core import views as v


app_name = 'core'


urlpatterns = [
    path('', v.index, name='index'),
    path('persons/', v.person_list, name='person_list'),
    path('articles/', v.article_list, name='article_list'),
]
```

```python
# myproject/core/views.py
def article_list(request):
    template_name = 'core/article_list.html'
    object_list = Article.objects.all()
    context = {'object_list': object_list}
    return render(request, template_name, context)
```

No vídeo havia alguns artigos cadastrados: "Dicas de Python" e "Dicas de Python 2", publicados em 15 de agosto de 2020, e "Django Admin", "Django Autoslug", "Django Boilerplate" e "Django extensions", publicados em 14 de junho de 2020.

Também vamos usar a função `parse` da biblioteca `python-dateutil`. Se ela não estiver instalada no seu ambiente:

```bash
pip install python-dateutil
```

## O template com os campos de data

No `article_list.html`, ao lado do título, colocamos um formulário com dois `input` do tipo `date`:

```html
<!-- myproject/core/templates/core/article_list.html -->
{% extends "base.html" %}

{% block content %}
  <div class="row">
    <div class="col-md-4">
      <h1>Lista de Artigos</h1>
    </div>
    <div class="col-md-8">
      <form class="form-inline my-2 my-lg-0 pull-right">
        <label>Data Inicial</label>
        <input class="form-control ml-sm-2 mr-sm-2" name='start_date' type="date">
        <label>Data Final</label>
        <input class="form-control ml-sm-2 mr-sm-2" name='end_date' type="date">
        <button class="btn btn-primary my-2 my-sm-0" type="submit">OK</button>
      </form>
    </div>
  </div>

  <table class="table">
    <thead>
      <tr>
        <th>Título</th>
        <th>Sub-título</th>
        <th>Data de publicação</th>
      </tr>
    </thead>
    <tbody>
      {% for object in object_list %}
        <tr>
          <td>{{ object.title }}</td>
          <td>{{ object.subtitle }}</td>
          <td>{{ object.published_date }}</td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
{% endblock content %}
```

Os pontos importantes:

* O `<form>` não tem `method`, então usa o padrão, **GET**: ao clicar em OK, os valores vão na URL, assim: `/articles/?start_date=2020-08-15&end_date=2020-08-16`.
* O atributo **`name`** é o que importa para o Django: é por ele (`start_date` e `end_date`) que vamos pegar os valores na view. Não precisa de `id`.
* O `type="date"` faz o navegador mostrar o seletor de data (o calendário). O valor exibido segue o idioma do navegador (`dd/mm/aaaa`), mas o valor enviado é sempre no formato `AAAA-MM-DD`.
* As classes `ml-sm-2` e `mr-sm-2` do Bootstrap dão uma margem à esquerda e à direita, para os campos ficarem alinhados.

Esse campo de busca da navbar (o "Search" do topo) não tem nada a ver com isso; ele é só do menu.

## Lendo as datas na view

Na view, pegamos os valores com `request.GET.get()`, usando o mesmo nome do atributo `name`:

```python
start_date = request.GET.get('start_date')
end_date = request.GET.get('end_date')
```

O `.get()` devolve `None` se o parâmetro não veio na URL, então só aplicamos o filtro se as duas datas foram preenchidas. Para conferir que os valores estão chegando, dá para fazer um `print` antes:

```python
if start_date and end_date:
    print(start_date)
    print(end_date)
```

Escolhendo 15/08/2020 nos dois campos e clicando em OK, o terminal do `runserver` mostra:

```
2020-08-15
2020-08-15
```

## Filtrando com range

O lookup `__range` (com dois underlines) recebe uma lista com o início e o fim do intervalo:

```python
if start_date and end_date:
    object_list = object_list.filter(
        published_date__range=[start_date, end_date]
    )
```

Buscando de 15/08/2020 até 16/08/2020, a página mostra os dois artigos publicados em 15 de agosto. Funciona.

## O problema: de 15/08 até 15/08

Agora o caso mais natural: quero os artigos de **um dia só**, então coloco 15/08/2020 nas duas datas. Resultado: **nenhum artigo**.

O motivo é que `published_date` é um `DateTimeField`. Quando comparamos com a string `'2020-08-15'`, o Django a entende como `2020-08-15 00:00:00`. O filtro vira "publicado entre 15/08 à meia-noite e 15/08 à meia-noite", e os artigos foram publicados às 7h14 e 7h27, fora desse intervalo.

No terminal ainda aparece um aviso, porque o projeto usa `USE_TZ = True` e as datas chegaram sem fuso horário:

```
RuntimeWarning: DateTimeField Article.published_date received a naive datetime (2020-08-15 00:00:00) while time zone support is active.
```

## Solução 1: somar um dia na data final

A solução mostrada no vídeo é somar um dia à data final, para o intervalo ir até a meia-noite do dia seguinte. Só que não dá para somar um número a uma string, e o valor que vem do `request.GET` é sempre string. Então primeiro convertemos a string em data com o `parse` do `dateutil`, e depois somamos um `timedelta` de 1 dia:

```python
# myproject/core/views.py
from dateutil.parser import parse
from datetime import timedelta
from django.shortcuts import render
from .models import Article


def article_list(request):
    template_name = 'core/article_list.html'
    object_list = Article.objects.all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        # Converte em data e adiciona um dia.
        end_date = parse(end_date) + timedelta(1)
        object_list = object_list.filter(
            published_date__range=[start_date, end_date]
        )

    context = {'object_list': object_list}
    return render(request, template_name, context)
```

* `parse('2020-08-15')` devolve `datetime(2020, 8, 15, 0, 0)`.
* `timedelta(1)` é um intervalo de 1 dia, então `end_date` passa a ser `2020-08-16 00:00:00`.

Agora a busca de 15/08/2020 até 15/08/2020 retorna os dois artigos de 15 de agosto, e de 14/06/2020 até 14/06/2020 retorna os artigos de 14 de junho.

## Solução 2: usar `__date__range`

Depois do vídeo, o [@walisonfilipe](https://twitter.com/walisonfilipe) mostrou um jeito mais simples. Pra não precisar fazer o

```python
end_date = parse(end_date) + timedelta(1)
```

basta acrescentar `date` antes do `range`, daí fica assim:

```python
object_list = object_list.filter(
    published_date__date__range=[start_date, end_date]
)
```

O lookup `__date` pega só a parte de data do `DateTimeField` (descarta a hora), e o `__range` compara data com data. Assim "de 15/08 até 15/08" significa exatamente "o dia 15/08 inteiro", e a view nem precisa mais do `parse` e do `timedelta`:

```python
# myproject/core/views.py
def article_list(request):
    template_name = 'core/article_list.html'
    object_list = Article.objects.all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        object_list = object_list.filter(
            published_date__date__range=[start_date, end_date]
        )

    context = {'object_list': object_list}
    return render(request, template_name, context)
```

## Testando

O código foi rodado com Django 2.2 e Python 3.8, com artigos em 15/08/2020 (7h14 e 7h27) e em 14/06/2020:

| Busca | Só `__range` | `parse` + `timedelta(1)` | `__date__range` |
|---|---|---|---|
| 15/08 até 16/08 | 2 artigos | 2 artigos | 2 artigos |
| 15/08 até 15/08 | nenhum | 2 artigos | 2 artigos |
| 14/06 até 14/06 | nenhum | 1 artigo | 1 artigo |

Repare numa diferença sutil: com o `timedelta`, a data final vira meia-noite do dia seguinte, então um artigo publicado exatamente às 00:00:00 do dia seguinte também entraria. Com o `__date__range` isso não acontece.

Agradecimentos a [@walisonfilipe](https://twitter.com/walisonfilipe)
