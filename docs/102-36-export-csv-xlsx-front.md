# Dica 36 - Exportando CSV e XLSX pelo front no projeto

**Versões usadas no vídeo:** Django 4.1, Python 3.10, django-import-export 3.x, PyExcelerate e Tailwind CSS com o template Windster (Flowbite).
{: .versoes }

<a href="https://youtu.be/-5ygHedHzow">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`). Aqui elas já estão escritas do jeito certo, sem a barra.

![](../.gitbook/assets/tags.png)

Nas dicas anteriores vimos como exportar dados pela linha de comando: CSV com o módulo `csv` do Python ([dica 34](100-34-export-csv.md)) e XLSX com o PyExcelerate ([dica 35](101-35-export-xlsx.md)). Agora vamos levar isso para o front do **Projeto Dicas de Django**: um botão **Exportar** na lista de produtos abre um modal onde o usuário escolhe **CSV** ou **XLSX**, e cada opção chama uma view que gera o arquivo.

No fim da dica veremos também como exportar **apenas os itens selecionados** pelo Admin, usando o `django-import-export`.

## Pré-requisitos

* O projeto das dicas anteriores (repositório [rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)), com a app `product`, a lista de produtos (`product_list.html`) e o modal de importação da [dica 30](096-30-import-csv-inmemoryuploadedfile.md).
* O model `Product` com os campos `title` e `price`.
* O PyExcelerate instalado ([dica 35](101-35-export-xlsx.md)):

```bash
pip install pyexcelerate
pip freeze | grep pyexcelerate >> requirements.txt
```

* O `django-import-export` instalado e configurado no Admin ([dica 30](096-30-import-csv-inmemoryuploadedfile.md)), com `'import_export'` em `INSTALLED_APPS`.

## O botão Exportar

Na lista de produtos já existia um link **Exportar** que não fazia nada (`<a href="">`). Troque esse link por um botão que chama a função `openExportModal()`.

Edite `product/templates/product/product_list.html`, no bloco dos botões do cabeçalho (`<!-- START: Adicionar -->`):

```html
<!-- product/templates/product/product_list.html -->
<!-- START: Adicionar -->
<div class="flex items-center space-x-2 sm:space-x-3 ml-auto">
  <a href="{% url 'product:product_create' %}" data-modal-toggle="add-user-modal" class="w-1/2 text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center sm:w-auto">
    <svg class="-ml-1 mr-2 h-6 w-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd"></path></svg>
    Adicionar
  </a>
  <button onclick="openImportModal()" class="w-1/2 text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center sm:w-auto">
    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
      <path fill-rule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
    </svg>
    Importar
  </button>
  <button onclick="openExportModal()" class="w-1/2 text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center sm:w-auto">
    <svg class="-ml-1 mr-2 h-6 w-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clip-rule="evenodd"></path></svg>
    Exportar
  </button>
</div>
<!-- END: Adicionar -->
```

No fim do bloco `content`, junto dos outros modais, inclua o novo modal de exportação:

```html
  {% include "./includes/delete_modal.html" %}
  {% include "./includes/import_modal.html" %}
  {% include "./includes/export_modal.html" %}

