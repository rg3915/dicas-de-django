# Dica 34 - Django: custom template tags

**Versões usadas no vídeo:** Django 2.2.20, Python 3.8 e Bootstrap 4.
{: .versoes }

<a href="https://youtu.be/ldMf8AW2h4Y">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`). Se copiar código de lá, remova a `\`.

![](../.gitbook/assets/tags.png)

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

A linguagem de templates do Django tem dois tipos de recurso:

* **tags**, escritas com `{% ... %}`, que executam alguma lógica (`for`, `if`, `block`, `url`...);
* **filtros**, escritos com `|` dentro de `{{ ... }}`, que transformam um valor (`date`, `slugify`, `default`...).

Nesta dica vamos ver alguns tags e filtros nativos (*built-in*) na prática e depois criar os nossos: dois filtros, para saber o grupo do usuário, e duas template tags, para mostrar o nome do modelo.

A lista completa de tags e filtros nativos está na documentação:

[https://docs.djangoproject.com/en/3.2/ref/templates/builtins/](https://docs.djangoproject.com/en/3.2/ref/templates/builtins/)

## Pré-requisitos

Continuamos o projeto das dicas anteriores: o app `core` dentro de `myproject`, com o modelo `Article` (com os campos `title`, `subtitle`, `category`, `published_date`, `status` e `user`, da [Dica 31](031-django-admin-pegando-usuario-logado-no-admin.md)), a view `article_list` e o template `core/article_list.html`, que estende um `base.html` com Bootstrap 4 (das dicas [14](014-heranca-de-templates-e-arquivos-estaticos.md) e [15](015-busca-por-data-no-frontend.md)).

O template, antes desta dica, mostrava só título, subtítulo e data:

```html
<!-- myproject/core/templates/core/article_list.html (antes) -->
<tbody>
  {% for obj in object_list %}
    <tr>
      <td>{{ obj.title }}</td>
      <td>{{ obj.subtitle }}</td>
      <td>{{ obj.published_date }}</td>
    </tr>
  {% endfor %}
</tbody>
```

## Built-in tags

A tag `for` percorre uma lista; dentro dela, a variável `forloop.counter` dá o número da volta (começando em 1), ótima para numerar as linhas. A tag `if` testa uma condição:

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

Com isso, a coluna da categoria só aparece nos artigos cuja categoria é "Django".

## Built-in filters

Agora alguns filtros:

```html
...
<td>{{ forloop.counter }}</td>
<td>{{ obj.title|slugify }}</td>
<td>{{ obj.title|truncatechars:13 }}</td>
<td>{{ obj.subtitle|safe|default:"---" }}</td>
<td>{{ obj.published_date|date:"d/m/Y" }}</td>
...
```

* `slugify`: transforma o texto em slug, tudo minúsculo, sem acentos e com hífens no lugar dos espaços ("Barra de progresso" vira `barra-de-progresso`).
* `truncatechars:13`: corta o texto em 13 caracteres, terminando com reticências ("Django Admin…").
* `safe`: marca o texto como seguro, ou seja, o HTML dele é renderizado em vez de aparecer escapado. Por exemplo, um artigo com

  ```
  subtitle='<p>lorem</p>'
  ```

  com `{{ obj.subtitle }}` aparece literalmente `<p>lorem</p>` na página. Com

  ```html
  {{ obj.subtitle|safe }}
  ```

  aparece um parágrafo com "lorem". Use `safe` só com conteúdo em que você confia.
* `default:"---"`: se o valor for vazio, mostra `---`. Os filtros podem ser encadeados, como em `safe|default:"---"`.
* `date:"d/m/Y"`: formata a data como dia/mês/ano com quatro dígitos (`20/02/2021`).

Para a categoria, usamos `else` e `default` juntos: se a categoria não for "Django", mostra a categoria ou `---` quando o artigo não tiver categoria.

```html
{% if obj.category.title == 'Django' %}
  <td>{{ obj.category }}</td>
{% else %}
  <td>{{ obj.category|default:"---" }}</td>
{% endif %}
```

## Writing custom template filters

### Code layout

[https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#code-layout](https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#code-layout)

Tags e filtros personalizados ficam numa pasta `templatetags` dentro do app, no mesmo nível do `models.py`. A pasta precisa de um `__init__.py` (para ser um pacote Python), e cada arquivo dentro dela é uma biblioteca, carregada no template pelo nome do arquivo:

```
core
├── __init__.py
├── models.py
├── templatetags
│   ├── __init__.py
│   ├── model_name_tags.py
│   └── usergroup_tags.py
```

O app tem que estar no `INSTALLED_APPS` e, depois de criar a pasta `templatetags`, **reinicie o servidor**, senão o Django não encontra as bibliotecas novas.

### Os filtros de grupo do usuário

[https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#writing-custom-template-filters](https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#writing-custom-template-filters)

```bash
mkdir myproject/core/templatetags
touch myproject/core/templatetags/__init__.py
touch myproject/core/templatetags/usergroup_tags.py
```

```python
# myproject/core/templatetags/usergroup_tags.py
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

