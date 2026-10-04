# Dica 23 - CRUD de produtos

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, django-widget-tweaks 1.4.12 e Tailwind CSS com o template Windster (Flowbite).
{: .versoes }

<a href="https://youtu.be/TfC_1EcRBss">
    <img src="../.gitbook/assets/youtube.png">
</a>

Na [Dica 20 - Templates](086-20-templates.md) criamos um padrão de templates, urls e views para os usuários (lista, detalhes, adicionar e editar). Agora vamos reaproveitar esse padrão para fazer um **CRUD** completo dos produtos do projeto **Dicas de Django**: listar, ver detalhes, adicionar, editar e deletar, desta vez **salvando** os dados.

No fim, também tiramos da lista de usuários os botões de adicionar, editar e deletar: não faz muito sentido o administrador cadastrar ou editar usuários por ali. O usuário se cadastra sozinho (dica 17) e, mais para frente, vai editar só os próprios dados, num perfil.

## Pré-requisitos

* O projeto das dicas anteriores, com a app `product` (models `Category`, `Product` e `Photo`, criados na [Dica 19.7](085-19-7-modelagem-resumo.md)) e os templates de usuário da [Dica 20](086-20-templates.md).
* `django-widget-tweaks` em `INSTALLED_APPS`.

O model `Product`, como ficou na dica 19.7:

```python
# product/models.py
class Product(models.Model):
    title = models.CharField('título', max_length=255, unique=True)
    description = models.TextField('descrição', null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='categoria',
        related_name='products',
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        return f'{self.title}'
```

## Os arquivos de template

A app `product` ainda não tem a pasta `templates`. Seguindo o padrão, criamos `templates/product` (com o nome da app, no singular) e os três templates:

```bash
mkdir -p backend/product/templates/product
touch backend/product/templates/product/product_list.html
touch backend/product/templates/product/product_detail.html
touch backend/product/templates/product/product_form.html
```

Em seguida copiamos o conteúdo dos templates de usuário para os de produto (`user_list.html` para `product_list.html`, `user_detail.html` para `product_detail.html`, `user_form.html` para `product_form.html`) e a pasta `includes`:

```bash
cp -r backend/accounts/templates/accounts/includes backend/product/templates/product/
```

`breadcrumb.html`, `search.html` e `navigation_buttons.html` ficam iguais aos da dica 20. O `delete_modal.html` vai ganhar um `id` no botão de deletar, como veremos adiante.

## As urls

Crie `product/urls.py`, copiando a estrutura de `accounts/urls.py`. Aqui definimos `app_name`, então as urls serão referenciadas com o namespace `product:`:

```python
# product/urls.py
from django.urls import include, path

from backend.product import views as v

app_name = 'product'

# A ordem das urls é importante por causa do slug, quando existir.
product_patterns = [
    path('', v.product_list, name='product_list'),  # noqa E501
    path('create/', v.product_create, name='product_create'),  # noqa E501
    path('<int:pk>/', v.product_detail, name='product_detail'),  # noqa E501
    path('<int:pk>/update/', v.product_update, name='product_update'),  # noqa E501
    path('<int:pk>/delete/', v.product_delete, name='product_delete'),  # noqa E501
]

urlpatterns = [
    path('', include(product_patterns)),
]
```

E inclua no `urls.py` principal, com o `namespace`:

```python
# urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('backend.core.urls', namespace='core')),  # noqa E501
    path('accounts/', include('backend.accounts.urls')),  # noqa E501
    path('bookstore/', include('backend.bookstore.urls', namespace='bookstore')),  # noqa E501
    path('crm/', include('backend.crm.urls', namespace='crm')),  # noqa E501
    path('expense/', include('backend.expense.urls', namespace='expense')),  # noqa E501
    path('product/', include('backend.product.urls', namespace='product')),  # noqa E501
    path('admin/', admin.site.urls),  # noqa E501
]
```

No menu lateral, ligue o item **Produtos**:

```html
<!-- core/templates/includes/aside.html -->
<a href="{% url 'product:product_list' %}" class="text-base text-gray-900 font-normal rounded-lg hover:bg-gray-100 flex items-center p-2 group ">
  ...
  <span class="ml-3 flex-1 whitespace-nowrap">Produtos</span>
</a>
```

