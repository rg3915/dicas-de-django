# Dica 35 - Django: passando usuário logado no formulário

**Versões usadas no vídeo:** Django 2.2.20 e Python 3.8.
{: .versoes }

<a href="https://youtu.be/69jPO_v6ldI">
    <img src="../.gitbook/assets/youtube.png">
</a>

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

Na [Dica 31](031-django-admin-pegando-usuario-logado-no-admin.md) vimos como pegar o usuário logado no Admin. Agora vamos fazer o mesmo num formulário nosso, fora do Admin.

O formulário (`forms.Form` ou `forms.ModelForm`) não tem acesso ao `request`, então não sabe quem é o usuário logado. A solução é a view, que tem o `request.user`, **passar o usuário para o formulário** quando o cria. Com o usuário dentro do formulário, você pode, por exemplo, filtrar as opções de um campo só com os registros daquele usuário.

## Pré-requisitos

Continuamos o projeto das dicas anteriores: o app `core` dentro de `myproject`, com o `base.html` e as URLs do app no namespace `core`.

## O modelo Person

Em `models.py`, crie o modelo `Person`. Ele herda de `UuidModel`, o modelo abstrato que já existia no projeto e acrescenta um campo `slug` do tipo UUID:

```python
# myproject/core/models.py
import uuid

from django.db import models


class UuidModel(models.Model):
    slug = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


...


class Person(UuidModel):
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
```

A propriedade `full_name` junta nome e sobrenome (o sobrenome é opcional, por isso o `or ""` e o `strip()`), e é usada no `__str__`.

Crie e aplique a migration:

```bash
python manage.py makemigrations
python manage.py migrate
```

```
Migrations for 'core':
  myproject/core/migrations/0007_person.py
    - Create model Person
```

## O formulário recebendo o usuário

Crie o `forms.py` com um `ModelForm` para `Person` e sobrescreva o `__init__` para receber o usuário:

```python
# myproject/core/forms.py
from django import forms

from .models import Person


class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = '__all__'

    def __init__(self, user=None, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        # my_field = MyModel.objects.filter(user=user)
        if user.is_authenticated:
            print(user)
        else:
            print('Não')
```

* `def __init__(self, user=None, *args, **kwargs)`: o primeiro argumento do formulário passa a ser o usuário. Os demais (`*args`, `**kwargs`), como os dados do `request.POST`, seguem para o `__init__` original do `ModelForm`, pelo `super()`.
* Depois do `super()`, o usuário está disponível dentro do formulário e você pode fazer o que quiser com ele. O comentário mostra o uso mais comum: filtrar um campo pelo usuário, algo como `self.fields['my_field'].queryset = MyModel.objects.filter(user=user)`.
* Aqui, para testar, só imprimimos no terminal o usuário, se ele estiver autenticado (`user.is_authenticated`), ou `Não`, se for um visitante anônimo.

## A view

Na view, passe o `request.user` como **primeiro** argumento do formulário:

```python
# myproject/core/views.py
from django.shortcuts import redirect, render

from .forms import PersonForm


def person_create(request):
    template_name = 'core/person_form.html'
    # Não esquecer do request.user como primeiro parâmetro.
    form = PersonForm(request.user, request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('person:person_list')

    context = {'form': form}
    return render(request, template_name, context)
```

* `PersonForm(request.user, request.POST or None)`: o usuário vai para o parâmetro `user`, e `request.POST or None` vai para o `data` do formulário. Num GET, `request.POST` está vazio, então o formulário é criado sem dados (não validado); num POST, recebe os dados enviados.
* Se o formulário for válido, salva a pessoa e redireciona para a lista de pessoas.

**Atenção:** a ordem importa. No vídeo, a primeira versão da view era `PersonForm(request.POST or None)`, sem o `request.user`. Assim, num GET, `user` recebia `None` e a página dava o erro:

```
AttributeError at /persons/create/
'NoneType' object has no attribute 'is_authenticated'
```

Também atenção ao `redirect`: o código do vídeo usa `'person:person_list'`, mas neste projeto as URLs estão no namespace `core` (`app_name = 'core'`). No vídeo o formulário não chega a ser enviado; se você salvar uma pessoa com esse código, ela é gravada, mas o redirecionamento dá `NoReverseMatch: 'person' is not a registered namespace`. Para funcionar neste projeto, use `redirect('core:person_list')`.

## A URL

```python
# myproject/core/urls.py
from django.urls import path

from myproject.core import views as v

app_name = 'core'


urlpatterns = [
    path('', v.index, name='index'),
    path('persons/', v.person_list, name='person_list'),
    path('persons/create/', v.person_create, name='person_create'),
    path('articles/', v.article_list, name='article_list'),
    path('articles/filter/', v.article_filter_list, name='article_filter_list'),
    path('articles/json/', v.article_json, name='article_json'),
]
```

A linha nova é a do `persons/create/`; as outras são das dicas anteriores.

## O template

No vídeo, o arquivo `core/person_form.html` existia, mas estava vazio (a página aparece em branco, porque o objetivo era só ver o usuário no terminal). Para ver e enviar o formulário, um template mínimo:

```html
<!-- myproject/core/templates/core/person_form.html -->
{% extends "base.html" %}

{% block content %}
  <h1>Cadastrar pessoa</h1>
  <form method="POST">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-primary">Salvar</button>
  </form>
{% endblock content %}
```

## Testando

Rode o servidor:

```bash
python manage.py runserver
```

Sem estar logado, abra `http://localhost:8000/persons/create/`: o terminal imprime `Não`, porque o `request.user` é um usuário anônimo (`AnonymousUser`), cujo `is_authenticated` é `False`.

Agora entre no Admin (`http://localhost:8000/admin/`) com o seu usuário e abra de novo `http://localhost:8000/persons/create/`. O terminal mostra o usuário logado (saída do vídeo, com o template ainda vazio, por isso o tamanho `0` da resposta):

```
admin
[24/Apr/2021 07:32:38] "GET /persons/create/ HTTP/1.1" 200 0
```

Pronto: o formulário recebeu o usuário logado.

## Conclusão

Para usar o usuário logado num formulário:

1. acrescente um parâmetro `user` no `__init__` do formulário, antes de `*args` e `**kwargs`, e chame o `super().__init__(*args, **kwargs)`;
2. na view, crie o formulário com `PersonForm(request.user, request.POST or None)`.

Com o usuário dentro do formulário, dá para filtrar querysets de campos, preencher valores iniciais ou validar regras que dependem de quem está logado.
