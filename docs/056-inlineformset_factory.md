# Dica 56 - Django inlineformset_factory + HTMX

**Versões usadas no vídeo:** Django 3.2.10, Python 3.8, Bootstrap 4.4.1, htmx 1.6.1, django-widget-tweaks 1.4.9 e jQuery 3.4.1.
{: .versoes }

<a href="https://youtu.be/66_FQxopiBY">
    <img src="../.gitbook/assets/youtube.png">
</a>

Este video está disponível nas playlist:

* Dicas de Django
* HTMX
* Tutorial Django
* Django - assuntos diversos

Github: [https://github.com/rg3915/django-inlineformset-tutorial](https://github.com/rg3915/django-inlineformset-tutorial)

Todo o passo a passo está em [https://github.com/rg3915/django-inlineformset-tutorial#passo-a-passo](https://github.com/rg3915/django-inlineformset-tutorial#passo-a-passo).

Documentação e referências:

* [https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/#inline-formsets](https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/#inline-formsets)
* [Formulários dinâmicos com inlineformset_factory em uma aplicação Django](https://felipefrizzo.github.io/post/form-inline/), do Felipe Frizzo
* [https://felipefrizzo.github.io/post/form-inline-cbv/](https://felipefrizzo.github.io/post/form-inline-cbv/)

Neste tutorial vamos aprender o `inlineformset_factory` do jeito certo. O objetivo é inserir vários produtos numa ordem de compra, na mesma tela: o formulário da ordem (a nota fiscal) e, abaixo dele, uma linha para cada item (produto, quantidade e preço), com um botão para adicionar novas linhas e um "x" para remover. É o que o `TabularInline` faz no Admin, só que agora no site. Para completar, vamos usar o htmx para:

* adicionar uma nova linha de item, buscando o HTML no Django;
* trazer o preço do produto quando ele for escolhido;
* deletar um item já salvo.

Depois veremos como editar a ordem de compra com os mesmos formulários.

## Pré-requisitos

O projeto do vídeo já vem pronto do repositório, no pacote `backend`, com as apps `core`, `accounts`, `product` e `ecommerce`, e usa:

```
# requirements.txt
dj-database-url==0.5.0
django-extensions==3.1.5
django-localflavor==3.1
django-seed==0.3.1
django-widget-tweaks==1.4.9
Django==3.2.*
Faker==10.0.0
isort==5.10.1
python-decouple==3.5
```

Para rodar o projeto:

```bash
git clone https://github.com/rg3915/django-inlineformset-tutorial.git
cd django-inlineformset-tutorial
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python contrib/env_gen.py
python manage.py migrate
python manage.py createsuperuser --username="admin" --email=""
```

O `widget_tweaks` precisa estar no `INSTALLED_APPS`:

```python
# backend/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd apps
    'django_extensions',
    'widget_tweaks',
    'django_seed',
    # my apps
    'backend.accounts.apps.AccountsConfig',
    'backend.core.apps.CoreConfig',
    'backend.ecommerce.apps.EcommerceConfig',
    'backend.product.apps.ProductConfig',
]
```

O `base.html` carrega o Bootstrap 4, o Font Awesome, o htmx e o jQuery, e tem os blocos `css`, `content` e `js`:

```html
<!-- backend/core/templates/base.html -->
{% load static %}
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
  <link rel="shortcut icon" href="https://www.djangoproject.com/favicon.ico">
  <title>Django</title>

  <!-- Bootstrap core CSS -->
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css">

  <!-- Font-awesome -->
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">

  <link rel="stylesheet" href="{% static 'css/style.css' %}">

  <!-- HTMX -->
  <script src="https://unpkg.com/htmx.org@1.6.1"></script>

  {% block css %}{% endblock css %}

</head>

<body>
  <div class="container">
    {% include "includes/nav.html" %}
    {% block content %}{% endblock content %}
  </div>

  <!-- jQuery -->
  <script src="{% static 'js/jquery-3.4.1.min.js' %}"></script>
  <!-- Bootstrap core JS -->
  <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js"></script>
  <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js"></script>

  {% block js %}{% endblock js %}
</body>

</html>
```

No `backend/core/static/css/style.css` estão as classes usadas nos botões de remover:

```css
/* backend/core/static/css/style.css */
body {
  margin-top: 70px;
}

label.required:after {
  content: ' *';
  color: red;
}

.span-is-link {
  cursor: pointer;
}

.no {
  color: red;
}
```

## Produtos: um exemplo de htmx

Antes de ir para o formset, um exemplo de htmx que já existe no projeto. A app `product` tem o modelo:

```python
# backend/product/models.py
from django.db import models


class Product(models.Model):
    title = models.CharField('título', max_length=20, unique=True)
    price = models.DecimalField('preço', max_digits=7, decimal_places=2)
    manufacturing_date = models.DateField('data de fabricação', null=True, blank=True)  # noqa E501
    due_date = models.DateField('data de vencimento', null=True, blank=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        return self.title
```

Na lista de produtos, o botão **Adicionar** abre um modal do Bootstrap (`data-toggle` e `data-target`) e, ao mesmo tempo, o htmx faz um GET no formulário (`hx-get`) e coloca o HTML dentro do modal (`hx-target="#addContent"`):

```html
<!-- backend/product/templates/product/product_list.html -->
{% extends "base.html" %}

{% block content %}
<div>
  <div class="row">
    <div class="col-auto">
      <h1>
        Lista de Produtos
        <a
          href=""
          class="btn btn-primary"
          data-toggle="modal"
          data-target="#addModal"
          hx-get="{% url 'product:product_create' %}"
          hx-target="#addContent"
          hx-swap="innerHTML"
        >Adicionar</a>
      </h1>
    </div>
  </div>
  <table class="table">
    <thead>
      <tr>
        <th>Título</th>
        <th>Preço</th>
      </tr>
    </thead>
    <tbody id="productTbody">
      {% for object in object_list %}
        <tr>
          <td>{{ object.title }}</td>
          <td>R$ <span class="float-right">{{ object.price }}</span></td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</div>

{% include "../includes/add_modal.html" %}

{% endblock content %}
```

```html
<!-- backend/product/templates/includes/add_modal.html -->
<!-- addModal -->
<div class="modal fade" id="addModal" tabindex="-1" role="dialog" aria-labelledby="addModalLabel">
  <div class="modal-dialog" role="document">
    <div id="addContent" class="modal-content">
      <div class="modal-header">
        <h4 class="modal-title" id="detailModalLabel">Adicionar</h4>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
      </div>
      <div class="modal-body">
        <!-- O novo conteúdo será inserido aqui -->
        ...
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">Fechar</button>
        <button type="submit" class="btn btn-primary">Salvar</button>
      </div>
    </div>
  </div>
</div>
```

O formulário do modal faz o POST com `hx-post` e coloca a linha nova no começo da tabela (`hx-target="#productTbody"` e `hx-swap="afterbegin"`):

```html
<!-- backend/product/templates/hx/product_form_hx.html -->
<div class="modal-header">
  <h4 class="modal-title" id="addModalLabel">Adicionar</h4>
  <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
</div>
<form
  hx-post="{% url 'product:product_create' %}"
  hx-target="#productTbody"
  hx-indicator=".htmx-indicator"
  hx-swap="afterbegin"
>
  <div class="modal-body">
    {% csrf_token %}
    {% for field in form %}
      <div class="form-group p-2">
        {{ field.label_tag }}
        {{ field }}
        {{ field.errors }}
        {% if field.help_text %}
          <small class="text-muted">{{ field.help_text|safe }}</small>
        {% endif %}
      </div>
    {% endfor %}
  </div>
  <div class="modal-footer">
    <button type="button" class="btn btn-default" data-dismiss="modal">Fechar</button>
    <button type="submit" class="btn btn-primary">Salvar</button>
  </div>
</form>

<script>
  $('form').on('submit', function() {
    $('#addModal').modal('toggle')
  });
</script>
```

```html
<!-- backend/product/templates/hx/product_result_hx.html -->
<tr>
  <td>{{ object.title }}</td>
  <td>R$ <span class="float-right">{{ object.price }}</span></td>
</tr>
```

A view é bem tradicional: renderiza o formulário no GET e, no POST, salva e devolve só a linha da tabela:

```python
# backend/product/views.py
from django.shortcuts import render
from django.views.generic import ListView

from .forms import ProductForm
from .models import Product


class ProductListView(ListView):
    model = Product


def product_create(request):
    template_name = 'hx/product_form_hx.html'
    form = ProductForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            product = form.save()
            template_name = 'hx/product_result_hx.html'
            context = {'object': product}
            return render(request, template_name, context)

    context = {'form': form}
    return render(request, template_name, context)
```

```python
# backend/product/forms.py
from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Product
        fields = ('title', 'price')

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
```

```python
# backend/product/urls.py
from django.urls import path

from backend.product import views as v

app_name = 'product'


urlpatterns = [
    path('', v.ProductListView.as_view(), name='product_list'),
    path('create/', v.product_create, name='product_create'),
]
```

## A ordem de compra e o TabularInline

Na app `ecommerce` temos `Order` (a ordem de compra, com o número da nota fiscal) e `OrderItems` (os itens da ordem: produto, quantidade e preço). O `TimeStampedModel` é um modelo abstrato da app `core` que acrescenta os campos `created` e `modified`.

```python
# backend/ecommerce/models.py
from django.db import models

from backend.core.models import TimeStampedModel
from backend.product.models import Product


class Order(TimeStampedModel):
    nf = models.CharField('nota fiscal', max_length=7, unique=True)

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'ordem de compra'
        verbose_name_plural = 'ordens de compra'

    def __str__(self):
        return self.nf


class OrderItems(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        verbose_name='ordem',
        related_name='order_items',
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        verbose_name='produto',
        related_name='product_items',
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField('quantidade')
    price = models.DecimalField('preço', max_digits=7, decimal_places=2)

    class Meta:
        ordering = ('pk',)

    def __str__(self):
        return f'{self.pk} - {self.order.pk} - {self.product}'
```

```python
# backend/core/models.py (trecho)
class TimeStampedModel(models.Model):
    created = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )
    modified = models.DateTimeField(
        'modificado em',
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        abstract = True
```

No Admin, o `TabularInline` mostra os itens dentro da tela da ordem de compra. É exatamente esse comportamento que vamos reproduzir no site.

```python
# backend/ecommerce/admin.py
from django.contrib import admin

from .models import Order, OrderItems


class OrderItemsInline(admin.TabularInline):
    model = OrderItems
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderItemsInline,)
    list_display = ('__str__', 'nf',)
    search_fields = ('nf',)


@admin.register(OrderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'quantity', 'price')
```

Rode o servidor, entre no Admin, crie uma ordem de compra (nota fiscal `001`), clique em "Adicionar outro(a) Order items" para inserir mais itens e salve. Os itens ficam salvos junto com a ordem.

## As rotas

No `urls.py` principal, a rota da app `ecommerce` estava comentada; descomente-a:

```python
# backend/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('backend.core.urls', namespace='core')),
    path('accounts/', include('backend.accounts.urls')),  # without namespace
    path('ecommerce/', include('backend.ecommerce.urls', namespace='ecommerce')),
    path('product/', include('backend.product.urls', namespace='product')),
    path('admin/', admin.site.urls),
]
```

E no `includes/nav.html` o link "Ordem de compra" passa a apontar para a lista:

```html
<!-- backend/core/templates/includes/nav.html (trecho) -->
<li class="nav-item">
  <a class="nav-link" href="{% url 'ecommerce:order_list' %}">Ordem de compra</a>
</li>
```

## Os formulários com inlineformset_factory

Esta é a parte mais delicada, e a mais importante. Edite o `forms.py` da app `ecommerce`:

```python
# backend/ecommerce/forms.py
from django import forms
from django.forms import inlineformset_factory

from .models import Order, OrderItems


class OrderForm(forms.ModelForm):
    required_css_class = 'required'

    nf = forms.IntegerField(label="Nota Fiscal")

    class Meta:
        model = Order
        fields = ('nf',)


class OrderItemsForm(forms.ModelForm):
    required_css_class = 'required'

    id = forms.IntegerField()

    class Meta:
        model = OrderItems
        fields = ('order', 'id', 'product', 'quantity', 'price')

    def __init__(self, *args, **kwargs):
        super(OrderItemsForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['order'].label = ''
        self.fields['order'].widget = forms.HiddenInput()

        self.fields['id'].label = ''
        self.fields['id'].widget = forms.HiddenInput()


OrderItemsFormset = inlineformset_factory(
    Order,
    OrderItems,
    form=OrderItemsForm,
    extra=0,
    can_delete=False,
    min_num=1,
    validate_min=True,
)
```

O que cada parte faz:

* `OrderForm` é o formulário principal, só com a nota fiscal.
* `OrderItemsForm` é o formulário de **uma** linha de item. Ele declara o `id` explicitamente, porque vamos precisar do `id` de cada item na hora de editar a ordem de compra (para o Django saber qual item atualizar e para o botão de deletar).
* No `__init__`, o laço coloca a classe `form-control` do Bootstrap em todos os campos. Depois, `order` e `id` ficam com o rótulo vazio e com o widget `HiddenInput`, para não aparecerem na tela.
* `inlineformset_factory(Order, OrderItems, ...)` cria a classe do formset: o primeiro argumento é o modelo principal e o segundo, o modelo dos itens. Passamos o nosso `form=OrderItemsForm`, `extra=0` (nenhuma linha extra vazia), `can_delete=False` (não queremos o checkbox de deletar; vamos deletar manualmente com htmx), `min_num=1` (pelo menos uma linha) e `validate_min=True` (valida esse mínimo).

## As views de criar e listar

```python
# backend/ecommerce/views.py
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView

from backend.product.models import Product

from .forms import OrderForm, OrderItemsForm, OrderItemsFormset
from .models import Order, OrderItems


class OrderListView(ListView):
    model = Order


def order_create(request):
    template_name = 'ecommerce/order_form.html'
    order_instance = Order()

    form = OrderForm(request.POST or None, instance=order_instance, prefix='main')
    formset = OrderItemsFormset(request.POST or None, instance=order_instance, prefix='items')

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('ecommerce:order_list')

    context = {'form': form, 'formset': formset}
    return render(request, template_name, context)
```

Repare em três detalhes:

* O formulário e o formset recebem a **mesma instância** (`order_instance`). Quando o `form.save()` grava a ordem, a instância ganha `pk`, e o `formset.save()` grava os itens ligados a ela.
* Cada um tem o seu **prefixo**: `main` para o formulário e `items` para o formset. Os campos ficam com nomes como `main-nf`, `items-0-product`, `items-1-quantity` etc. Esses nomes serão importantes no JavaScript.
* No POST, só salvamos se os dois forem válidos.

## As rotas da app ecommerce

```python
# backend/ecommerce/urls.py
from django.urls import path

from backend.ecommerce import views as v

app_name = 'ecommerce'

urlpatterns = [
    path('', v.OrderListView.as_view(), name='order_list'),
    path('create/', v.order_create, name='order_create'),
    path('add-row/', v.add_row_order_items_hx, name='add_row_order_items_hx'),
    path('product/price/', v.product_price, name='product_price'),
    path('<int:pk>/update/', v.order_update, name='order_update'),
    path('order-item/<int:pk>/delete/', v.order_item_delete, name='order_item_delete'),
]
```

No vídeo, as quatro últimas rotas começam comentadas e vão sendo liberadas conforme criamos as views abaixo.

## Os templates

Crie as pastas e os arquivos:

```bash
mkdir -p backend/ecommerce/templates/ecommerce/hx
touch backend/ecommerce/templates/ecommerce/order_{list,form}.html
touch backend/ecommerce/templates/ecommerce/hx/{product_price,row_order_items}_hx.html
tree
```

```
backend/ecommerce/templates/
└── ecommerce
    ├── hx
    │   ├── product_price_hx.html
    │   └── row_order_items_hx.html
    ├── order_form.html
    └── order_list.html
```

A lista de ordens de compra mostra cada ordem com os seus itens:

```html
<!-- backend/ecommerce/templates/ecommerce/order_list.html -->
{% extends "base.html" %}

{% block content %}
<div>
  <div class="row">
    <div class="col-auto">
      <h1>
        Ordens de Compra
        <a class="btn btn-primary" href="{% url 'ecommerce:order_create' %}">Adicionar</a>
      </h1>
    </div>
  </div>
  <table class="table">
    <thead>
      <tr>
        <th>Nota Fiscal</th>
        <th>Criado em</th>
        <th>Ações</th>
      </tr>
    </thead>
    <tbody id="bookTbody">
      {% for object in object_list %}
        <tr class="bg-light">
          <td>{{ object }}</td>
          <td>{{ object.created|date:"d/m/Y H:i:s" }}</td>
          <th>
            <a class="btn btn-success" href="{% url 'ecommerce:order_update' object.pk %}">
              <i class="fa fa-edit"></i> Editar
            </a>
          </th>
        </tr>
        <tr>
          <th>Produto</th>
          <th>Quantidade</th>
          <th>Preço</th>
        </tr>
        {% for items in object.order_items.all %}
          <tr>
            <td>{{ items.product.title }}</td>
            <td>{{ items.quantity }}</td>
            <td>R$ <span class="float-right">{{ items.price }}</span></td>
          </tr>
        {% endfor %}
      {% endfor %}
    </tbody>
  </table>
</div>

{% endblock content %}
```

## O formulário da ordem de compra

Agora o template principal. Ele usa o `widget_tweaks` (`{% render_field %}`) para acrescentar atributos aos campos direto no template:

```html
<!-- backend/ecommerce/templates/ecommerce/order_form.html -->
{% extends "base.html" %}
{% load static %}
{% load widget_tweaks %}
<!-- ... -->
          {{ formset.management_form }}
        <!-- ... -->
          <div id="order" class="form-inline">

            {% for order_item_form in formset %}
              <div id="item-{{ forloop.counter0 }}" class="form-group">
                {{ order_item_form.order }}
                {{ order_item_form.id }}

                {{ order_item_form.product.label }}
                {% render_field order_item_form.product class="form-control" hx-get="/ecommerce/product/price/" hx-target="#id_items-0-price" hx-swap="outerHTML" %}

                {{ order_item_form.quantity.label }}
                {{ order_item_form.quantity }}

                {{ order_item_form.price.label }}
                {{ order_item_form.price }}

                {% if order_item_form.id.value %}
                  <span
                    class="span-is-link no ml-2 remove-row"
                    hx-delete="{% url 'ecommerce:order_item_delete' order_item_form.id.value %}"
                    hx-confirm="Deseja mesmo deletar o item {{order_item_form.id.value}}?"
                    hx-target="#item-{{ forloop.counter0 }}"
                    hx-swap="outerHTML"
                  >
                    <i class="fa fa-times fa-lg"></i>
                  </span>
                {% else %}
                  <span class="span-is-link no ml-2" onclick="removeRow()">
                    <i class="fa fa-times fa-lg"></i>
                  </span>
                {% endif %}
              </div>
            {% endfor %}

          </div>
        <!-- ... -->
      <span
        id="addItem"
        class="btn btn-info mt-2"
        hx-get="{% url 'ecommerce:add_row_order_items_hx' %}"
        hx-target="#order"
        hx-swap="beforeend"
      >
        <i class="fa fa-plus"></i>
        Adicionar
      </span>
      <!-- ... -->

<script>
// Necessário por causa do delete
document.body.addEventListener('htmx:configRequest', (event) => {
  event.detail.headers['X-CSRFToken'] = '{{ csrf_token }}';
});
</script>
<!-- ... -->
```

Código completo: [backend/ecommerce/templates/ecommerce/order_form.html](https://github.com/rg3915/django-inlineformset-tutorial/blob/0387b97160d8505fe09e2ffc64251268a8149a12/backend/ecommerce/templates/ecommerce/order_form.html)

Vamos por partes:

* **O formulário principal** (`form.visible_fields`) mostra a nota fiscal com o rótulo, o campo com a classe `form-control` e os erros.
* **`{{ formset.management_form }}`** é obrigatório. Ele gera os campos ocultos que o Django usa para controlar o formset. Inspecionando o elemento no navegador, aparece:

  ```html
  <input type="hidden" name="items-TOTAL_FORMS" value="1" id="id_items-TOTAL_FORMS">
  <input type="hidden" name="items-INITIAL_FORMS" value="0" id="id_items-INITIAL_FORMS">
  <input type="hidden" name="items-MIN_NUM_FORMS" value="1" id="id_items-MIN_NUM_FORMS">
  <input type="hidden" name="items-MAX_NUM_FORMS" value="1000" id="id_items-MAX_NUM_FORMS">
  ```

  O `TOTAL_FORMS` diz quantas linhas estão sendo enviadas. Como vamos adicionar e remover linhas no navegador, o JavaScript terá que atualizar esse valor.
* **A `div` com `id="order"`** guarda as linhas. Cada linha é uma `div` com `id="item-0"`, `id="item-1"` etc. (`forloop.counter0` começa em zero), com os campos ocultos `order` e `id` e os campos produto, quantidade e preço.
* **No campo produto**, o `render_field` acrescenta os atributos do htmx: quando o produto muda, o htmx faz um GET em `/ecommerce/product/price/` e substitui (`outerHTML`) o campo de preço da linha (`#id_items-0-price`). Aqui o endereço foi escrito à mão, e não com `{% url %}`, porque o `render_field` do widget_tweaks não aceita outra tag do Django dentro dele.
* **O "x" de remover** tem duas versões. Se o item já existe no banco (`order_item_form.id.value`), ele faz um `hx-delete` na rota de deletar, com confirmação (`hx-confirm`), e substitui a linha pela resposta vazia. Se é uma linha nova, ainda não salva, basta tirá-la da tela com a função JavaScript `removeRow()`.
* **O botão Adicionar** faz um GET em `add_row_order_items_hx` e coloca o HTML recebido no fim da `div#order` (`hx-swap="beforeend"`).
* **Os botões**: Salvar, Fechar (escondido no começo, com `display: none`) e Cancelar.
* **No bloco `js`**, carregamos o `main.js` e configuramos o htmx para mandar o `X-CSRFToken` em todas as requisições. Sem isso, o `hx-delete` seria barrado pela proteção contra CSRF do Django.

## Adicionando uma nova linha com htmx

A view devolve um `OrderItemsForm` vazio, renderizado num template parcial:

```python
# backend/ecommerce/views.py
def add_row_order_items_hx(request):
    template_name = 'ecommerce/hx/row_order_items_hx.html'
    form = OrderItemsForm()
    context = {'order_item_form': form}
    return render(request, template_name, context)
```

```html
<!-- backend/ecommerce/templates/ecommerce/hx/row_order_items_hx.html -->
{% load widget_tweaks %}

<div id="item-{{ forloop.counter0 }}" class="form-group">

  <div class="form-group">
    {% render_field order_item_form.order data-field='order' %}

    <label>{{ order_item_form.product.label }}</label>
    {% render_field order_item_form.product class="form-control" hx-get="/ecommerce/product/price/" hx-target="#id_price" hx-swap="outerHTML" data-field='product' %}

    <label>{{ order_item_form.quantity.label }}</label>
    {% render_field order_item_form.quantity class="form-control" data-field='quantity' %}

    <label>{{ order_item_form.price.label }}</label>
    {% render_field order_item_form.price class="form-control" data-field='price' %}
  </div>

  <span class="span-is-link no ml-2" onclick="removeRow()">
    <i class="fa fa-times fa-lg"></i>
  </span>

</div>
```

Esta linha é parecida com a linha do `order_form.html`, com uma diferença importante: como o formulário não faz parte do formset, os campos saem **sem o prefixo e sem o número** (`name="product"`, `id="id_price"`, e a `div` sai com `id="item-"`). Por isso cada campo ganhou um `data-field`, que o JavaScript usa para encontrar o campo e renumerá-lo.

## O JavaScript que renumera as linhas

```javascript
// backend/core/static/js/main.js
document.querySelector('#addItem').addEventListener('click', function() {
  setTimeout(() => {
    reorderItems()
  }, 500)
})

function reorderItems() {
  Array.from(document.querySelectorAll("[id^='item-']"))
    .forEach((item, i) => {
      item.setAttribute('id', 'item-' + i)

      if (!item.querySelector('[data-field="order"]')) {
        return
      }

      item.querySelector('[data-field="order"]').setAttribute('name', 'items-' + i + '-order')
      item.querySelector('[data-field="order"]').setAttribute('id', 'id_items-' + i + '-order')

      item.querySelector('[data-field="product"]').setAttribute('name', 'items-' + i + '-product')
      item.querySelector('[data-field="product"]').setAttribute('hx-target', '#id_items-'+ i +'-price')

      item.querySelector('[data-field="quantity"]').setAttribute('name', 'items-' + i + '-quantity')

      item.querySelector('[data-field="price"]').setAttribute('name', 'items-' + i + '-price')
      item.querySelector('[data-field="price"]').setAttribute('id', 'id_items-' + i + '-price')
  })

  Array.from(document.querySelectorAll("#id_id"))
    .forEach((item, i) => item.setAttribute('name', 'items-' + (i + 1) + '-id'))

  let totalItems = $('#order').children().length
  document.querySelector('#id_items-TOTAL_FORMS').value = totalItems

  // htmx.org/api/#process
  htmx.process(document.querySelector("#order"))
}

function removeRow() {
  const span = event.target.parentNode
  const div = span.parentNode
  div.parentNode.removeChild(div)

  reorderItems()
}

Array.from(document.querySelectorAll('.remove-row'))
  .forEach((item, i) => {
    item.addEventListener('click', function() {
      document.querySelector('button[type="submit"]').style.display = 'none'
      document.querySelector('#btn-close').style.display = 'block'
    })
  })
```

Como funciona:

* Ao clicar em **Adicionar**, o htmx busca a linha nova; meio segundo depois (`setTimeout`), `reorderItems()` percorre todas as `div` cujo `id` começa com `item-` e renumera tudo: o `id` da `div` (`item-0`, `item-1`...), o `name` de cada campo (`items-0-product`, `items-1-quantity`...), o `id` do preço (`id_items-0-price`) e o `hx-target` do produto, que precisa apontar para o preço **da mesma linha**.
* Atualiza o `items-TOTAL_FORMS` com o número de linhas, senão o Django ignoraria as linhas novas.
* Chama `htmx.process()` na `div#order`, para o htmx reconhecer os atributos `hx-*` que acabaram de ser alterados (veja [htmx.org/api/#process](https://htmx.org/api/#process)).
* `removeRow()` tira a linha da tela e renumera de novo.
* Por fim, ao clicar no "x" de um item já salvo (`.remove-row`), o botão Salvar some e aparece o Fechar, porque o item já foi deletado no banco.

Com isso, ao clicar em Adicionar, a linha vem do Django e é renumerada. Inspecionando o elemento, a segunda linha fica com `items-1-order`, `items-1-product`, `items-1-quantity` e `items-1-price`, a terceira com `items-2-...`, e assim por diante.

## Salvando

O `if request.method == 'POST'` da view `order_create` já faz o trabalho: valida o formulário e o formset, salva os dois e redireciona para a lista.

```python
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('ecommerce:order_list')
```

Crie uma ordem com a nota fiscal `002`, adicione quatro linhas com produtos e quantidades diferentes e salve. A lista mostra a ordem com os quatro itens.

## Retornando o preço do produto com htmx

Agora, quando escolhermos o produto, queremos que o preço dele apareça no campo preço, para não precisar digitar (ainda dá para alterar à mão).

Quando o produto muda, o htmx faz o GET mandando o próprio campo na query string, por exemplo `/ecommerce/product/price/?items-0-product=6`. A view tira dali o número da linha e o `pk` do produto:

```python
# backend/ecommerce/views.py
def product_price(request):
    template_name = 'ecommerce/hx/product_price_hx.html'
    url = request.get_full_path()
    print('url', url)
    print(url.split('-'))
    item = url.split('-')[1]
    print('item', item)
    print('list', list(request.GET.values()))
    product_pk = list(request.GET.values())[0]
    product = Product.objects.get(pk=product_pk)

    context = {'product': product, 'item': item[0]}
    return render(request, template_name, context)
```

Os `print` ajudam a entender. Para `?items-0-product=2`, a saída é:

```
url /ecommerce/product/price/?items-0-product=2
['/ecommerce/product/price/?items', '0', 'product=2']
item 0
list ['2']
```

* `url.split('-')[1]` é o número da linha (`'0'`).
* `list(request.GET.values())[0]` é o `pk` do produto (`'2'`). Os valores vêm numa lista, por isso pegamos o primeiro.

O template devolve um `input` novo para o preço, com o `id` e o `name` da linha certa e o preço do produto no `value`:

```html
<!-- backend/ecommerce/templates/ecommerce/hx/product_price_hx.html -->
<input
  id="id_items-{{item}}-price"
  name="items-{{item}}-price"
  class="form-control"
  type="number"
  data-field="price"
  value="{{ product.price|safe }}"
/>
```

O filtro `|safe` é importante: com a localização em português, o preço seria escrito com vírgula (`3,00`), que um `input type="number"` não aceita. Com `|safe` ele sai como `3.00`.

Como o `hx-swap` do produto é `outerHTML`, este `input` substitui o campo de preço inteiro. Escolha um produto, e o preço aparece.

## Editando a ordem de compra

A view de edição é igual à de criação; a única diferença é que a instância vem do banco:

```python
# backend/ecommerce/views.py
def order_update(request, pk):
    template_name = 'ecommerce/order_form.html'
    order_instance = Order.objects.get(pk=pk)

    form = OrderForm(request.POST or None, instance=order_instance, prefix='main')
    formset = OrderItemsFormset(request.POST or None, instance=order_instance, prefix='items')

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('ecommerce:order_list')

    context = {'form': form, 'formset': formset}
    return render(request, template_name, context)
```

Com a instância, o formset já vem preenchido com os itens da ordem, e cada linha traz o seu `id` oculto. É por causa desse `id` que o Django sabe que deve atualizar os itens existentes, em vez de criar novos. Na lista, o botão **Editar** aponta para `{% url 'ecommerce:order_update' object.pk %}`. Altere as quantidades e os preços, salve, e a lista mostra os valores novos.

## Deletando itens

Por último, a view que deleta um item. Ela devolve uma resposta vazia, e como o `hx-target` do "x" é a própria linha com `hx-swap="outerHTML"`, a linha some da tela:

```python
# backend/ecommerce/views.py
def order_item_delete(request, pk):
    order_item = OrderItems.objects.get(pk=pk)
    order_item.delete()
    return HttpResponse('')
```

Ao clicar no "x" de um item salvo, o navegador pergunta "Deseja mesmo deletar o item 7?"; confirmando, o item é apagado do banco, a linha desaparece e o botão Salvar dá lugar ao Fechar, porque a exclusão já está gravada.

## Conclusão

O jeito certo de trabalhar com `inlineformset_factory` é: um `ModelForm` para cada modelo, o formset criado com `inlineformset_factory(Pai, Filho, form=...)`, o formulário e o formset compartilhando a mesma instância e cada um com o seu prefixo, e o `management_form` no template. O htmx entra para buscar no Django as linhas novas, o preço do produto e para deletar os itens, e um pouco de JavaScript mantém a numeração dos campos e o `TOTAL_FORMS` corretos.