{% endblock content %}
```

E no bloco `js`, depois do código que já abre e fecha o modal de importação, acrescente as funções do modal de exportação. Elas usam a classe `Modal` do Flowbite, do mesmo jeito que os modais de exclusão e de importação:

```html
{% block js %}
  <script>
    // ... código dos modais de exclusão e de importação

    const targetElExport = document.getElementById('export-modal')
    const exportModal = new Modal(targetElExport)

    openExportModal = () => {
      exportModal.show()
    }
    closeExportModal = () => {
      exportModal.hide()
    }
  </script>
{% endblock js %}
```

* `document.getElementById('export-modal')` pega o `div` do modal pelo `id` (definido no include abaixo);
* `new Modal(...)` cria o objeto do Flowbite que sabe mostrar (`show()`) e esconder (`hide()`) o modal;
* `openExportModal` é chamada pelo botão **Exportar**, e `closeExportModal` pelo **X** e pelo link **Não, cancelar** do modal.

## O modal de exportação

Crie `product/templates/product/includes/export_modal.html`. É uma cópia do modal de importação, trocando o formulário de upload por dois links, um para cada formato:

```html
<!-- includes/export_modal.html -->
<!-- export_modal.html -->
<div class="hidden overflow-x-hidden overflow-y-auto fixed top-4 left-0 right-0 md:inset-0 z-50 justify-center items-center h-modal sm:h-full" id="export-modal">
  <div class="relative w-full max-w-md px-4 h-full md:h-auto">
    <!-- Modal content -->
    <div class="bg-white rounded-lg shadow relative">
      <!-- Modal header -->
      <div class="flex justify-end p-2">
        <button type="button" onclick="closeExportModal()" class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center" data-modal-toggle="import-modal">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
        </button>
      </div>
      <!-- Modal body -->
      <div class="p-6 pt-0 text-center">
        <h3 class="text-xl font-normal text-gray-500 mt-5">Exportar dados</h3>
        <p class="text-base font-normal text-gray-500 mb-6">Escolha uma opção:</p>

        <a href="{% url 'product:export_csv' %}" class="text-white bg-cyan-600 hover:bg-cyan-800 focus:ring-4 focus:ring-cyan-300 font-medium rounded-lg text-base inline-flex items-center px-3 py-2.5 text-center mr-2">
          CSV
        </a>

        <a href="{% url 'product:export_xlsx' %}" class="text-white bg-cyan-600 hover:bg-cyan-800 focus:ring-4 focus:ring-cyan-300 font-medium rounded-lg text-base inline-flex items-center px-3 py-2.5 text-center mr-2">
          XLSX
        </a>

        <a href="#" onclick="closeExportModal()" class="text-gray-900 bg-white hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 border border-gray-200 font-medium inline-flex items-center rounded-lg text-base px-3 py-2.5 text-center" data-modal-toggle="import-modal">
          Não, cancelar
        </a>

      </div>
    </div>
  </div>
</div>
```

Os pontos importantes:

* o `id="export-modal"` é o que o JavaScript usa para encontrar o modal;
* o botão **X** e o link **Não, cancelar** chamam `closeExportModal()`;
* os links **CSV** e **XLSX** apontam para as urls `product:export_csv` e `product:export_xlsx`, que vamos criar agora.

## As urls

Edite `product/urls.py` e acrescente as duas rotas no fim de `product_patterns`:

```python
# product/urls.py
from django.urls import include, path

from backend.product import views as v

app_name = 'product'

# A ordem das urls é importante por causa do slug, quando existir.
product_patterns = [
    # path('', v.ProductListView.as_view(), name='product_list'),  # noqa E501
    path('', v.product_list, name='product_list'),  # noqa E501
    path('create/', v.product_create, name='product_create'),  # noqa E501
    path('<int:pk>/', v.product_detail, name='product_detail'),  # noqa E501
    path('<int:pk>/update/', v.product_update, name='product_update'),  # noqa E501
    path('<int:pk>/delete/', v.product_delete, name='product_delete'),  # noqa E501
    path('import/', v.import_view, name='import_view'),  # noqa E501
    path('export/csv/', v.export_csv, name='export_csv'),  # noqa E501
    path('export/xlsx/', v.export_xlsx, name='export_xlsx'),  # noqa E501
]

urlpatterns = [
    path('', include(product_patterns)),
]
```

## As views

Edite `product/views.py`. No topo, importe o módulo `csv` e o `Workbook` do PyExcelerate:

```python
# product/views.py
import csv
# from django.views.generic import ListView
import openpyxl
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from pyexcelerate import Workbook

