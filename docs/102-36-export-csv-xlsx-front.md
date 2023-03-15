# Exportando CSV e XLSX pelo front no projeto

## Exportar CSV ou XLSX pelo front

Edite `product/product_list.html`

```html
<button onclick="openExportModal()" class="w-1/2 text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center sm:w-auto">
  <svg class="-ml-1 mr-2 h-6 w-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clip-rule="evenodd"></path></svg>
  Exportar
</button>

  {% include "./includes/export_modal.html" %}

{% block js %}
  <script>
    // ...

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

Edite `product/includes/export_modal.html`

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

Edite `product/urls.py`

```python
path('export/csv/', v.export_csv, name='export_csv'),  # noqa E501
path('export/xlsx/', v.export_xlsx, name='export_xlsx'),  # noqa E501
```

Edite `product/views.py`

```python
import csv
from pyexcelerate import Workbook

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

## Exportar apenas itens selecionados no Admin

```python
# product/admin.py
from import_export.admin import ImportExportModelAdmin, ExportActionModelAdmin

class ProductAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    ...
```