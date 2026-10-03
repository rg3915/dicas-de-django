# Simples é melhor que complexo - palestra

Publicado em 03/01/2026.

**Testado com:** Django 6.0, HTMX 2 e Python 3.12.
{: .versoes }

<a href="https://youtu.be/tsoBSDNiX2c">
    <img src="../.gitbook/assets/youtube.png">
</a>

Palestra apresentada no Grupy-SP, no aniversário de 18 anos (06/12/2025).

O título vem do Zen do Python (digite `import this` no interpretador): *simples é melhor que complexo*. A palestra é sobre escolher uma stack de desenvolvimento web sem se afogar em opções. Primeiro vêm os argumentos; depois, um exemplo prático de monolito Django com HTMX e Alpine.js, com código completo.

## O problema: opções demais

Numa entrevista, uma recrutadora me perguntou: "Mas você só sabe Python?". A pergunta reflete aquelas vagas genéricas que listam dezenas de tecnologias. E quem está começando sente o mesmo: abre o YouTube e não sabe por onde começar.

Se o objetivo é desenvolvimento web, a busca leva a uma avalanche:

* **JavaScript** no front-end, e com ele React, Vue.js, Angular, Svelte e Next.js.
* **PHP** com Laravel e WordPress (um CMS muito usado para sites de conteúdo).
* **JavaScript no back-end** com Node, Deno ou Bun.
* **Bancos de dados**: relacionais (PostgreSQL, MySQL, MariaDB, Oracle, SQLite) e não relacionais (MongoDB, Cassandra).
* **DevOps**: Docker, Kubernetes, Terraform.
* **Deploy e hospedagem**: AWS, Google Cloud, Oracle Cloud, Nginx, Apache, CI/CD, certificado HTTPS.

Nessa altura você não sabe mais para onde ir. Então vamos recomeçar devagar.

## Comece pelo básico

O mais básico do desenvolvimento web é **HTML e CSS**. HTML é a estrutura (uma linguagem de marcação, não de programação); CSS é a apresentação. Com isso você já faz muita coisa.

Nem todo site precisa de back-end. O próprio Dicas de Django é um site estático, só HTML e CSS, publicado pelo GitHub, sem banco de dados.

Quando precisa de back-end, escolha **uma** linguagem e aprofunde. Aqui é Python, que resolve quase tudo.

## Front e back separados ou monolito?

Separar front-end (uma SPA em React ou Vue) e back-end (uma API em Python) tem um custo que muita gente ignora:

* **o dobro de conhecimento**: você precisa dominar as duas pontas;
* **o dobro de tempo**: duas aplicações, duas rotas, dois deploys;
* **o dobro de dinheiro**: tempo e ferramental a mais custam caro.

Na empresa, você segue a arquitetura que já existe. Mas como freelancer quem decide é você, porque o cliente não é programador: ele quer o sistema funcionando. Se o cliente reclamar que está demorando o dobro, é porque você escolheu o dobro de ferramentas.

O **monolito** é um framework que faz tudo: back-end, front-end e conexão com o banco, num lugar só. Falam mal dele ("e se o servidor cair?"), mas na maioria dos casos você não precisa de tanta interatividade no front, e o monolito resolve o problema.

## A stack simples

* **Front-end**: HTML e CSS (obrigatórios). Se precisar de interatividade, **HTMX** ou **Alpine.js** (a sintaxe do Alpine lembra o Vue: `x-for`, `x-show`, `x-model`).
* **Back-end**: Python e Django. Flask ou FastAPI também servem, mas veja as diferenças abaixo.
* **Banco**: PostgreSQL (ou MySQL). A documentação do Django recomenda desenvolver com o mesmo banco de produção, e não com o SQLite padrão. Eu uso Docker para subir o banco na minha máquina.
* **Infra**: saiba ao menos o básico de Gunicorn e use uma plataforma como serviço (PaaS), em que um `git push` faz o deploy, sem configurar Nginx nem certificado. O Heroku é o mais conhecido, mas não é mais gratuito; existem alternativas como o Fly.io.

## Por que Django