* `register = template.Library()`: toda biblioteca de tags e filtros precisa dessa variável, com esse nome; é nela que registramos os filtros.
* `@register.filter('name_group')`: registra a função como filtro com o nome `name_group`. Um filtro recebe o valor que está antes do `|` (aqui, o usuário) e devolve o valor transformado. `name_group` devolve o nome do primeiro grupo do usuário, ou uma string vazia se ele não tiver grupo.
* `has_group` recebe dois argumentos: o valor antes do `|` (o usuário) e o argumento depois dos dois-pontos (o nome do grupo), como em `user|has_group:"Autor"`. O `values_list('name', flat=True)` devolve uma lista simples com os nomes dos grupos, e verificamos se o nome pedido está nela.
* O `if user:` é necessário porque nem todo artigo tem usuário. Sem ele, um artigo com `user` vazio daria erro (`None` não tem `groups`). No vídeo, essa verificação foi acrescentada depois, justamente por causa disso.

### Testando os filtros

No Admin, crie um grupo chamado **Autor** (em *Authentication and Authorization > Groups*) e coloque nele o usuário `admin`. Associe alguns artigos ao usuário `admin`.

No template, carregue a biblioteca com `{% load %}` (o nome é o do arquivo, sem `.py`) e use o filtro. Por exemplo, para saber se o usuário logado é autor:

```html
{% load usergroup_tags %}

{% if request.user|has_group:"Autor" %}
É Autor.
{% endif %}
```

O `request.user` é o usuário logado. Na lista de artigos, porém, queremos o grupo do **autor de cada artigo**, então usamos `obj.user` e mostramos o nome do grupo com `name_group`:

```html
<td>
  {% if obj.user|has_group:"Autor" %}
    {{ obj.user|name_group }}
  {% endif %}
</td>
```

A coluna **Grupo** mostra "Autor" nos artigos do usuário `admin` e fica vazia nos outros.

## Writing custom template tags

