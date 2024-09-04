# Novidades do Django 5.1

Doc: https://docs.djangoproject.com/en/5.1/releases/5.1/

Github: https://github.com/rg3915/django51


## Middleware de autenticação requerido por padrão

https://docs.djangoproject.com/en/5.1/ref/middleware/#django.contrib.auth.middleware.LoginRequiredMiddleware

O novo **LoginRequiredMiddleware** redireciona todas as solicitações não autenticadas para uma página de login. As views podem permitir solicitações não autenticadas usando o novo decorator **login_not_required()**.

O **LoginRequiredMiddleware** respeita os valores de **login_url** e **redirect_field_name** definidos via o decorator **login_required()**, mas não suporta a definição de **login_url** ou **redirect_field_name** através do **LoginRequiredMixin**.

Para habilitar isso, adicione `"django.contrib.auth.middleware.LoginRequiredMiddleware"` a sua configuração de **MIDDLEWARE**.


```python
# core/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_not_required


@login_not_required
def index(request):
    return render(request, 'index.html')


@login_not_required
def about(request):
    return render(request, 'about.html')


def profile(request):
    return render(request, 'profile.html')
```

```python
# urls.py
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import admin
from django.urls import path

from backend.core import views as v


urlpatterns = [
    path('', v.index, name='index'),
    path('about/', v.about, name='about'),
    path('accounts/profile/', v.profile, name='profile'),
    path(
        'accounts/login/',
        LoginView.as_view(template_name='login.html'),
        name='login'
    ),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),
]
```


Em `settings.py` adicione

```python
# settings.py
MIDDLEWARE = [
    ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.LoginRequiredMiddleware',  # <---
    ...
]


LOGOUT_REDIRECT_URL = 'index'
```

## `{% querystring %}` template tag


Vamos criar uma nova app

```bash
cd backend
python ../manage.py startapp crm
```

Vamos criar um novo comando

```bash
cd ..
python manage.py create_command core -n create_data
```

Vamos pegar `page`, que vem de `request.GET`, a partir de `get_context_data`

```python
def get_context_data(self, *args, **kwargs):
    context = super().get_context_data(*args, **kwargs)
    context['page'] = self.request.GET.get('page', 1)
    return context
```

```html
<p>{{ page }} é a página definida pela variável page.</p>
<p>{{ page.next_page_number }} page.next_page_number não existe.</p>
```

Então, em `pagination.html`, podemos escrever

```html
<a href="{% querystring page=page|add:-1 %}">Previous page is {{ page|add:-1 }}</a>

<a href="{% querystring page=page|add:1 %}">Next page is {{ page|add:1 }}</a>
```

Isso significa que se escrevermos a url

```
http://localhost:8000/person/?search=a
```

O resultado será na verdade

```
http://localhost:8000/person/?search=a&page=1
```

Ou seja, ele mantém o filtro que aplicamos em `?search=a`.

Para isso façamos

```python
    def get_queryset(self):
        queryset = super().get_queryset()

        search = self.request.GET.get('search')

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        return queryset
```

... voltando em `pagination.html`, antes escrevia assim

```html
<a href="?{% if request.GET.search %}search={{ request.GET.search }}{% endif %}&page={{ pg }}">
```

Agora podemos escrever

```html
<nav aria-label="Pagination">
  <ul class="pagination">
    {% if page_obj.has_previous %}
      <li><a href="{% querystring page=1 %}">&laquo;</a></li>
      <li><a href="{% querystring page=page_obj.previous_page_number %}">&lsaquo;</a></li>
    {% endif %}

    {% for pg in page_obj.paginator.page_range %}
      {% if pg <= 3 or pg >= page_obj.paginator.num_pages|add:'-2' %}
        <li class="{% if page_obj.number == pg %}active{% endif %}">
          <a href="{% querystring page=pg %}">{{ pg }}</a>
        </li>
      {% elif pg >= page_obj.number|add:'-3' and pg <= page_obj.number|add:'3' %}
        <li class="{% if page_obj.number == pg %}active{% endif %}">
          <a href="{% querystring page=pg %}">{{ pg }}</a>
        </li>
      {% elif pg == page_obj.number|add:'-4' or pg == page_obj.number|add:'4' %}
        <li><a href="#">...</a></li>
      {% endif %}
    {% endfor %}

    {% if page_obj.has_next %}
      <li><a href="{% querystring page=page_obj.next_page_number %}">&rsaquo;</a></li>
      <li><a href="{% querystring page=page_obj.paginator.num_pages %}">&raquo;</a></li>
    {% endif %}
  </ul>
</nav>
```

## Minor features

### django.contrib.admin

* `ModelAdmin.list_display` agora suporta o uso de `__` para "list fields" de modelos relacionados, ou FK.

```python
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'category__title', 'category__type')
```

Antes gerava o seguinte erro:

```
File "~/.venv/lib/python3.12/site-packages/django/core/management/base.py", line 563, in check
    raise SystemCheckError(msg)
django.core.management.base.SystemCheckError: SystemCheckError: System check identified some issues:

ERRORS:
<class 'backend.core.admin.ProductAdmin'>: (admin.E108) The value of 'list_display[1]' refers to 'category__title', which is not a callable, an attribute of 'ProductAdmin', or an attribute or method on 'core.Product'.
```

Mas agora foi corrigido.

