# Dica 30 - Importando CSV InMemoryUploadedFile

VIDEO EM BREVE.

**Importante:** remova a `\` no meio das tags.

![](../.gitbook/assets/tags.png)

Edite `product/product_list.html`

```html
<!-- product_list.html -->
<button onclick="openImportModal()" class="w-1/2 text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center sm:w-auto">
  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
    <path fill-rule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
  </svg>
  Importar
</button>

  <!-- head -->
  <th scope="col" class="p-4 text-left text-xs font-medium text-gray-500 uppercase">
    Preço
  </th>

  <!-- body -->
  <td class="p-4 whitespace-nowrap text-base font-medium text-gray-900">R$ {{ object.price|default:"---" }}</td>

  {\% include "./includes/import_modal.html" %}

{\% block js %}
  <script>
    // ...

    const targetElImport = document.getElementById('import-modal')
    const importModal = new Modal(targetElImport)

    openImportModal = () => {
      importModal.show()
    }
    closeImportModal = () => {
      importModal.hide()
    }
  </script>
{\% endblock js %}
```

Edite `product/product_detail.html`

```html
<!-- Preço -->
<div class="block w-full overflow-x-auto">
  <div class="mt-2">
    <div class="text-sm font-normal text-gray-500">Preço</div>
    <div class="text-base font-semibold text-gray-900">R$ {{ object.price }}</div>
  </div>
</div>
```


Edite `product/includes/import_modal.html`

```html
<!-- import_modal.html -->
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
        <form action="{\% url 'product:import_csv' %}" method="POST" enctype="multipart/form-data">
          {\% csrf_token %}

          <h3 class="text-xl font-normal text-gray-500 mt-5 mb-6">Importar dados de um CSV ou XLSX</h3>

          <input type="file" name="csv_file">

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

Edite `product/urls.py`

```python
# product/urls.py
path('import-csv/', v.import_csv, name='import_csv'),  # noqa E501
```

Edite `product/views.py`

```python
# product/views.py
from django.views.decorators.http import require_http_methods
from .services import csv_to_list_in_memory, save_data


@require_http_methods(['POST'])
def import_csv(request):
    csv_file = request.FILES.get('csv_file')
    data = csv_to_list_in_memory(csv_file)
    save_data(data)
    return redirect('product:product_list')
```

Edite `product/services.py`

```python
# product/services.py
import csv
import io

from .models import Product


def csv_to_list_in_memory(filename: str) -> list:
    '''
    Lê um csv InMemoryUploadedFile e retorna um OrderedDict.
    '''
    file = filename.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(file))
    # Gerando uma list comprehension
    data = [line for line in reader]
    return data


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

# Importando CSV pelo Admin com django-import-export

https://django-import-export.readthedocs.io/en/latest/getting_started.html#importing-data

https://django-import-export.readthedocs.io/en/latest/advanced_usage.html#admin-integration

## Instalação

```
pip install django-import-export

pip freeze | grep django-import-export >> requirements.txt
```

## Configuração

Edite `settings.py`

```python
# settings.py
INSTALLED_APPS = (
    ...
    'import_export',
)
```

Rode o comando

```
python manage.py collectstatic
```

Edite `product/admin.py`

```python
# product/admin.py
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Category, Photo, Product


class ProductResource(resources.ModelResource):

    class Meta:
        model = Product


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_classes = [ProductResource]
    ...
```