No vídeo, o primeiro `runserver` reclamou porque o `include` da app ainda não estava no `urls.py` principal e o namespace `product` não existia. Com os dois ajustes acima, o menu passa a funcionar.

## O formulário

```python
# product/forms.py
from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Product
        fields = ('title', 'description', 'category')
```

Um `ModelForm` simples, com os campos um a um. O `required_css_class = 'required'` acrescenta a classe CSS `required` nas linhas dos campos obrigatórios quando o formulário é renderizado pelo próprio Django (útil para, por exemplo, colocar um asterisco via CSS).

## As views

```python
# product/views.py
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Product


def product_list(request):
    template_name = 'product/product_list.html'
    object_list = Product.objects.all()
    context = {'object_list': object_list}
    return render(request, template_name, context)


def product_detail(request, pk):
    template_name = 'product/product_detail.html'
    instance = get_object_or_404(Product, pk=pk)

    context = {'object': instance}
    return render(request, template_name, context)


def product_create(request):
    template_name = 'product/product_form.html'
    form = ProductForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('product:product_list')

    context = {'form': form}
    return render(request, template_name, context)


def product_update(request, pk):
    template_name = 'product/product_form.html'
    instance = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=instance)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('product:product_list')

    context = {'form': form, 'object': instance}
    return render(request, template_name, context)


def product_delete(request, pk):
    instance = get_object_or_404(Product, pk=pk)
    instance.delete()
    return redirect('product:product_list')
```

Cada uma, em ordem:

* **product_list**: todos os produtos em `object_list` (o padrão de nomes que adotamos).
* **product_detail**: busca o produto pelo `pk` da url com `get_object_or_404` e manda como `object`.
* **product_create**: a diferença em relação à dica 20 é o trecho que **salva**. Se a requisição é POST e o formulário é válido, `form.save()` grava o produto e `redirect` volta para a lista. Num GET (ou com erros), o template é renderizado com o formulário.
* **product_update**: igual ao create, mas com `instance=instance`, para o formulário vir preenchido e o `save()` atualizar o mesmo registro. O `'object': instance` no contexto faz o título mostrar **Editar**.
* **product_delete**: busca o produto, apaga e volta para a lista.

## O get_absolute_url

Para o título do produto na lista virar um link para os detalhes, crie o `get_absolute_url` no model, como fizemos no `User`, só que agora com o namespace:

```python
# product/models.py
from django.db import models
from django.urls import reverse_lazy

...


class Product(models.Model):
    ...

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse_lazy('product:product_detail', kwargs={'pk': self.pk})
```

## A lista de produtos

Em relação ao `user_list.html`: o título passa a ser **Produtos**, as urls usam o namespace `product:`, as colunas são **Título**, **Descrição** e **Categoria** (mais uma coluna vazia no começo, para a imagem), e a coluna de status sai.

