# Dica 26 - Paginação e Breadcrumb

**Importante:** remova a `\` no meio das tags.

![](../.gitbook/assets/tags.png)

## Paginação

[https://docs.djangoproject.com/en/4.1/topics/pagination/#using-paginator-in-a-view-function](https://docs.djangoproject.com/en/4.1/topics/pagination/#using-paginator-in-a-view-function)

Edite `product/views.py`

```python
# from django.views.generic import ListView

# class ProductListView(ListView):
#     model = Product
#     paginate_by = 10
```

```python
from django.core.paginator import Paginator

def product_list(request):
    template_name = 'product/product_list.html'
    object_list = Product.objects.all()

    search = request.GET.get('search')

    ...

    # https://docs.djangoproject.com/en/4.1/topics/pagination/#using-paginator-in-a-view-function
    items_per_page = 10
    paginator = Paginator(object_list, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'items_count': page_obj.object_list.count(),
    }
    return render(request, template_name, context)
```

## Botões da Paginação

Edite `product/includes/navigation_buttons.html`

```html
<!-- navigation_buttons.html -->
<div class="flex items-center space-x-3">
  {\% if page_obj.has_previous %}
    <a href="?page={{ page_obj.previous_page_number }}&search={{ request.GET.search }}"
  {\% endif %}
  {\% if page_obj.has_next %}
    <a href="?page={{ page_obj.next_page_number }}&search={{ request.GET.search }}"
  {\% endif %}
</div>
```

O `&search={{ request.GET.search }}` mantém a **busca paginada**.


```html
<!-- navigation_buttons.html -->
<div class="flex items-center space-x-3">
  {\% if page_obj.has_previous %}
    <a
      href="?page={{ page_obj.previous_page_number }}&search={{ request.GET.search }}"
      class="flex-1 text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center"
    >
      <svg class="-ml-1 mr-1 h-5 w-5"" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"> <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"></path>
        </svg>
        Anterior
        </a>
  {\% endif %}
  {\% if page_obj.has_next %}
    <a href="?page={{ page_obj.next_page_number }}&search={{ request.GET.search }}" class="flex-1 text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center">
      Próximo
      <svg class="-mr-1 ml-1 h-5 w-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
          </svg>
          </a>
  {\% endif %}
  </div>
```

## Arruma o contador de itens

```html
<div class="flex items-center mb-4 sm:mb-0">
  {\% if page_obj.has_previous %}
    <a href="?page={{ page_obj.previous_page_number }}&search={{ request.GET.search }}" class="text-gray-500 hover:text-gray-900 cursor-pointer p-1 hover:bg-gray-100 rounded inline-flex justify-center">
      <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>
    </a>
  {\% endif %}
  {\% if page_obj.has_next %}
    <a href="?page={{ page_obj.next_page_number }}&search={{ request.GET.search }}" class="text-gray-500 hover:text-gray-900 cursor-pointer p-1 hover:bg-gray-100 rounded inline-flex justify-center mr-2">
      <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>
    </a>
  {\% endif %}
  <span class="text-sm font-normal text-gray-500"><span class="text-gray-900 font-semibold">Página {{ page_obj.number }} de {{ page_obj.paginator.num_pages }}</span> - Mostrando <span class="text-gray-900 font-semibold">{{ items_count }}</span> de <span class="text-gray-900 font-semibold">{{ page_obj.paginator.count }}</span> items</span>
</div>
```

### Move os arquivos para a pasta `core`

```
mv backend/product/templates/product/includes/navigation_buttons.html backend/core/templates/includes/
mv backend/product/templates/product/includes/search.html backend/core/templates/includes/
```

Edite `product_list.html`

```html
{\% include "includes/search.html" %}
{\% include "includes/navigation_buttons.html" %}
```


## breadcrumb

```
mv backend/product/templates/product/includes/breadcrumb.html backend/core/templates/includes/
```

Edite `product_list.html`, `product_detail.html` e `product_form.html`

```html
{\% include "includes/breadcrumb.html" %}
```

Edite `product/models.py`

```python
class Product(TimeStampedModel):
    ...

    def list_url(self):
        return reverse_lazy('product:product_list')

    @property
    def verbose_name(self):
        return self._meta.verbose_name

    @property
    def verbose_name_plural(self):
        return self._meta.verbose_name_plural
```

Edite `product/views.py`

```python
def product_create(request):
    template_name = 'product/product_form.html'
    form = ProductForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('product:product_list')

    verbose_name_plural = form.instance._meta.verbose_name_plural
    context = {
        'form': form,
        'verbose_name_plural': verbose_name_plural
    }
    return render(request, template_name, context)
```

Edite core/includes/breadcrumb.html

```html
<!-- breadcrumb.html -->
<nav class="flex mb-5" aria-label="Breadcrumb">
  <ol class="inline-flex items-center space-x-1 md:space-x-2">
    <li class="inline-flex items-center">
      <a href="{\% url 'core:dashboard' %}" class="text-gray-700 hover:text-gray-900 inline-flex items-center">
        <svg class="w-5 h-5 mr-2.5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path></svg>
        Home
      </a>
    </li>
    <li>
      <div class="flex items-center">
        <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>
        {\% if object.pk %}
          <a href="{{ object.list_url }}" class="text-gray-700 hover:text-gray-900 ml-1 md:ml-2 text-sm font-medium">
            {{ object.verbose_name_plural }}
          </a>
        {\% elif 'create' in request.path %}
          <a href="javascript:window.history.go(-1)" class="text-gray-700 hover:text-gray-900 ml-1 md:ml-2 text-sm font-medium">
            {{ verbose_name_plural }}
          </a>
        {\% else %}
          <a href="{{ page_obj.0.list_url }}" class="text-gray-700 hover:text-gray-900 ml-1 md:ml-2 text-sm font-medium">
            {{ page_obj.0.verbose_name_plural }}
          </a>
        {\% endif %}
      </div>
    </li>
    <li>
      <div class="flex items-center">
        <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>
        <span class="text-gray-400 ml-1 md:ml-2 text-sm font-medium" aria-current="page">
          {\% if 'create' in request.path %}
            Adicionar
          {\% elif object.pk and 'update' in request.path %}
            Editar
          {\% elif object.pk %}
            Detalhe
          {\% else %}
            Lista
          {\% endif %}
        </span>
      </div>
    </li>
  </ol>
</nav>
```