[https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#writing-custom-template-tags](https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/#writing-custom-template-tags)

Agora duas template tags simples, que devolvem o nome do modelo (o `verbose_name` e o `verbose_name_plural` definidos no `Meta`). Assim o título da página ("Lista de Artigos") vem do próprio modelo.

```bash
touch myproject/core/templatetags/model_name_tags.py
```

```python
# myproject/core/templatetags/model_name_tags.py
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

* `@register.simple_tag`: registra uma tag simples. Ela é usada como `{% model_name_plural model %}`: recebe os argumentos escritos depois do nome e o valor que ela devolve é escrito no template.
* `if hasattr(value, 'model')`: se o valor recebido for um queryset ou um formulário (que têm o atributo `model`), pegamos o modelo dele. Assim a tag funciona com o modelo, com um queryset ou com um `ModelForm`.
* `value._meta.verbose_name` e `value._meta.verbose_name_plural`: os nomes definidos no `Meta` do modelo (`'artigo'` e `'artigos'`). O `.title()` deixa a primeira letra maiúscula: "Artigos".

### Passando o modelo no contexto

A tag precisa receber o modelo. Na view, acrescente a chave `model` ao contexto:

```python
# myproject/core/views.py
from django.shortcuts import render
from .models import Article


def article_list(request):
    template_name = 'core/article_list.html'
    object_list = Article.objects.all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        # Converte em data e adiciona um dia.
        # end_date = parse(end_date) + timedelta(1)
        # Usando date antes de range não precisa do timedelta.
        object_list = object_list.filter(
            published_date__date__range=[start_date, end_date]
        )

    context = {'object_list': object_list, 'model': Article}
    return render(request, template_name, context)
```

(O filtro por data é da [Dica 15](015-busca-por-data-no-frontend.md); o que muda aqui é só o `'model': Article` no contexto.)

No template:

```html
{% load model_name_tags %}

Lista de {% model_name_plural model %}
```

Atenção a dois erros que aparecem no vídeo:

* no `{% load %}` vai o nome do **arquivo** (`model_name_tags`), e não o nome da tag. `{% load model_name_plural model %}` dá erro dizendo que `model_name_plural` não é uma biblioteca registrada;
* se a view não mandar `model` no contexto, a tag não tem o que mostrar e o título fica só "Lista de".

Com tudo certo, o título fica "Lista de Artigos". Trocando por `{% model_name model %}`, fica no singular: "Lista de Artigo".

## O template completo

```html
<!-- myproject/core/templates/core/article_list.html -->
{% extends "base.html" %}
{% load usergroup_tags %}
{% load model_name_tags %}

{% block content %}
  <div class="row">
    <div class="col-md-4">
      <h1>Lista de {% model_name_plural model %}</h1>
    </div>
    <div class="col-md-8">
      <form class="form-inline my-2 my-lg-0 pull-right">
        <label>Data Inicial</label>
        <input class="form-control ml-sm-2 mr-sm-2" name="start_date" type="date"/>
        <label>Data Final</label>
        <input class="form-control ml-sm-2 mr-sm-2" name="end_date" type="date"/>
        <button class="btn btn-primary my-2 my-sm-0" type="submit">OK</button>
      </form>
    </div>
  </div>

  <div class="row">
    <div class="col-md-12">
      <table class="table">
        <thead>
          <tr>
            <th>Item</th>
            <th>Título</th>
            <th>Título</th>
            <th>Sub-título</th>
            <th>Data de publicação</th>
            <th>Categoria</th>
            <th>Grupo</th>
          </tr>
        </thead>
        <tbody>
          {% for obj in object_list %}
            <tr>
              <td>{{ forloop.counter }}</td>
              <td>{{ obj.title|slugify }}</td>
              <td>{{ obj.title|truncatechars:13 }}</td>
              <td>{{ obj.subtitle|safe|default:"---" }}</td>
              <td>{{ obj.published_date|date:"d/m/Y" }}</td>
              {% if obj.category.title == 'Django' %}
                <td>{{ obj.category }}</td>
              {% else %}
                <td>{{ obj.category|default:"---" }}</td>
              {% endif %}
              <td>
                {% if obj.user|has_group:"Autor" %}
                  {{ obj.user|name_group }}
                {% endif %}
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
{% endblock content %}
```

Rodando o servidor e abrindo `http://localhost:8000/articles/`, a tabela mostra, para cada artigo: o número da linha, o título em forma de slug, o título cortado em 13 caracteres, o subtítulo (com HTML renderizado ou `---`), a data em `dd/mm/aaaa`, a categoria (ou `---`) e o grupo do autor.

## Conclusão

* Filtros personalizados (`@register.filter`) transformam um valor e podem receber um argumento: `valor|filtro:"argumento"`.
* Template tags simples (`@register.simple_tag`) recebem quantos argumentos você quiser e escrevem o resultado no template.
* Os dois ficam em `templatetags/` dentro do app e são carregados com `{% load nome_do_arquivo %}`.
