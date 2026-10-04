# Dica 42 - Custom context processors

**Versões usadas no vídeo:** Django 2.2.24, Python 3.8 e Bootstrap 4.
{: .versoes }

<a href="https://youtu.be/VidyZ5gqSRY">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`). Se copiar código de lá, remova a `\`.

![](../.gitbook/assets/tags.png)


O **Custom context processors** é um recurso que nos fornece objetos globais que podemos usar em qualquer parte da nossa aplicação.

Neste tutorial vamos colocar um contador de viagens no menu do site, ao lado do link **Viagens**, e fazer com que esse número apareça em **todas** as páginas, não só na lista de viagens. Para isso vamos escrever o nosso próprio context processor.

## Pré-requisitos

O vídeo usa o projeto do repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django) (pasta `myproject`), com Django 2.2 e Bootstrap 4. O que importa aqui é o app `travel`, criado na [Dica 40](040-formularios-date-datetime-duration-e-templatetags-de-data.md):

```python
# myproject/travel/models.py
from django.db import models


class Travel(models.Model):
    destination = models.CharField('destino', max_length=200)
    date_travel = models.DateField('data', null=True, blank=True)
    datetime_travel = models.DateTimeField('data/hora', null=True, blank=True)
    time_travel = models.TimeField('tempo', null=True, blank=True)
    duration_travel = models.DurationField('duração', null=True, blank=True)

    class Meta:
        ordering = ('destination',)
        verbose_name = 'viagem'
        verbose_name_plural = 'viagens'

    def __str__(self):
        return self.destination
```

```python
# myproject/travel/views.py
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import TravelForm
from .models import Travel


class TravelListView(ListView):
    model = Travel
    paginate_by = 10


class TravelCreateView(CreateView):
    model = Travel
    form_class = TravelForm
    success_url = reverse_lazy('travel:travel_list')
```

```python
# myproject/travel/urls.py
from django.urls import path

from myproject.travel import views as v

app_name = 'travel'


urlpatterns = [
    path('', v.TravelListView.as_view(), name='travel_list'),
    path('create/', v.TravelCreateView.as_view(), name='travel_create'),
]
```

O menu fica em `myproject/core/templates/nav.html`, que é incluído no `base.html` de todas as páginas.

## O problema: contar no template da lista

A primeira ideia é usar o que a página de viagens já tem. A `TravelListView` manda o `object_list` para o template, então dá para contar ali mesmo, no menu:

```html
<!-- myproject/core/templates/nav.html (primeira tentativa) -->
<li class="nav-item">
    <a class="nav-link" href="{% url 'travel:travel_list' %}">
        Viagens
        <span class="badge badge-warning">{{ object_list.count }}</span>
    </a>
</li>
```

Na página de viagens, aparentemente funciona. Mas repare nos problemas:

* Na **Home**, o número some, porque a view da home não manda nenhum `object_list`.
* Em **Pessoas** e em **Artigos**, aparece um número, mas é a contagem de pessoas e de artigos, porque essas páginas também mandam um `object_list` (de outro model).
* Mesmo na página de viagens, a lista é paginada (`paginate_by = 10`), então o `object_list` tem no máximo 10 itens, e não o total.

O que queremos é a quantidade de viagens, sempre, em qualquer página. Ou seja, uma variável **global** de template.

## O que é um context processor

Um context processor é uma função que recebe o `request` e devolve um dicionário. A cada template renderizado com `request` (como fazem o `render()` e as class based views), o Django chama todos os context processors listados em `settings.py` e junta esses dicionários no contexto do template.

Você já usa vários sem perceber. Em `settings.py`, dentro de `TEMPLATES`, estão os padrões do projeto:

* `django.template.context_processors.debug`: disponibiliza `debug` e `sql_queries`;
* `django.template.context_processors.request`: disponibiliza o `request` em todos os templates;
* `django.contrib.auth.context_processors.auth`: disponibiliza o `user` e as `perms`;
* `django.contrib.messages.context_processors.messages`: disponibiliza as `messages`.

É por isso que `{{ user }}` e `{{ request }}` funcionam em qualquer template. Agora vamos criar o nosso.

## Criando o context processor

Crie o arquivo `context_processors.py` dentro do app `travel`. No vídeo ele foi criado direto no terminal, com `cat`:

```bash
cat << EOF > myproject/travel/context_processors.py
from .models import Travel


def travel_count(request):
    travel = Travel.objects.all()
    context = {'total_travel': travel.count()}
    return context

EOF
```

O arquivo fica assim:

```python
# myproject/travel/context_processors.py
from .models import Travel


def travel_count(request):
    travel = Travel.objects.all()
    context = {'total_travel': travel.count()}
    return context
```

* A função recebe o `request` (obrigatório, mesmo que não seja usado).
* `travel.count()` faz um `SELECT COUNT(*)` no banco, sem carregar as viagens.
* A chave do dicionário, `total_travel`, é o nome da variável que vamos usar no template. Ela tem um nome diferente do nome da função (`travel_count`) de propósito, para deixar claro que o que vai para o template é a **chave do dicionário**, e não o nome da função.

## Registrando em settings.py

Acrescente o caminho completo da função na lista `context_processors`:

```python
# myproject/settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR,
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # apps
                'myproject.travel.context_processors.travel_count',
            ],
        },
    },
]
```

O caminho é `pacote.app.módulo.função`: `myproject.travel.context_processors.travel_count`.

## Usando a variável no menu

Em `nav.html`, troque o `{{ object_list.count }}` por `{{ total_travel }}`:

```html
<!-- myproject/core/templates/nav.html -->
<li class="nav-item">
    <a class="nav-link" href="{% url 'travel:travel_list' %}">
        Viagens
        <span class="badge badge-warning">{{ total_travel }}</span>
    </a>
</li>
```

O `badge badge-warning` é a classe do Bootstrap 4 que desenha o número num selo amarelo.

Reinicie o servidor (`python manage.py runserver`) e navegue pelo site. O selo ao lado de **Viagens** mostra o total de viagens cadastradas (no vídeo, 15) em todas as páginas: Home, Pessoas, Artigos e Viagens.

## Cuidado: use com moderação

O context processor roda em **todo** template renderizado com `request`, em todas as páginas do site. No nosso exemplo, isso significa uma query `COUNT` a mais em cada página. Um ou dois contadores simples não pesam, mas, se você colocar consultas pesadas ou muitos context processors, o sistema inteiro fica lento. Use com moderação, e só para o que realmente precisa estar em todas as páginas.

Pronto: com uma função de poucas linhas e uma linha no `settings.py`, temos um objeto global disponível na aplicação inteira.