```html
<!-- product_list.html -->
{% extends "base.html" %}

{% block content %}
  <!-- START: header -->
  <div class="p-4 bg-white block sm:flex items-center justify-between border-b border-gray-200 lg:mt-1.5">
    <div class="mb-1 w-full">
      <div class="mb-4">
        {% include "./includes/breadcrumb.html" %}
        <h1 class="text-xl sm:text-2xl font-semibold text-gray-900">Produtos</h1>
      </div>
      <div class="sm:flex">
        {% include "./includes/search.html" %}
        <!-- START: Adicionar -->
        <div class="flex items-center space-x-2 sm:space-x-3 ml-auto">
          <a href="{% url 'product:product_create' %}" data-modal-toggle="add-user-modal" class="w-1/2 text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center sm:w-auto">
            <svg class="-ml-1 mr-2 h-6 w-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd"></path></svg>
            Adicionar
          </a>
          <a href="" class="w-1/2 text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center sm:w-auto">
            <svg class="-ml-1 mr-2 h-6 w-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clip-rule="evenodd"></path></svg>
            Exportar
          </a>
        </div>
        <!-- END: Adicionar -->
      </div>
    </div>
  </div>
  <!-- END: header -->
  <!-- START: table -->
  <div class="flex flex-col">
    <div class="overflow-x-auto">
      <div class="align-middle inline-block min-w-full">
        <div class="shadow overflow-hidden">
          <table class="table-fixed min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-100">
              <tr>
                <th scope="col" class="p-4">
                  <div class="flex items-center">
                    <input id="checkbox-all" aria-describedby="checkbox-1" type="checkbox"
                      class="bg-gray-50 border-gray-300 focus:ring-3 focus:ring-cyan-200 h-4 w-4 rounded">
                    <label for="checkbox-all" class="sr-only">checkbox</label>
                  </div>
                </th>
                <th scope="col" class="p-4 text-left text-xs font-medium text-gray-500 uppercase">
                </th>
                <th scope="col" class="p-4 text-left text-xs font-medium text-gray-500 uppercase">
                  Título
                </th>
                <th scope="col" class="p-4 text-left text-xs font-medium text-gray-500 uppercase">
                  Descrição
                </th>
                <th scope="col" class="p-4 text-left text-xs font-medium text-gray-500 uppercase">
                  Categoria
                </th>
                <th scope="col" class="p-4">
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              {% for object in object_list %}
                <tr class="hover:bg-gray-100">
                  <td class="p-4 w-4">
                    <div class="flex items-center">
                      <input id="checkbox-1" aria-describedby="checkbox-1" type="checkbox"
                        class="bg-gray-50 border-gray-300 focus:ring-3 focus:ring-cyan-200 h-4 w-4 rounded">
                      <label for="checkbox-1" class="sr-only">checkbox</label>
                    </div>
                  </td>
                  <td class="p-4 flex items-center whitespace-nowrap space-x-6 mr-12 lg:mr-0">
                    <img class="h-10 w-10 rounded-full" src="https://via.placeholder.com/150" alt="">
                    <div class="text-sm font-normal text-gray-500">
                      <div class="text-base font-semibold text-gray-900">
                        <a href="{{ object.get_absolute_url }}" class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg">{{ object }}</a>
                      </div>
                      <div class="text-sm font-normal text-gray-500">{{ object }}</div>
                    </div>
                  </td>
                  <td class="p-4 whitespace-nowrap text-base font-medium text-gray-900">{{ object.title }}</td>
                  <td class="p-4 whitespace-nowrap text-base font-medium text-gray-900">{{ object.description|default:"---" }}</td>
                  <td class="p-4 whitespace-nowrap text-base font-medium text-gray-900">{{ object.category|default:"---" }}</td>
                  <td class="p-4 whitespace-nowrap space-x-2">
                    <a href="{% url 'product:product_update' object.pk %}" class="text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium rounded-lg text-sm inline-flex items-center px-3 py-2 text-center">
                      <svg class="mr-2 h-5 w-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z"></path><path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd"></path></svg>
                      Editar
                    </a>
                    <button type="button" data-url="{% url 'product:product_delete' object.pk %}" data-modal-toggle="delete-user-modal" onclick="openModal(event)" class="text-white bg-red-600 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm inline-flex items-center px-3 py-2 text-center">
                      <svg class="mr-2 h-5 w-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>
                      Deletar
                    </button>
                  </td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
  <!-- END: table -->
  <!-- START: footer of table -->
  <div class="bg-white sticky sm:flex items-center w-full sm:justify-between bottom-0 right-0 border-t border-gray-200 p-4">
    <div class="flex items-center mb-4 sm:mb-0">
      <a href="#" class="text-gray-500 hover:text-gray-900 cursor-pointer p-1 hover:bg-gray-100 rounded inline-flex justify-center">
        <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>
      </a>
      <a href="#" class="text-gray-500 hover:text-gray-900 cursor-pointer p-1 hover:bg-gray-100 rounded inline-flex justify-center mr-2">
        <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>
      </a>
      <span class="text-sm font-normal text-gray-500">Mostrando <span class="text-gray-900 font-semibold">1-20</span> de <span class="text-gray-900 font-semibold">2290</span></span>
    </div>
    {% include "./includes/navigation_buttons.html" %}
  </div>
  <!-- END: footer of table -->

  {% include "./includes/delete_modal.html" %}

{% endblock content %}

{% block js %}
  <script>
    const targetEl = document.getElementById('delete-user-modal')
    const modal = new Modal(targetEl)

    openModal = (event) => {
      const url = event.target.dataset.url
      document.getElementById('id_delete').setAttribute('href', url)

      modal.show()
    }
    closeModal = () => {
      modal.hide()
    }
  </script>
{% endblock js %}
```

