# Dica 30 - Importando CSV InMemoryUploadedFile

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, django-import-export 3.1.0, Tailwind CSS e Flowbite.
{: .versoes }

<a href="https://youtu.be/9JnJHDGt5BI">
    <img src="../.gitbook/assets/youtube.png">
</a>

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

Na [dica anterior](095-29-import-csv.md) importamos um CSV de produtos pela linha de comando. Agora vamos fazer a mesma coisa pelo **front-end** da aplicação: um botão **Importar** na lista de produtos abre um modal com um campo de arquivo; o usuário escolhe o CSV, o arquivo chega na view como um `InMemoryUploadedFile`, nós lemos o conteúdo dele em memória (sem salvar no disco) e gravamos os produtos no banco com `bulk_create`.

No fim, veremos também como importar o mesmo CSV pelo **painel de admin**, com o [django-import-export](https://django-import-export.readthedocs.io/en/latest/).

**Importante:** numa versão antiga desta página as tags de template tinham uma `\` no meio (`{\%`), por causa do GitBook. No vídeo o código foi copiado dessa versão e foi preciso remover a barra. Aqui as tags já estão escritas do jeito certo; se você encontrar `{\%` em algum lugar, troque por `{%`.

![](../.gitbook/assets/tags.png)

## Pré-requisitos

Este tutorial continua o projeto das dicas anteriores (app `backend.product`, com o CRUD de produtos feito com Tailwind CSS e Flowbite). Precisamos de:

* O campo `price` no model `Product`, criado na [dica 29](095-29-import-csv.md):

```python
# backend/product/models.py
class Product(TimeStampedModel):
    title = models.CharField('título', max_length=255, unique=True)
    description = models.TextField('descrição', null=True, blank=True)
    price = models.DecimalField('preço', max_digits=9, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='categoria',
        related_name='products',
        null=True,
        blank=True,
    )
    slug = models.SlugField(null=True, blank=True)
    ...
```

* Um arquivo `/tmp/products.csv` com as colunas `title` e `price`, gerado com o faker-commerce (script `backend/product/gen_products.py`, das dicas [28](094-28-faker-commerce.md) e [29](095-29-import-csv.md)). O começo do arquivo fica assim (os valores mudam a cada vez que o script roda):

```
title,price
Awesome Hat eebc1fde,23.92
Bacon f83adfb0,5.12
Ball 387f27f3,92.36
...
```

## O botão Importar na lista de produtos

Edite `product/product_list.html`. Ao lado do botão **Adicionar** (e antes do **Exportar**), acrescente o botão **Importar**. Repare no `onclick="openImportModal()"`: o modal será aberto via JavaScript.

```html
<!-- backend/product/templates/product/product_list.html -->
<!-- START: Adicionar -->
<div class="flex items-center space-x-2 sm:space-x-3 ml-auto">
  <a href="{% url 'product:product_create' %}" data-modal-toggle="add-user-modal" class="w-1/2 text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center sm:w-auto">
    ...
    Adicionar
  </a>
  <button onclick="openImportModal()" class="w-1/2 text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center sm:w-auto">
    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
      <path fill-rule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
    </svg>
    Importar
  </button>
  <a href="" class="w-1/2 text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center sm:w-auto">
    ...
    Exportar
  </a>
</div>
<!-- END: Adicionar -->
```

Na mesma página, vamos mostrar o preço na tabela. No cabeçalho (`<thead>`), depois da coluna **Descrição**, acrescente:

```html
<!-- head -->
<th scope="col" class="p-4 text-left text-xs font-medium text-gray-500 uppercase">
  Preço
</th>
```

E no corpo (`<tbody>`), a célula do preço entre a descrição e a categoria:

```html
<!-- body -->
<td class="p-4 whitespace-nowrap text-base font-medium text-gray-900">{{ object.description|truncatechars:"50"|default:"---" }}</td>
<td class="p-4 whitespace-nowrap text-base font-medium text-gray-900">R$ {{ object.price|default:"---" }}</td>
<td class="p-4 whitespace-nowrap text-base font-medium text-gray-900">{{ object.category|default:"---" }}</td>
```

No fim do `{% block content %}`, logo abaixo do include do modal de deletar, inclua o modal de importação:

```html
  {% include "./includes/delete_modal.html" %}
  {% include "./includes/import_modal.html" %}

{% endblock content %}
```

E no `{% block js %}`, depois do código do modal de deletar, crie o objeto `Modal` do Flowbite para o novo modal e as funções que o abrem e fecham:

```html
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

    const targetElImport = document.getElementById('import-modal')
    const importModal = new Modal(targetElImport)

    openImportModal = () => {
      importModal.show()
    }
    closeImportModal = () => {
      importModal.hide()
    }
  </script>
{% endblock js %}
```

## O preço na página de detalhes

Edite `product/product_detail.html` e acrescente o preço entre o título e a descrição:

```html
<!-- backend/product/templates/product/product_detail.html -->
<!-- Preço -->
<div class="block w-full overflow-x-auto">
  <div class="mt-2">
    <div class="text-sm font-normal text-gray-500">Preço</div>
    <div class="text-base font-semibold text-gray-900">R$ {{ object.price }}</div>
  </div>
</div>
```

## O modal de importação

Crie o arquivo `product/includes/import_modal.html`:

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
        <form action="{% url 'product:import_csv' %}" method="POST" enctype="multipart/form-data">
          {% csrf_token %}

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

Dois detalhes importantes no formulário:

* `enctype="multipart/form-data"`: **sem ele o arquivo não é enviado**, e `request.FILES` chega vazio na view.
* `name="csv_file"`: é o nome que vamos usar na view para pegar o arquivo (`request.FILES.get('csv_file')`).

O título já diz "CSV ou XLSX" porque o XLSX entra na [dica 33](099-33-import-xlsx.md); por enquanto vamos tratar só o CSV.

Ao clicar em **Importar**, o modal abre com o campo de arquivo e os botões **Sim, importar** e **Não, cancelar**. Enquanto a rota `import_csv` não existir, a página dá erro na tag `{% url %}`; vamos criá-la agora.

## A rota

Edite `product/urls.py` e acrescente a rota `import-csv/` no fim de `product_patterns`:

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
    path('import-csv/', v.import_csv, name='import_csv'),  # noqa E501
]

urlpatterns = [
    path('', include(product_patterns)),
]
```

## A view

Edite `product/views.py`. Acrescente os imports no topo do arquivo e a view `import_csv` no final:

```python
# backend/product/views.py
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import ProductForm
from .models import Product
from .services import csv_to_list_in_memory, save_data

...


@require_http_methods(['POST'])
def import_csv(request):
    csv_file = request.FILES.get('csv_file')
    data = csv_to_list_in_memory(csv_file)
    save_data(data)
    return redirect('product:product_list')
```

* `@require_http_methods(['POST'])` garante que a view só aceita POST; um GET em `/product/import-csv/` devolve `405 Method Not Allowed`.
* O arquivo enviado não vem em `request.POST`, e sim em `request.FILES`, pelo nome do campo (`csv_file`). Para arquivos pequenos (até 2,5 MB, o padrão de `FILE_UPLOAD_MAX_MEMORY_SIZE`) o Django entrega um objeto `InMemoryUploadedFile`: o conteúdo fica na memória, não é gravado no disco.
* Depois de salvar, voltamos para a lista de produtos.

## Lendo o CSV em memória

A lógica fica num arquivo separado. Crie `product/services.py`:

```python
# backend/product/services.py
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

Na dica anterior líamos o CSV com `open(filename)`, porque o arquivo estava no disco. Aqui é diferente: o `InMemoryUploadedFile` não tem caminho, e `filename.read()` devolve **bytes**. Por isso:

1. `filename.read().decode('utf-8')` transforma os bytes em texto (não esqueça o `decode`, senão o `csv` reclama que recebeu bytes);
2. `io.StringIO(file)` embrulha esse texto num objeto que se comporta como um arquivo aberto, que é o que o `csv.DictReader` espera;
3. o `DictReader` usa a primeira linha (`title,price`) como chaves, e a list comprehension devolve uma lista de dicionários, um por linha.

O `save_data` é o mesmo da dica anterior: monta um `Product` para cada item e grava todos de uma vez com `bulk_create`.

Agora, na lista de produtos, clique em **Importar**, escolha o `products.csv` e clique em **Sim, importar**. Os 100 produtos aparecem na lista, já com a coluna **Preço** preenchida.

Como o campo `title` é `unique=True`, se você importar o mesmo arquivo duas vezes o `bulk_create` falha com `IntegrityError` (no PostgreSQL do vídeo: `duplicate key value violates unique constraint "product_product_title_key"`). Essa mensagem aparece no terminal do vídeo; basta apagar os produtos antes de importar de novo.

## Importando CSV pelo Admin com django-import-export

Esta parte também foi publicada como um vídeo curto separado, "django-import-export - Dica #30.1":

<a href="https://youtu.be/SaCCzTRSuYg">
    <img src="../.gitbook/assets/youtube.png">
</a>

E se for preciso importar os dados pelo painel do admin? Para isso usamos o django-import-export:

* [https://django-import-export.readthedocs.io/en/latest/getting_started.html#importing-data](https://django-import-export.readthedocs.io/en/latest/getting_started.html#importing-data)
* [https://django-import-export.readthedocs.io/en/latest/advanced_usage.html#admin-integration](https://django-import-export.readthedocs.io/en/latest/advanced_usage.html#admin-integration)

### Instalação

```bash
pip install django-import-export

pip freeze | grep django-import-export >> requirements.txt
```

No vídeo foi instalada a versão 3.1.0 (`django-import-export==3.1.0` no `requirements.txt`).

### Configuração

Edite `settings.py` e acrescente `import_export` nas apps de terceiros:

```python
# backend/settings.py
INSTALLED_APPS = [
    'backend.accounts',  # <<<
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # apps de terceiros
    'django_extensions',
    'widget_tweaks',
    'django_seed',
    'import_export',
    # minhas apps
    'backend.core',
    'backend.bookstore',
    'backend.crm',
    'backend.expense',
    'backend.product',
    'backend.realty',
    'backend.todo',
]
```

Como pede a documentação, rode o `collectstatic`, porque a biblioteca tem arquivos estáticos próprios para o admin:

```bash
python manage.py collectstatic
```

### O admin

Edite `product/admin.py`. Criamos um `ProductResource` (que descreve como o model é importado e exportado) e trocamos a classe base de `ProductAdmin` de `admin.ModelAdmin` para `ImportExportModelAdmin`:

```python
# backend/product/admin.py
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

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
class ProductAdmin(ImportExportModelAdmin):
    resource_classes = [ProductResource]
    inlines = (PhotoInline,)
    list_display = ('__str__', 'slug', 'category')
    readonly_fields = ('slug',)
    search_fields = ('title',)
    list_filter = ('category',)
    # date_hierarchy = 'created'
```

Atenção ao nome do atributo: no django-import-export 3.x ele é `resource_classes`, no **plural**, e recebe uma lista. No vídeo aparece digitado `resource_class = [ProductResource]` (no singular), e a importação pelo admin dá erro; o código do repositório usa `resource_classes`. O atributo no singular ainda existe na 3.1.0, mas está obsoleto e espera a própria classe, não uma lista: `resource_class = [ProductResource]` gera `TypeError: 'list' object is not callable` ao abrir a tela de importação.

### Importando pelo painel

Na lista de produtos do admin (`/admin/product/product/`) aparecem os botões **Importar** e **Exportar** ao lado de **Adicionar produto**. Para testar, apague os produtos e:

1. clique em **Importar**;
2. escolha o arquivo `products.csv` e o formato **csv**, e clique em **Enviar**;
3. a próxima tela mostra uma prévia dos dados que serão importados; confira e clique em **Confirmar importação**.

O admin mostra a mensagem "A importação foi completada com 100 novas e 0 atualizadas produtos", e os produtos aparecem na lista, agora com o slug preenchido (por exemplo `awesome-hat-eebc1fde`): o admin salva os produtos um a um, então o signal `pre_save` da [dica 27](093-27-signals.md) roda; o `bulk_create` do front não dispara signals, por isso lá o slug fica vazio.

## Conclusão

Vimos duas formas de importar um CSV sem passar pela linha de comando: pelo front, lendo o `InMemoryUploadedFile` com `decode('utf-8')` + `io.StringIO` + `csv.DictReader` e gravando com `bulk_create`; e pelo admin, com o django-import-export. Nas próximas dicas vamos ler o mesmo CSV com [Pandas](097-31-import-csv-pandas.md) e com [Dask](098-32-import-csv-dask.md).
