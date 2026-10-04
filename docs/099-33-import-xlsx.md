# Dica 33 - Importando XLSX com OpenPyXL

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, openpyxl 3.0.10 e Jupyter Notebook.
{: .versoes }

<a href="https://youtu.be/_5pjqup_F64">
    <img src="../.gitbook/assets/youtube.png">
</a>

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

Documentação do OpenPyXL: [https://openpyxl.readthedocs.io/en/stable/](https://openpyxl.readthedocs.io/en/stable/)

Até aqui importamos produtos de arquivos CSV. Agora vamos importar de uma planilha do Excel (`.xlsx`) com o **OpenPyXL**, de duas formas:

1. pelo Jupyter Notebook, lendo um arquivo do disco;
2. pelo front da aplicação, generalizando o modal de importação da [dica 30](096-30-import-csv-inmemoryuploadedfile.md) para aceitar tanto CSV quanto XLSX enviados por upload (`InMemoryUploadedFile`).

**Importante:** numa versão antiga desta página as tags de template tinham uma `\` no meio (`{\%`), por causa do GitBook. Aqui as tags já estão escritas do jeito certo; se você encontrar `{\%` em algum lugar, troque por `{%`.

![](../.gitbook/assets/tags.png)

## Pré-requisitos

* O projeto das dicas anteriores, com o model `Product` (`title` e `price`), o `product/services.py` com as funções `csv_to_list_in_memory` e `save_data`, e o modal de importação da [dica 30](096-30-import-csv-inmemoryuploadedfile.md).
* O Jupyter Notebook com o shell do Django (`python manage.py shell_plus --notebook`), como na [dica 31](097-31-import-csv-pandas.md).
* Uma planilha `products.xlsx` com duas colunas, `title` e `price`, sendo a primeira linha o cabeçalho. No vídeo ela tem 5 produtos:

| title      | price |
|------------|-------|
| notebook   | 6500  |
| pc game    | 9000  |
| book       | 120   |
| television | 4500  |
| iphone     | 7000  |

## Instalação

```bash
pip install openpyxl
```

No projeto ele já estava instalado (`Requirement already satisfied: openpyxl in ./.venv/lib/python3.10/site-packages (3.0.10)`) e no `requirements.txt` aparece como `openpyxl==3.0.*`.

## Lendo o XLSX no notebook

No Jupyter, crie um notebook novo com o kernel **Django Shell-Plus** e digite (cada bloco é uma célula):

```python
import openpyxl
```

```python
wb = openpyxl.load_workbook("/home/regis/Documentos/products.xlsx", data_only=True)
```

Troque o caminho pelo caminho do seu arquivo. O `data_only=True` é uma dica importante: com ele o OpenPyXL lê os **valores** das células, e não as fórmulas (uma célula com `=A1*2` vem com o resultado calculado, e não com o texto da fórmula), e a leitura fica mais rápida.

```python
ws = wb.active
```

`wb` é a pasta de trabalho (*workbook*) e `ws` é a planilha (*worksheet*) ativa, ou seja, a primeira aba.

```python
max_row = ws.max_row
max_col = ws.max_column
```

`max_row` e `max_column` dizem quantas linhas e colunas têm dados. Com eles percorremos a planilha linha a linha com `iter_rows`; cada `row` é uma tupla de células, e o conteúdo de cada célula está em `.value`:

```python
for row in ws.iter_rows(max_row=max_row, max_col=max_col):
    print(row[0].value, row[1].value)
```

```
title price
notebook 6500
pc game 9000
book 120
television 4500
iphone 7000
```

## Salvando no banco

Apague os produtos que já existem, para não atrapalhar:

```python
Product.objects.all().delete()
```

```
(100, {'product.Product': 100})
```

A função `save_data` é a mesma das dicas anteriores:

```python
def save_data(data):
    '''
    Salva os dados no banco.
    '''
    aux = []
    for item in data:
        title = item.get('title')
        price = item.get('price')
        obj = Product(
            title=title,
            price=price,
        )
        aux.append(obj)

    Product.objects.bulk_create(aux)
```

Agora montamos a lista de dicionários. Repare no `min_row=2`: a primeira linha da planilha é o cabeçalho (`title` e `price`), que não queremos gravar como produto, então começamos a partir da segunda linha:

```python
data = []

for row in ws.iter_rows(min_row=2, max_row=max_row, max_col=max_col):
    _dict = dict(title=row[0].value, price=row[1].value)
    data.append(_dict)
```

```python
save_data(data)
```

```python
Product.objects.all().count()
```

```
5
```

```python
Product.objects.all()
```

```
<QuerySet [<Product: book>, <Product: iphone>, <Product: notebook>, <Product: pc game>, <Product: television>]>
```

Os cinco produtos foram cadastrados (a lista vem em ordem alfabética por causa do `ordering = ('title',)` do model).

## Importando XLSX InMemoryUploadedFile

Agora vamos fazer o mesmo pelo front, aproveitando o modal de importação. Em vez de ter uma view só para CSV, vamos **generalizar**: uma única view `import_view` que olha a extensão do arquivo enviado e decide como lê-lo.

### O modal

Em `product/includes/import_modal.html`, mude a `action` do formulário para a nova rota `import_view` e o `name` do campo de arquivo para `filename`. Continua sendo essencial o `enctype="multipart/form-data"`, senão o arquivo não é enviado.

```html
<!-- backend/product/templates/product/includes/import_modal.html -->
<div class="hidden overflow-x-hidden overflow-y-auto fixed top-4 left-0 right-0 md:inset-0 z-50 justify-center items-center h-modal sm:h-full" id="import-modal">
  <div class="relative w-full max-w-md px-4 h-full md:h-auto">
    <!-- Modal content -->
    <div class="bg-white rounded-lg shadow relative">
      <!-- Modal header -->
      <div class="flex justify-end p-2">
        <button type="button" onclick="closeImportModal()" class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center" data-modal-toggle="import-modal">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
        </button>
      </div>
      <!-- Modal body -->
      <div class="p-6 pt-0 text-center">
        <form action="{% url 'product:import_view' %}" method="POST" enctype="multipart/form-data">
          {% csrf_token %}

          <h3 class="text-xl font-normal text-gray-500 mt-5 mb-6">Importar dados de um CSV ou XLSX</h3>

          <input type="file" name="filename">

          <button type="submit" class="text-white bg-cyan-600 hover:bg-cyan-800 focus:ring-4 focus:ring-cyan-300 font-medium rounded-lg text-base inline-flex items-center px-3 py-2.5 text-center mr-2">
            Sim, importar
          </button>
          <a href="#" onclick="closeImportModal()" class="text-gray-900 bg-white hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 border border-gray-200 font-medium inline-flex items-center rounded-lg text-base px-3 py-2.5 text-center" data-modal-toggle="import-modal">
            Não, cancelar
          </a>
        </form>
      </div>
    </div>
  </div>
</div>
```

As duas linhas que mudaram:

```html
<form action="{% url 'product:import_view' %}" method="POST" enctype="multipart/form-data">

<input type="file" name="filename">
```

### A rota

Em `product/urls.py`, troque a rota `import-csv/` por `import/`:

```python
# backend/product/urls.py
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
]

urlpatterns = [
    path('', include(product_patterns)),
]
```

### A view

Em `product/views.py`, importe o `openpyxl` no topo e troque a view `import_csv` pela `import_view`:

```python
# backend/product/views.py
import openpyxl
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import ProductForm
from .models import Product
from .services import csv_to_list_in_memory, save_data

...


@require_http_methods(['POST'])
def import_view(request):
    filename = request.FILES.get('filename')

    if filename.name.endswith('.csv'):
        data = csv_to_list_in_memory(filename)
    else:
        wb = openpyxl.load_workbook(filename, data_only=True)
        ws = wb.active

        max_row = ws.max_row
        max_col = ws.max_column

        data = []

        for row in ws.iter_rows(min_row=2, max_row=max_row, max_col=max_col):
            _dict = dict(title=row[0].value, price=row[1].value)
            data.append(_dict)

    save_data(data)
    return redirect('product:product_list')
```

Como funciona:

* O arquivo vem de `request.FILES.get('filename')`, o novo nome do campo.
* `filename.name` é o nome original do arquivo enviado. Se terminar com `.csv`, usamos o `csv_to_list_in_memory` da dica 30.
* Caso contrário, tratamos como XLSX. O `openpyxl.load_workbook` aceita, além de um caminho, um objeto do tipo arquivo, então passamos o próprio `InMemoryUploadedFile`, sem salvar nada no disco. O resto é o mesmo código do notebook, com `min_row=2` para pular o cabeçalho.
* Nos dois casos `data` termina como uma lista de dicionários com `title` e `price`, e o `save_data` grava tudo.

Como foi dito no vídeo, essa view ainda não está bem tratada: falta validação (por exemplo, um arquivo que não é nem CSV nem XLSX, um envio sem arquivo, ou títulos repetidos, que quebram o `unique=True` do campo `title`). Isso fica como lição de casa.

### Testando

Apague os produtos, clique em **Importar** na lista de produtos, escolha o `products.xlsx` e clique em **Sim, importar**: aparecem os cinco produtos (book R$ 120,00, iphone R$ 7.000,00, notebook R$ 6.500,00, pc game R$ 9.000,00 e television R$ 4.500,00). Importando em seguida o `products.csv`, os produtos do CSV também entram na lista.

## Conclusão

Vimos como ler um XLSX com o OpenPyXL (`load_workbook` com `data_only=True`, `wb.active` e `iter_rows` com `min_row=2`), primeiro no notebook e depois pelo front, com uma única view que importa CSV ou XLSX conforme a extensão do arquivo enviado.