## Os detalhes

```html
<!-- product_detail.html -->
{% extends "base.html" %}

{% block content %}
  <div class="bg-white shadow rounded-lg p-4 sm:p-6 xl:p-8 ">
    <div class="mb-4">
      {% include "./includes/breadcrumb.html" %}
      <h1 class="text-xl sm:text-2xl font-semibold text-gray-900">Detalhes: {{ object }}</h1>
    </div>
    <div class="mb-5">
      <a href="javascript: history.go(-1)" class="text-base font-medium text-cyan-600 hover:bg-gray-100 rounded-lg">Voltar</a>
    </div>

    <div class="block w-full overflow-x-auto">
      <img class="h-20 w-20 rounded-lg" src="https://via.placeholder.com/500" alt="">
    </div>

    <!-- Título -->
    <div class="block w-full overflow-x-auto">
      <div class="mt-2">
        <div class="text-sm font-normal text-gray-500">Título</div>
        <div class="text-base font-semibold text-gray-900">{{ object.title }}</div>
      </div>
    </div>

    <!-- Descrição -->
    <div class="block w-full overflow-x-auto">
      <div class="mt-2">
        <div class="text-sm font-normal text-gray-500">Descrição</div>
        <div class="text-base font-semibold text-gray-900">{{ object.description }}</div>
      </div>
    </div>

    <!-- Categoria -->
    <div class="block w-full overflow-x-auto">
      <div class="mt-2">
        <div class="text-sm font-normal text-gray-500">Categoria</div>
        <div class="text-base font-semibold text-gray-900">{{ object.category|default:"---" }}</div>
      </div>
    </div>

  </div>
{% endblock content %}
```

Do `user_detail.html` copiado saem os campos de perfil (`object.profile...`), que não existem no produto.

## O formulário de adicionar e editar

Igual ao `user_form.html` da dica 22 (já com os `non_field_errors`), trocando "Usuário" por "Produto" e o **Cancelar** para voltar à lista de produtos:

```html
<!-- product_form.html -->
{% extends "base.html" %}
{% load widget_tweaks %}

{% block content %}
  <div class="mx-auto md:h-screen flex flex-col px-6 pt-8 pt:mt-0">
    <!-- Card -->
    <div class="bg-white shadow rounded-lg md:mt-0 w-full sm:max-w-screen-sm xl:p-0">
      <div class="p-6 sm:p-8 lg:p-16 space-y-8">
        <h2 class="text-2xl lg:text-3xl font-bold text-gray-900">
          {% if object.pk %}
            Editar
          {% else %}
            Adicionar
          {% endif %}
          Produto
        </h2>

        {% if form.errors %}
          {% for error in form.non_field_errors %}
            <p class="text-red-500">{{ error }}</p>
          {% endfor %}
        {% endif %}

        <form class="mt-8 space-y-6" action="." method="POST" enctype="multipart/form-data">
          {% csrf_token %}
          {% for field in form.visible_fields %}
            <div>
              <label class="text-sm font-medium text-gray-900 block mb-2">{{ field.label }}</label>
              {% render_field field class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5" %}
            </div>
            <span class="text-sm font-medium text-gray-500">{{ field.help_text }}</span>
            {% for error in field.errors %}
              <span class="text-red-500">{{ error }}</span> <br>
            {% endfor %}
          {% endfor %}

          <div class="flex flex-col sm:flex-row">
            <button type="submit" class="text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium rounded-lg text-base px-5 py-3 w-full sm:w-auto text-center">Salvar</button>
            <a href="{% url 'product:product_list' %}" class="text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 font-medium rounded-lg text-sm px-5 py-3 mt-2 sm:mt-0 sm:ml-2 w-full sm:w-auto text-center">
              Cancelar
            </a>
          </div>
        </form>
      </div>
    </div>
  </div>
{% endblock content %}
```

## Deletando com o modal

