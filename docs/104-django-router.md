# Django Router

**Versões usadas no vídeo:** Django 5.1.3, Python 3.12, django-router 1.0.8 e django-extensions 3.2.3.
{: .versoes }

<a href="https://youtu.be/Z6qH9YehjUU?si=wKuNsmgj1ZTkLtvU">
    <img src="../.gitbook/assets/youtube.png">
</a>


Veja a [documentação](https://pypi.org/project/django-router/)

E veja o código no [Github](https://github.com/rg3915/django-router-tutorial/)

Veja o [CustomRouter](https://github.com/rg3915/django-router-tutorial/blob/main/apps/core/custom_router.py)

Veja o uso em [views.py](https://github.com/rg3915/django-router-tutorial/blob/main/apps/crm/views.py)

O Flask, o FastAPI e até o Django Ninja definem rotas com um decorator em cima da função. O Django padrão não tem isso: ele trabalha com views e, separadamente, com um `urls.py` que liga cada url a cada view. Que tal usar a mesma ideia de decorator de rotas no Django, para renderizar os templates?

É isso que a biblioteca [django-router](https://pypi.org/project/django-router/) faz: você escreve `@router.path()` em cima da view e não precisa mais manter o `urls.py` de cada app.

Nesta dica vamos ver:

1. o uso básico, com as apps no mesmo nível da pasta do projeto;
2. o problema das rotas geradas para as views de função;
3. um `CustomRouter` para o caso em que as apps são subpastas da pasta do projeto (o jeito que eu gosto de trabalhar), gerando as rotas do jeito ideal.

## Instalação

```bash
pip install django-router
```

Edite `settings.py` e coloque `django_router` em `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    ...
    'django_router',
    ...
]
```

E, no `urls.py` principal, importe o `router` e some `router.urlpatterns` no fim de `urlpatterns`:

```python
# urls.py
from django_router import router

# a única vez que você precisa mexer num `urls.py`
urlpatterns = router.urlpatterns

# ou, junto com as urls que já existem
urlpatterns = [
    ...
] + router.urlpatterns
```

Pronto. Agora vamos ver isso em detalhe.

## Apps no mesmo nível da pasta do projeto

Este é o jeito com que você provavelmente está acostumado: a pasta do projeto (aqui chamada `apps`, com `settings.py` e `urls.py`) e as apps `accounts`, `core` e `crm` ao lado dela.

```
.
├── accounts
│   └── views.py
├── apps
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core
│   └── views.py
├── crm
│   └── views.py
└── manage.py
```

Em `settings.py`, além do `django_router`, usamos o `django_extensions`, por causa do comando `show_urls` que veremos daqui a pouco:

```python
# apps/settings.py
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
    'django_router',
    # my apps
    'accounts.apps.AccountsConfig',
    'core.apps.CoreConfig',
    'crm.apps.CrmConfig',
]
```

O `urls.py` principal:

```python
# apps/urls.py
from django.contrib import admin
from django.urls import include, path
from django_router import router


# urlpatterns = router.urlpatterns

urlpatterns = [
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls')),  # without namespace
    path('admin/', admin.site.urls),
] + router.urlpatterns
```

Repare que **não existe** mais um `include('crm.urls')`: o `urls.py` da app `crm` não é mais usado. No início do vídeo ele aparece assim, para comparação:

```python
# crm/urls.py (não é mais necessário)
from django.urls import path
from apps.crm import views as v

app_name = 'crm'

urlpatterns = [
    path('', v.person_list, name='person_list'),
]
```

Agora as rotas ficam nas próprias views, com `@router.path()`. No `crm/views.py` temos o CRUD de `Person` duas vezes, com views de função e com *class based views*. O comentário ao lado de cada decorator mostra a rota que o django-router gera:

```python
# crm/views.py
from django_router import router
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView
)

from .forms import PersonForm
from .mixins import SearchMixin
from .models import Person


@router.path()  # /crm/person_list/
def person_list(request):
    template_name = 'crm/person_list.html'
    object_list = Person.objects.all()

    search = request.GET.get('search')
    if search:
        object_list = object_list.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
        )

    context = {'object_list': object_list}
    return render(request, template_name, context)


@router.path()  # /crm/person_detail/
# @router.path('person/<int:pk>/')
def person_detail(request, pk):
    template_name = 'crm/person_detail.html'
    obj = Person.objects.get(pk=pk)
    context = {'object': obj}
    return render(request, template_name, context)


@router.path()  # /crm/person_create/
def person_create(request):
    template_name = 'crm/person_form.html'
    form = PersonForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('crm:person_list')

    context = {'form': form}
    return render(request, template_name, context)


@router.path()  # /crm/person_update/
def person_update(request, pk):
    template_name = 'crm/person_form.html'
    instance = Person.objects.get(pk=pk)
    form = PersonForm(request.POST or None, instance=instance)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('crm:person_list')

    context = {'form': form}
    return render(request, template_name, context)


@router.path()  # /crm/person_delete/
def person_delete(request, pk):
    template_name = 'crm/person_confirm_delete.html'
    obj = Person.objects.get(pk=pk)

    if request.method == 'POST':
        obj.delete()
        return redirect('crm:person_list')

    context = {'object': obj}
    return render(request, template_name, context)


@router.path()  # /crm/person/
class PersonListView(SearchMixin, ListView):
    model = Person
    paginate_by = 10


@router.path()  # /crm/person/<int:pk>/
class PersonDetailView(DetailView):
    model = Person


@router.path()  # /crm/person/create/
class PersonCreateView(CreateView):
    model = Person
    form_class = PersonForm


@router.path()  # /crm/person/<int:pk>/update/
class PersonUpdateView(UpdateView):
    model = Person
    form_class = PersonForm


@router.path()  # /crm/person/<int:pk>/delete/
class PersonDeleteView(DeleteView):
    model = Person
    success_url = reverse_lazy('crm:person_list')
```

O `SearchMixin` só aplica o filtro de busca na `ListView`:

```python
# crm/mixins.py
from django.db.models import Q


class SearchMixin:

    def get_queryset(self):
        queryset = super(SearchMixin, self).get_queryset()
        search = self.request.GET.get('search')
        if search:
            return queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )
        return queryset
```

### Como o django-router monta as rotas

* O **namespace** é o primeiro pedaço do módulo da view: `crm.views` vira `crm`. Todas as rotas da app ficam debaixo de `crm/` e com nome `crm:...`.
* Para **views de função**, a rota e o nome são o nome da função: `person_list` vira `/crm/person_list/`, com nome `crm:person_list`.
* Para **class based views**, ele usa o nome do model e o tipo da view: `ListView` vira `person/`, `DetailView` vira `person/<int:pk>/`, `CreateView` vira `person/create/`, `UpdateView` vira `person/<int:pk>/update/` e `DeleteView` vira `person/<int:pk>/delete/`. O `<int:pk>` entra sozinho para as views de um objeto só (`SingleObjectMixin`, exceto a `CreateView`).
* Se quiser, você pode passar a rota e o nome direto no decorator: `@router.path('person/<int:pk>/', name='person_detail')`.

### Vendo as rotas com `show_urls`

O comando `show_urls`, do django-extensions, lista todas as rotas do projeto:

```bash
python manage.py show_urls
```

As rotas do CRM (sem as do Admin) ficam assim:

```
/crm/person/                    crm.views.PersonListView     crm:person_list
/crm/person/<int:pk>/           crm.views.PersonDetailView   crm:person_detail
/crm/person/<int:pk>/delete/    crm.views.PersonDeleteView   crm:person_delete
/crm/person/<int:pk>/update/    crm.views.PersonUpdateView   crm:person_update
/crm/person/create/             crm.views.PersonCreateView   crm:person_create
/crm/person_create/             crm.views.person_create      crm:person_create
/crm/person_delete/             crm.views.person_delete      crm:person_delete
/crm/person_detail/             crm.views.person_detail      crm:person_detail
/crm/person_list/               crm.views.person_list        crm:person_list
/crm/person_update/             crm.views.person_update      crm:person_update
```

As class based views ficaram certinhas. Mas tem uma coisa que eu não gostei: cadê o `<int:pk>` do `person_detail`, do `person_update` e do `person_delete` de função? Não tem. Como a biblioteca não sabe que a função recebe `pk`, essas três rotas simplesmente não funcionam. Daria para resolver passando a rota na mão (`@router.path('person/<int:pk>/')`, comentado no código acima), mas aí perderíamos a graça do decorator sem argumentos.

## Apps como subpastas da pasta do projeto

O jeito que eu gosto de trabalhar é com as apps **dentro** da pasta principal `apps`, e cada app só com o `views.py` (o `urls.py` não é mais necessário):

```
.
├── apps
│   ├── accounts
│   │   └── views.py
│   ├── core
│   │   └── views.py
│   ├── crm
│   │   └── views.py
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

Agora o módulo da view é `apps.crm.views`, e o namespace padrão do django-router (o primeiro pedaço) seria `apps`, o que não queremos. Por isso, mantendo essa estrutura, eu preferi criar um `CustomRouter`.

Este é o projeto do repositório [rg3915/django-router-tutorial](https://github.com/rg3915/django-router-tutorial). Para rodar:

```bash
git clone https://github.com/rg3915/django-router-tutorial.git
cd django-router-tutorial

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python contrib/env_gen.py

python manage.py migrate
python manage.py runserver
```

```
# requirements.txt
Django==5.1.3
django-ninja==1.3.0
dj-database-url==2.3.0
django-extensions==3.2.3
django-localflavor==4.0
django-widget-tweaks==1.5.0
Faker==33.0.0
isort==5.13.2
python-decouple==3.8
django-router==1.0.8
```

Nas apps, o `name` do `apps.py` passa a ter o prefixo `apps.` (por exemplo `name = 'apps.crm'`), e em `settings.py`:

```python
# apps/settings.py
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
    'django_router',
    # my apps
    'apps.accounts.apps.AccountsConfig',
    'apps.core.apps.CoreConfig',
    'apps.crm.apps.CrmConfig',
]
```

### O código original do `Router`

O `Router` da biblioteca fica no `__init__.py` do pacote `django_router`. Os métodos que nos interessam são estes (versão 1.0.8):

```python
# django_router/__init__.py (trecho da biblioteca)
class Router:
    def __init__(self):
        self._namespaces = dict()

    def path(self, pattern=None, name=None, **kwargs):
        def _wrapper(view):
            self._push(path, pattern, view, name, kwargs)
            return view

        return _wrapper

    ...

    def _push(self, func, pattern, view, name, kwargs):
        namespace = view.__module__.split(".")[0]
        self._namespaces.setdefault(namespace, []).append(
            (func, pattern, view, name, kwargs)
        )

    def _get_params(self, view, parameter_map):
        pattern_parts = []
        name_parts = []
        if settings.SIMPLE_AUTO_NAMING or not isinstance(view, type):
            pattern_parts.append(from_camel(view.__name__))
            name_parts.append(from_camel(view.__name__))
        else:
            ...

    @property
    def urlpatterns(self):
        ...
            urlpatterns.append(path(f"{namespace}/", (paths, namespace, namespace)))

        return urlpatterns


router = Router()
```

* `_push` guarda cada view decorada, agrupada pelo namespace, que é o elemento `[0]` do módulo;
* `_get_params` calcula a rota e o nome: para função, é só o nome da função;
* `urlpatterns` monta os `path()` e coloca cada grupo debaixo de `f"{namespace}/"`.

### O `CustomRouter`

Crie o arquivo `apps/core/custom_router.py` com a classe `CustomRouter`, herdando de `Router` e sobrescrevendo esses três métodos. As linhas alteradas estão marcadas com `# <---`:

```python
# apps/core/custom_router.py
# ... (outros imports: veja o arquivo completo no GitHub)
from django_router import Router
# ...


class CustomRouter(Router):
    def _push(self, func, pattern, view, name, kwargs):
        # Get second element of tuple.
        namespace = view.__module__.split(".")[1]  # <---

        self._namespaces.setdefault(namespace, []).append(
            (func, pattern, view, name, kwargs)
        )

    def _get_params(self, view, parameter_map):
        pattern_parts = []
        name_parts = []
        if settings.SIMPLE_AUTO_NAMING or not isinstance(view, type):
            _view = from_camel(view.__name__)  # <---

            # Replace suffix.
            suffix_replacements = {
                '_list': '',
                '_create': '/add',
                '_detail': '/<int:pk>',
                '_update': '/<int:pk>/update',
                '_delete': '/<int:pk>/delete'
            }

            for suffix, replacement in suffix_replacements.items():
                if _view.endswith(suffix):
                    _view = _view.replace(suffix, replacement)
                    break

            pattern_parts.append(_view)  # <---

            name_parts.append(from_camel(view.__name__))
        # ... (o resto do método é igual ao da biblioteca)

    @property
    def urlpatterns(self):
        # ...
                # "slugify" url
                pattern = pattern.replace("_", "-")
                # ...
            # urlpatterns.append(path(f"{namespace}/", (paths, namespace, namespace)))
            urlpatterns.append(path("", (paths, namespace, namespace)))  # <---

        return urlpatterns


router = CustomRouter()
```

Código completo: [apps/core/custom_router.py](https://github.com/rg3915/django-router-tutorial/blob/815cc7dcaf0d9a8ca73542834a0f83ee43c91db7/apps/core/custom_router.py)

O que mudou:

* **`_push`**: onde estava `[0]` eu coloquei `[1]`, porque quero o nome da app, lembrando que ela é uma subpasta. `apps.crm.views` dá o namespace `crm`.
* **`_get_params`**: para as views de função, escrevi o dicionário `suffix_replacements`, que troca o sufixo do nome da função (verificado com `endswith`) pela rota correta: `_list` some, `_create` vira `/add`, `_detail` vira `/<int:pk>`, `_update` vira `/<int:pk>/update` e `_delete` vira `/<int:pk>/delete`. Depois faço o `append` do resultado em `pattern_parts`. O nome da rota continua sendo o nome da função. O resto do método permanece igual; só tive que copiá-lo da biblioteca para sobrescrever.
* **`urlpatterns`**: troco `_` por `-` na rota, para a url ficar no formato de slug; e, no `append` final, tirei o `f"{namespace}/"` e deixei `""`. Como `MODULE_PATH_MAP` é `True` por padrão, o caminho do módulo entre `apps` e `views` (`crm`) já entra como prefixo da rota, então o namespace no `path` duplicaria o `crm/`.

### Usando o `CustomRouter`

No `urls.py` principal, importe o `router` do `custom_router` em vez do `django_router`:

```python
# apps/urls.py
from django.contrib import admin
from django.urls import include, path
# from django_router import router
from apps.core.custom_router import router


# urlpatterns = router.urlpatterns

urlpatterns = [
    path('', include('apps.core.urls', namespace='core')),
    path('accounts/', include('apps.accounts.urls')),  # without namespace
    path('admin/', admin.site.urls),
] + router.urlpatterns
```

Na app `accounts`, a `SignUpView` usa o router com a rota e o nome escritos explicitamente. Daria para usar só `@router.path()`, mas você pode escrever o nome se quiser:

```python
# apps/accounts/views.py
# from django_router import router
from apps.core.custom_router import router
from django.urls import reverse_lazy
from django.views.generic import CreateView
from apps.accounts.forms import SignupForm


@router.path('signup/', name='signup')
# @router.path()
class SignUpView(CreateView):
    form_class = SignupForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'
```

As rotas de login e logout continuam no `apps/accounts/urls.py`, com as views prontas do Django:

```python
# apps/accounts/urls.py
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path


urlpatterns = [
    path(
        'login/',
        LoginView.as_view(template_name='accounts/login.html'),
        name='login'
    ),
    path('logout/', LogoutView.as_view(), name='logout'),
]
```

E o `apps/crm/views.py`, que é onde mais mudou: o import do router agora vem do `custom_router`, e todos os decorators ficam só `@router.path()`. No fim, alguns exemplos de rota escrita do seu jeito:

```python
# apps/crm/views.py
from apps.core.custom_router import router
# ... (outros imports: veja o arquivo completo no GitHub)


@router.path()
def person_list(request):
    template_name = 'crm/person_list.html'
    object_list = Person.objects.all()
    # ...


@router.path()
def person_detail(request, pk):
    # ...


# ... (person_create, person_update e person_delete)


@router.path()
class PersonListView(SearchMixin, ListView):
    model = Person
    paginate_by = 10


@router.path()
class PersonDetailView(DetailView):
    model = Person

# ... (PersonCreateView, PersonUpdateView e PersonDeleteView: veja o arquivo completo no GitHub)


@router.path()
def person_export_csv(request):
    return HttpResponse('export-person')


@router.path('person/export/csv/')
def person_export_csv2(request):
    return HttpResponse('export-person')


@router.path('person/export/excel/')
def person_export_excel(request):
    return HttpResponse('export-person')
```

Código completo: [apps/crm/views.py](https://github.com/rg3915/django-router-tutorial/blob/815cc7dcaf0d9a8ca73542834a0f83ee43c91db7/apps/crm/views.py)

As views de exportação são só exemplos: `person_export_csv` mostra a rota automática (que não termina em nenhum dos sufixos do dicionário), e `person_export_csv2` e `person_export_excel` mostram a rota escrita à mão.

O formulário e o model usados pelas views:

```python
# apps/crm/forms.py
from django import forms

from .models import Person


class PersonForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Person
        # fields = '__all__'
        fields = (
            'first_name',
            'last_name',
            'email',
            'address',
            'address_number',
            'complement',
            'district',
            'city',
            'uf',
            'cep',
            'country',
            'cpf',
            'rg',
            'cnh',
            'active',
        )

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['active'].widget.attrs['class'] = None
```

```python
# apps/crm/models.py
from django.db import models
from django.urls import reverse_lazy
from apps.core.models import Active, Address, Document, TimeStampedModel


class Person(TimeStampedModel, Address, Document, Active):
    first_name = models.CharField('nome', max_length=50)
    last_name = models.CharField('sobrenome', max_length=50, null=True, blank=True)  # noqa E501
    email = models.EmailField(null=True, blank=True)

    class Meta:
        ordering = ('first_name',)
        verbose_name = 'pessoa'
        verbose_name_plural = 'pessoas'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name or ""}'.strip()

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse_lazy('crm:person_detail', kwargs={'pk': self.pk})

    def get_fields_verbose_names(self):
        return [{'name': field.verbose_name, 'value': getattr(self, field.name)} for field in self._meta.fields]
```

Os models abstratos (`TimeStampedModel`, `Address`, `Document` e `Active`) estão em `apps/core/models.py`, e os templates (Bootstrap 4) em `apps/crm/templates/crm/`, no repositório.

### Conferindo as rotas

```bash
python manage.py show_urls
```

Agora as rotas estão do jeito que eu queria (sem as do Admin):

```
/                               apps.core.views.index                core:index
/accounts/login/                django.contrib.auth.views.LoginView  login
/accounts/logout/               django.contrib.auth.views.LogoutView logout
/accounts/signup/               apps.accounts.views.SignUpView       accounts:signup
/crm/person-export-csv/         apps.crm.views.person_export_csv     crm:person_export_csv
/crm/person/                    apps.crm.views.PersonListView        crm:person_list
/crm/person/                    apps.crm.views.person_list           crm:person_list
/crm/person/<int:pk>/           apps.crm.views.PersonDetailView      crm:person_detail
/crm/person/<int:pk>/           apps.crm.views.person_detail         crm:person_detail
/crm/person/<int:pk>/delete/    apps.crm.views.PersonDeleteView      crm:person_delete
/crm/person/<int:pk>/delete/    apps.crm.views.person_delete         crm:person_delete
/crm/person/<int:pk>/update/    apps.crm.views.PersonUpdateView      crm:person_update
/crm/person/<int:pk>/update/    apps.crm.views.person_update         crm:person_update
/crm/person/add/                apps.crm.views.person_create         crm:person_create
/crm/person/create/             apps.crm.views.PersonCreateView      crm:person_create
/crm/person/export/csv/         apps.crm.views.person_export_csv2    crm:person_export_csv2
/crm/person/export/excel/       apps.crm.views.person_export_excel   crm:person_export_excel
```

As views de função `person_list`, `person_detail`, `person_update` e `person_delete` agora geram as mesmas rotas das class based views, com o `<int:pk>` onde precisa, e `person_create` virou `/crm/person/add/`; e os exemplos de exportação aparecem com a rota automática (`/crm/person-export-csv/`, com hífen) e com as rotas escritas à mão.

Repare que, como o exemplo tem o CRUD duas vezes, as views de função e as class based views geram a mesma url com o mesmo nome. Nesse caso o Django usa a primeira que aparece na lista. Num projeto de verdade você escolheria um dos dois estilos.

## Conclusão

Com o django-router as rotas ficam junto das views, com um decorator, como no Flask, no FastAPI e no Django Ninja, e os `urls.py` das apps deixam de existir. Para views de função e para apps dentro de uma pasta principal, um `CustomRouter` de poucas linhas deixa as urls exatamente no formato que queremos.