from .forms import ProductForm
from .models import Product
from .services import csv_to_list_in_memory, save_data
```

E no fim do arquivo escreva as duas views. O código é o mesmo que usamos no shell nas dicas 34 e 35, agora dentro de uma função que recebe o `request` e, no fim, redireciona de volta para a lista de produtos:

```python
# product/views.py
def export_csv(request):
    with open('/tmp/products_out.csv', 'w') as f:
        csv_writer = csv.writer(f)
        products = Product.objects.all()

        csv_writer.writerow(['title', 'price'])
        for product in products:
            csv_writer.writerow([product.title, product.price])

    return redirect('product:product_list')


def export_xlsx(request):
    products = Product.objects.all()
    data = [(product.title, product.price) for product in products]
    data.insert(0, ('title', 'price'))

    wb = Workbook()
    wb.new_sheet("sheet name", data=data)
    wb.save("/tmp/products_out.xlsx")
    return redirect('product:product_list')
```

* `export_csv` abre `/tmp/products_out.csv` para escrita, grava o cabeçalho (`title`, `price`) e depois uma linha por produto;
* `export_xlsx` monta uma lista de tuplas `(title, price)`, insere o cabeçalho na posição 0, cria a planilha com `wb.new_sheet(...)` e salva em `/tmp/products_out.xlsx`.

## Testando

Rode o servidor, entre em **Produtos** e clique em **Exportar**. O modal **Exportar dados** aparece com as opções **CSV**, **XLSX** e **Não, cancelar**.

Ao clicar em **CSV** ou **XLSX** a página simplesmente volta para a lista: a view não avisa onde salvou o arquivo. Ele está na pasta temporária, em `/tmp/products_out.csv` e `/tmp/products_out.xlsx`. No vídeo, a pasta `/tmp` é aberta no gerenciador de arquivos para conferir que os dois arquivos foram criados.

Repare que o arquivo é salvo **no servidor**, e não baixado pelo navegador. Para o usuário receber o arquivo, a view teria que devolver um `HttpResponse` com o conteúdo, mas isso não faz parte deste vídeo.

## Exportar apenas itens selecionados no Admin

Na [dica 30](096-30-import-csv-inmemoryuploadedfile.md) configuramos o `ImportExportModelAdmin`, que coloca os botões **Importar** e **Exportar** no Admin. Mas esse **Exportar** exporta todos os registros. Para exportar só alguns, use também o `ExportActionModelAdmin`, que acrescenta uma **ação** na lista do Admin.

Edite `product/admin.py`:

```python
# product/admin.py
from django.contrib import admin
from import_export import resources
from import_export.admin import ExportActionModelAdmin, ImportExportModelAdmin

from .models import Category, Photo, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    search_fields = ('title',)


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0


class ProductResource(resources.ModelResource):

    class Meta:
        model = Product


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_classes = [ProductResource]
    inlines = (PhotoInline,)
    list_display = ('__str__', 'slug', 'category')
    readonly_fields = ('slug',)
    search_fields = ('title',)
    list_filter = ('category',)
    # date_hierarchy = 'created'
```

A única mudança é o `ExportActionModelAdmin`, no import e na herança de `ProductAdmin`.

Agora, em `/admin/product/product/`, marque alguns produtos, escolha a ação **Exportar produtos selecionados**, escolha o formato (CSV, XLSX etc.) e clique em **Ir**. O arquivo gerado (no vídeo, `Product-2023-03-15.csv`, aberto no LibreOffice Calc) traz só os produtos marcados, com todas as colunas do model: `id`, `created`, `modified`, `title`, `description`, `price`, `category` e `slug`.

## Conclusão

Com um modal, duas urls e duas views, o usuário passa a exportar os produtos em CSV ou XLSX pela interface do projeto, reaproveitando o código das dicas 34 e 35. E, no Admin, o `ExportActionModelAdmin` permite exportar apenas os registros selecionados. Esta é a última aula da série do Projeto Dicas de Django; o código completo está no repositório [rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django).