* **ORM**: conecta em PostgreSQL, MySQL, MariaDB ou Oracle com a mesma configuração e o mesmo código.
* **Roteamento** com o `urls.py`.
* **Admin**: CRUD pronto para cada model registrado.
* **MTV**: Model (dados), View (o controlador) e Template (a saída: HTML, TXT, JSON...).
* **Template engine com herança**: o que se repete em todas as páginas fica no `base.html` e as outras páginas herdam.
* **Segurança**: proteção contra XSS, CSRF e, no Django 6.0, suporte nativo a CSP (Content Security Policy).
* **Pacotes de terceiros**: django-extensions, Django Channels (WebSockets, chat), Django Ninja e Django REST framework (APIs), Django Debug Toolbar, django-allauth (login social), django-import-export (CSV, Excel). Isso é uma fração do que existe em [https://djangopackages.org/](https://djangopackages.org/).

Já o **Flask** é minimalista: para chegar perto do Django você adiciona uma biblioteca de formulários, o SQLAlchemy como ORM, o conector do banco e assim por diante. O **FastAPI** é focado em APIs, embora também renderize templates.

E use IA com moderação: se ela faz tudo por você, seu cérebro para de pensar.

## Exemplo prático: lista de tarefas com Django, HTMX e Alpine.js

Vamos provar o argumento com código. Uma lista de tarefas em que você adiciona e conclui tarefas sem recarregar a página, sem API REST, sem JSON e sem build de JavaScript. O HTMX troca pedaços de HTML que o próprio Django renderiza; o Alpine.js cuida de um filtro que roda só no navegador. O exemplo usa os *template partials*, novidade do Django 6.0.

### Pré-requisitos

* Python 3.12 ou mais recente (exigência do Django 6.0).

### Instalação

```bash
mkdir tarefas
cd tarefas
python -m venv .venv
source .venv/bin/activate
pip install "Django==6.0.*"
django-admin startproject config .
python manage.py startapp tarefa
```

No `config/settings.py`, adicione a app e ajuste o idioma:

```python
# config/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tarefa',
]

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'
```

### Model, form e admin

```python
# tarefa/models.py
from django.db import models


class Tarefa(models.Model):
    titulo = models.CharField('título', max_length=100)
    concluida = models.BooleanField('concluída', default=False)
    criada_em = models.DateTimeField('criada em', auto_now_add=True)

    class Meta:
        ordering = ('concluida', '-criada_em')
        verbose_name = 'tarefa'
        verbose_name_plural = 'tarefas'

    def __str__(self):
        return self.titulo
```

```python
# tarefa/forms.py
from django import forms

from .models import Tarefa


class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ('titulo',)
```

```python
# tarefa/admin.py
from django.contrib import admin

from .models import Tarefa


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'concluida', 'criada_em')
    list_filter = ('concluida',)
    search_fields = ('titulo',)
```

Só com o admin você já tem o CRUD completo para uso interno. As telas abaixo são para o usuário final.

### Views

```python
# tarefa/views.py
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .forms import TarefaForm
from .models import Tarefa


def tarefa_list(request):
    context = {
        'object_list': Tarefa.objects.all(),
        'form': TarefaForm(),
    }
    return render(request, 'tarefa/tarefa_list.html', context)


@require_POST
def tarefa_create(request):
    form = TarefaForm(request.POST)
    if form.is_valid():
        tarefa = form.save()
        # Devolve só o pedaço de HTML da nova tarefa (template partial).
        return render(request, 'tarefa/tarefa_list.html#tarefa-item', {'tarefa': tarefa})
    return render(request, 'tarefa/tarefa_list.html#tarefa-erro', {'form': form})


@require_POST
def tarefa_toggle(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk)
    tarefa.concluida = not tarefa.concluida
    tarefa.save(update_fields=['concluida'])
    return render(request, 'tarefa/tarefa_list.html#tarefa-item', {'tarefa': tarefa})
```

O detalhe está no nome do template: `'tarefa/tarefa_list.html#tarefa-item'` renderiza apenas o partial `tarefa-item` definido dentro de `tarefa_list.html`. A página inteira e o fragmento que o HTMX recebe saem do mesmo arquivo, sem duplicar HTML.

### URLs

```python
# tarefa/urls.py
from django.urls import path

from tarefa import views as v

app_name = 'tarefa'

urlpatterns = [
    path('', v.tarefa_list, name='tarefa_list'),
    path('create/', v.tarefa_create, name='tarefa_create'),
    path('<int:pk>/toggle/', v.tarefa_toggle, name='tarefa_toggle'),
]
```

```python
# config/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('tarefa.urls')),
    path('admin/', admin.site.urls),
]
```

### Templates

Crie a pasta `tarefa/templates/tarefa/`.

```html
<!-- tarefa/templates/base.html -->
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Tarefas{% endblock title %}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
  <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.4/dist/htmx.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
</head>
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
  <main class="container">
    {% block content %}{% endblock content %}
  </main>
</body>
</html>
```

O `hx-headers` no `<body>` faz todo request do HTMX levar o token CSRF. A proteção do Django continua ligada, sem configuração extra.

```html
<!-- tarefa/templates/tarefa/tarefa_list.html -->
{% extends "base.html" %}

{% block content %}
  <h1>Tarefas</h1>

  <form
    hx-post="{% url 'tarefa:tarefa_create' %}"
    hx-target="#tarefas"
    hx-swap="afterbegin"
    hx-on::after-request="if (event.detail.successful) this.reset()"
  >
    <fieldset role="group">
      {{ form.titulo }}
      <button type="submit">Adicionar</button>
    </fieldset>
    <div id="erro"></div>
  </form>

  <div x-data="{ esconderConcluidas: false }">
    <label>
      <input type="checkbox" role="switch" x-model="esconderConcluidas">
      Esconder concluídas
    </label>

    <ul id="tarefas">
      {% for tarefa in object_list %}
        {% partial tarefa-item %}
      {% endfor %}
    </ul>
  </div>
{% endblock content %}

{% partialdef tarefa-item %}
  <li
    id="tarefa-{{ tarefa.pk }}"
    x-show="!esconderConcluidas || {{ tarefa.concluida|yesno:'false,true' }}"
  >
    <label>
      <input
        type="checkbox"
        {% if tarefa.concluida %}checked{% endif %}
        hx-post="{% url 'tarefa:tarefa_toggle' tarefa.pk %}"
        hx-target="#tarefa-{{ tarefa.pk }}"
        hx-swap="outerHTML"
      >
      {% if tarefa.concluida %}<s>{{ tarefa.titulo }}</s>{% else %}{{ tarefa.titulo }}{% endif %}
    </label>
  </li>
{% endpartialdef %}

{% partialdef tarefa-erro %}
  <small id="erro" hx-swap-oob="true">{{ form.titulo.errors|join:", " }}</small>
{% endpartialdef %}
```

Como funciona:

* **`{% partialdef %}` e `{% partial %}`**: definem um trecho reutilizável e o usam dentro do `for`. A view acessa o mesmo trecho com `#tarefa-item`.
* **Adicionar** (HTMX): o formulário faz `POST` em `/create/`, a view salva e devolve um `<li>`, que o HTMX insere no começo da lista (`hx-swap="afterbegin"`). Depois do sucesso, `this.reset()` limpa o campo.
* **Concluir** (HTMX): o checkbox faz `POST` em `/<pk>/toggle/` e o `<li>` inteiro é trocado pela versão nova (`hx-swap="outerHTML"`).
* **Erro de validação**: a view devolve o partial `tarefa-erro` com `hx-swap-oob="true"`, que substitui o `<div id="erro">` fora do alvo principal.
* **Filtro** (Alpine.js): `x-data` cria o estado `esconderConcluidas`, o switch altera esse estado com `x-model` e cada `<li>` usa `x-show`. O filtro roda só no navegador, sem ir ao servidor. O Alpine também inicializa os `<li>` que o HTMX insere depois.

### Rodando

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse `http://localhost:8000/`, adicione tarefas, marque algumas como concluídas e ligue "Esconder concluídas". Abra a aba Rede do navegador: as respostas são pedaços de HTML, não JSON. Em `http://localhost:8000/admin/` as mesmas tarefas estão disponíveis para edição.

Tudo isso em um projeto, um deploy, uma linguagem no back-end e nenhuma etapa de build no front.

## Conclusão

Antes de adotar uma SPA, uma API e um pipeline de front-end, pergunte se o problema exige isso. Para a maioria dos sistemas, HTML, CSS, um pouco de HTMX ou Alpine.js, Django e PostgreSQL resolvem, com metade do esforço. Simples é melhor que complexo.

Links:

* Zen do Python: [https://peps.python.org/pep-0020/](https://peps.python.org/pep-0020/)
* HTMX: [https://htmx.org/docs/](https://htmx.org/docs/)
* Alpine.js: [https://alpinejs.dev/](https://alpinejs.dev/)
* Funções nativas de templates do Django (inclui `partialdef`): [https://docs.djangoproject.com/en/6.0/ref/templates/builtins/](https://docs.djangoproject.com/en/6.0/ref/templates/builtins/)