O modal de exclusão é **um só** e fica fora do `{% for %}` da tabela. Então, ao clicar em **Deletar** numa linha, o modal precisa saber **qual** produto apagar. A solução tem três partes:

1. Cada botão **Deletar** guarda a url de exclusão do seu produto num atributo `data-url` e passa o evento do clique para `openModal(event)`:

```html
<button type="button" data-url="{% url 'product:product_delete' object.pk %}" data-modal-toggle="delete-user-modal" onclick="openModal(event)" class="...">
```

2. No `delete_modal.html` da app `product`, o link **Sim, deletar** ganha o `id="id_delete"`:

```html
<!-- product/templates/product/includes/delete_modal.html -->
<!-- Delete User Modal -->
<div class="hidden overflow-x-hidden overflow-y-auto fixed top-4 left-0 right-0 md:inset-0 z-50 justify-center items-center h-modal sm:h-full" id="delete-user-modal">
  <div class="relative w-full max-w-md px-4 h-full md:h-auto">
    <!-- Modal content -->
    <div class="bg-white rounded-lg shadow relative">
      <!-- Modal header -->
      <div class="flex justify-end p-2">
        <button type="button" onclick="closeModal()" class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center" data-modal-toggle="delete-user-modal">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
        </button>
      </div>
      <!-- Modal body -->
      <div class="p-6 pt-0 text-center">
        <svg class="w-20 h-20 text-red-600 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <h3 class="text-xl font-normal text-gray-500 mt-5 mb-6">Tem certeza que você quer deletar este registro?</h3>
        <a id="id_delete" href="#" class="text-white bg-red-600 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-base inline-flex items-center px-3 py-2.5 text-center mr-2">
          Sim, deletar
        </a>
        <a href="#" onclick="closeModal()" class="text-gray-900 bg-white hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 border border-gray-200 font-medium inline-flex items-center rounded-lg text-base px-3 py-2.5 text-center" data-modal-toggle="delete-user-modal">
          Não, cancelar
        </a>
      </div>
    </div>
  </div>
</div>
```

3. No bloco `js` do `product_list.html`, o `openModal` lê o `data-url` do botão clicado (`event.target.dataset.url`) e coloca essa url no `href` do link `id_delete` antes de abrir o modal:

```javascript
openModal = (event) => {
  const url = event.target.dataset.url
  document.getElementById('id_delete').setAttribute('href', url)

  modal.show()
}
```

Inspecionando o elemento no navegador, depois de clicar em **Deletar** no produto 6, o link **Sim, deletar** aponta para `/product/6/delete/`. Clicando nele, a view `product_delete` apaga o produto e volta para a lista.

Observação: aqui a exclusão é feita por um link (requisição GET), do jeito que está no vídeo. Em produção o mais seguro é deletar só via POST, com `{% csrf_token %}`.

## Testando

```bash
python manage.py runserver
```

* No admin, crie uma categoria (por exemplo, "Calçados").
* Em **Produtos**, clique em **Adicionar**, preencha "Tênis", uma descrição e a categoria, e clique em **Salvar**: o produto aparece na lista.
* Clique no título: abre a página de detalhes.
* Clique em **Editar**: o formulário vem preenchido e o título mostra **Editar Produto**; ao salvar, a lista mostra o valor novo. **Cancelar** volta para a lista.
* Clique em **Deletar** e confirme: o produto some da lista.

## Limpando a lista de usuários

Por fim, na lista de usuários comentamos o botão **Adicionar** e a coluna com **Editar** e **Deletar**:

```html
<!-- accounts/templates/accounts/user_list.html -->
          <!-- <a href="{% url 'user_create' %}" data-modal-toggle="add-user-modal" class="...">
            ...
            Adicionar
          </a> -->

...

                  <!-- <td class="p-4 whitespace-nowrap space-x-2">
                    <a href="{% url 'user_update' object.pk %}" class="...">
                      ...
                      Editar
                    </a>
                    <button type="button" data-modal-toggle="delete-user-modal" onclick="openModal()" class="...">
                      ...
                      Deletar
                    </button>
                  </td> -->
```

Observação: o serviço de imagens `via.placeholder.com`, usado nos templates, não funciona mais; troque por outra imagem se for rodar hoje.
