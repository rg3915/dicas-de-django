# Dica 24 - Alpine.js e Django

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, Alpine.js 3 (via unpkg) e Tailwind CSS.
{: .versoes }

<a href="https://youtu.be/jTvfN0DctnQ">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

Alpine.js: [https://alpinejs.dev](https://alpinejs.dev)

Neste tutorial vamos montar uma lista de tarefas (to-do list) combinando **Alpine.js** com **Django**. A ideia é esta:

```
Usuário  <-->  Template  <-->  Django
                  ^              ^
                  |              |
               Alpine.js <--> API REST
```

* O usuário acessa um **template** que é renderizado pelo Django, como qualquer página.
* O Django também fornece uma pequena **API REST** (views que devolvem `JsonResponse`, sem Django REST framework).
* O **Alpine.js** consome essa API com `fetch` e insere os dados no template.

Ou seja, o template continua sendo renderizado pelo Django; a única coisa que o Alpine.js faz é buscar os dados na API e mostrá-los na página, além de enviar as alterações (criar, concluir e deletar tarefas) de volta para a API.

## Pré-requisitos

O vídeo continua o projeto do repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django) (Django 4.1, Python 3.10), que já tem:

* o pacote `backend` com as apps (`backend.core`, `backend.product` etc.) e o `manage.py` na raiz;
* o model abstrato `TimeStampedModel` em `backend/core/models.py`;
* o layout `base.html` com Tailwind CSS (o tema Windster, da Themesberg), com menu lateral em `includes/aside.html` e um `{% block js %}` no fim do `body`.

Para referência, o `TimeStampedModel` é este:

```python
# backend/core/models.py
from django.db import models


class TimeStampedModel(models.Model):
    created = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )
    modified = models.DateTimeField(
        'modificado em',
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        abstract = True
```

Se você estiver usando outro projeto, basta ter um `base.html` com `{% block content %}` e `{% block js %}`; as classes do Tailwind só afetam a aparência.

## Criando a app todo

Como as apps ficam dentro da pasta `backend`, entre nela para rodar o `startapp`:

```bash
cd backend
python ../manage.py startapp todo
cd ..
```

Registre a app em `settings.py`:

```python
# backend/settings.py
INSTALLED_APPS = [
    ...
    'backend.todo',
]
```

E ajuste o `name` em `apps.py`, porque a app está dentro do pacote `backend`:

```python
# backend/todo/apps.py
from django.apps import AppConfig


class TodoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.todo'
```

Inclua as URLs da app no `urls.py` principal:

```python
# backend/urls.py
urlpatterns = [
    ...
    path('todo/', include('backend.todo.urls', namespace='todo')),  # noqa E501
    path('admin/', admin.site.urls),  # noqa E501
]
```

## O model Todo

```python
# backend/todo/models.py
from django.db import models

from backend.core.models import TimeStampedModel


class Todo(TimeStampedModel):
    task = models.CharField('tarefa', max_length=100)
    done = models.BooleanField('feita', default=False)

    class Meta:
        ordering = ('task',)
        verbose_name = 'tarefa'
        verbose_name_plural = 'tarefas'

    def __str__(self):
        return f'{self.task}'

    def to_dict(self):
        return {
            'id': self.id,
            'task': self.task,
            'done': self.done,
        }
```

O método `to_dict()` é o nosso "serializer": ele transforma uma tarefa num dicionário com `id`, `task` e `done`, que o `JsonResponse` converte em JSON.

Registre o model no admin:

```python
# backend/todo/admin.py
from django.contrib import admin

from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'done')
    search_fields = ('task',)
    list_filter = ('done',)
```

Crie e rode as migrações e suba o servidor:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Saída (no vídeo):

```
Migrations for 'todo':
  backend/todo/migrations/0001_initial.py
    - Create model Todo
...
Django version 4.1.3, using settings 'backend.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Cadastre algumas tarefas pelo admin para ter dados para listar.

## As URLs

Crie o arquivo `todo/urls.py`:

```python
# backend/todo/urls.py
from django.urls import include, path

from backend.todo import views as v

app_name = 'todo'

todo_patterns = [
    path('', v.todos, name='todos'),  # noqa E501
    path('<int:pk>/done/', v.todo_done, name='todo_done'),  # noqa E501
    path('<int:pk>/delete/', v.todo_delete, name='todo_delete'),  # noqa E501
]

urlpatterns = [
    path('', v.todo_list, name='todo_list'),  # noqa E501
    path('api/v1/', include(todo_patterns)),
]
```

Ficamos com:

| URL | View | Para quê |
|---|---|---|
| `/todo/` | `todo_list` | renderiza o template |
| `/todo/api/v1/` | `todos` | `GET` lista as tarefas, `POST` cria uma |
| `/todo/api/v1/<pk>/done/` | `todo_done` | `POST` marca ou desmarca a tarefa como concluída |
| `/todo/api/v1/<pk>/delete/` | `todo_delete` | `DELETE` apaga a tarefa |

## As views (a API)

Este é o `views.py` completo. Abaixo explicamos cada view.

```python
# backend/todo/views.py
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Todo


def todo_list(request):
    '''
    Renderiza um template para as tarefas.
    '''
    template_name = 'todo/todo_list.html'
    return render(request, template_name)


def todos(request):
    '''
    Retorna as tarefas via API REST, ou adiciona uma nova.
    '''
    todos = Todo.objects.all()

    if request.method == 'POST':
        # Desserializa os dados.
        data = json.loads(request.body)

        # Salva a tarefa.
        todo = Todo.objects.create(task=data['task'])

        # Retorna o objeto.
        return JsonResponse(todo.to_dict())

    data = [todo.to_dict() for todo in todos]
    # Retorna uma lista.
    return JsonResponse(data, safe=False)


@csrf_exempt
@require_http_methods(['POST'])
def todo_done(request, pk):
    '''
    Conclui uma tarefa via API REST.
    '''
    data = json.loads(request.body)
    done = data.get('done')
    try:
        todo = Todo.objects.get(pk=pk)
        todo.done = done
        todo.save()
        return JsonResponse({'success': True})
    except Todo.DoesNotExist:
        return JsonResponse({'success': False})


@csrf_exempt
@require_http_methods(['DELETE'])
def todo_delete(request, pk):
    '''
    Deleta uma tarefa via API REST.
    '''
    todo = Todo.objects.get(pk=pk)
    todo.delete()
    return JsonResponse({'success': True})
```

* **`todo_list`**: só renderiza o template `todo/todo_list.html`, sem contexto nenhum. Os dados virão da API.
* **`todos`**: no `GET`, monta uma lista com *list comprehension* usando o `to_dict()` de cada tarefa e devolve com `JsonResponse(data, safe=False)`. O `safe=False` é obrigatório porque estamos devolvendo uma **lista**, e o `JsonResponse` por padrão só aceita dicionário.
* No `POST` da mesma view, os dados chegam **no corpo da requisição em JSON** (o Alpine.js envia `JSON.stringify(...)`), e não como dados de formulário. Por isso usamos `json.loads(request.body)`, e não `request.POST`. Criamos a tarefa e devolvemos o objeto criado, que o front-end vai acrescentar no fim da tabela.
* **`todo_done`**: recebe `pk` pela URL e `done` no corpo JSON; atualiza a tarefa e responde `{'success': True}`, ou `{'success': False}` se a tarefa não existir. `@require_http_methods(['POST'])` aceita apenas `POST`.
* **`todo_delete`**: aceita só `DELETE` e apaga a tarefa.

As duas últimas views usam `@csrf_exempt`. A view `todos` não usa: no `POST` ela exige o token CSRF, que vamos mandar no cabeçalho `X-CSRFToken` (veja abaixo).

## Adicionando o Alpine.js no base.html

No `<head>` do `base.html`, inclua o script do Alpine.js. Não esqueça do `defer`:

```html
<!-- backend/core/templates/base.html -->
    <!-- Alpine.js -->
    <script src="//unpkg.com/alpinejs" defer></script>

  </head>
```

O `base.html` do projeto termina com um bloco para scripts de cada página:

```html
<!-- backend/core/templates/base.html -->
    {% block js %}{% endblock js %}
  </body>
</html>
```

## Link no menu lateral

Em `core/templates/includes/aside.html`, acrescente o item **Tarefas** logo depois de **Produtos**:

```html
<!-- backend/core/templates/includes/aside.html -->
<li>
  <a href="{% url 'todo:todo_list' %}" class="text-base text-gray-900 font-normal rounded-lg hover:bg-gray-100 group transition duration-75 flex items-center p-2">
    <svg class="w-6 h-6 text-gray-500 flex-shrink-0 group-hover:text-gray-900 transition duration-75" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"></path><path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"></path></svg>
    <span class="ml-3">Tarefas</span>
  </a>
</li>
```

No vídeo o link foi colado com `target="_blank"` e por isso abria em outra aba; o atributo foi removido em seguida, e o código acima já está sem ele.

## O template todo_list.html

Crie a pasta e o arquivo:

```bash
mkdir -p backend/todo/templates/todo
touch backend/todo/templates/todo/todo_list.html
```

**Importante:** numa versão antiga desta página as tags de template tinham uma `\` no meio (`{\%`), por causa do GitBook. No vídeo o código foi copiado dessa versão e foi preciso remover a barra. Se você encontrar `{\%` em algum lugar, troque por `{%`.

![](../.gitbook/assets/tags.png)

No vídeo, primeiro colamos uma **versão base** do template: o layout da tabela, sem nenhum atributo do Alpine.js (só com comentários indicando onde cada um entra), e com uma única linha fixa com o texto "tarefa". Depois, fomos acrescentando os atributos do Alpine.js um a um, junto com o JavaScript. Abaixo está a **versão final**; os comentários `<!-- ... -->` são os da versão base e marcam onde cada atributo foi colocado.

```html
<!-- backend/todo/templates/todo/todo_list.html -->
{% extends "base.html" %}
{% load static %}

{% block content %}
  <div x-data="getTodos">
    <!-- START: header -->
    <div class="p-4 bg-white block sm:flex items-center justify-between border-b border-gray-200 lg:mt-1.5">
      <div class="mb-1 w-full">
        <div class="mb-4">
          <!-- { include "./includes/breadcrumb.html" %} -->
          <h1 class="text-xl sm:text-2xl font-semibold text-gray-900">Tarefas</h1>
        </div>
        <div class="sm:flex">
          <!-- @submit.prevent="" -->
          <form class="lg:pr-3" @submit.prevent="saveData">
            <div class="hidden sm:flex items-center sm:divide-x sm:divide-gray-100 mb-3 sm:mb-0">
              <label for="users-search" class="sr-only">Tarefa</label>
              <div class="mt-1 relative lg:w-64 xl:w-96">
                <!-- x-model="task" e x-ref="task" -->
                <input
                  type="text"
                  class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5"
                  placeholder="Nova Tarefa..."
                  x-model="task"
                  x-ref="task"
                >
                <!-- x-ref="task" para receber o foco após o submit -->
              </div>
              <button type="submit" class="text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium rounded-lg text-sm px-3 py-2 ml-1 w-full sm:w-auto text-center">Salvar</button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <!-- END: header -->
    <!-- START: table -->
    <div class="flex flex-col">
      <div class="overflow-x-auto">
        <div class="align-middle inline-block min-w-full">
          <div class="shadow overflow-hidden">
            <table class="table-fixed min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-100">
                <tr>
                  <th scope="col" class="p-4">
                    <div class="flex items-center">
                      <input id="checkbox-all" aria-describedby="checkbox-1" type="checkbox"
                        class="bg-gray-50 border-gray-300 focus:ring-3 focus:ring-cyan-200 h-4 w-4 rounded">
                      <label for="checkbox-all" class="sr-only">checkbox</label>
                    </div>
                  </th>
                  <th scope="col" class="p-4 text-left text-xs font-medium text-gray-500 uppercase">
                    Concluída
                  </th>
                  <th scope="col" class="p-4 text-left text-xs font-medium text-gray-500 uppercase">
                    Tarefa
                  </th>
                  <th scope="col" class="p-4 text-left text-xs font-medium text-gray-500 uppercase">
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <!-- x-for -->
                <template x-for="todo in todos" :key="todo.id">
                  <tr class="hover:bg-gray-100">
                    <td class="p-4 w-4">
                      <div class="flex items-center">
                        <input id="checkbox-1" aria-describedby="checkbox-1" type="checkbox"
                          class="bg-gray-50 border-gray-300 focus:ring-3 focus:ring-cyan-200 h-4 w-4 rounded">
                        <label for="checkbox-1" class="sr-only">checkbox</label>
                      </div>
                    </td>
                    <td class="p-4 w-4">
                      <!-- x-show="todo.done" -->
                      <button
                        class="text-green-500 w-10"
                        x-show="todo.done"
                      >
                        <svg fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"></path>
                        </svg>
                      </button>
                    </td>
                    <!-- @click="toggleDone(todo)" -->
                    <td
                      class="p-4 flex items-center whitespace-nowrap space-x-6 mr-12 lg:mr-0"
                      @click="toggleDone(todo)"
                    >
                      <div class="text-sm font-normal text-gray-500">
                        <!-- :class="{ 'text-gray-500': todo.done, 'text-gray-900': !todo.done }"
                        x-text="todo.task" -->
                        <div
                          class="text-base font-semibold"
                          :class="{ 'text-gray-500': todo.done, 'text-gray-900': !todo.done }"
                          x-text="todo.task"
                        >
                          tarefa
                        </div>
                      </div>
                    </td>
                    <td class="p-4 whitespace-nowrap space-x-2">
                      <!-- @click="deleteTask(todo)" -->
                      <button @click="deleteTask(todo)" type="button" class="text-white bg-red-600 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm inline-flex items-center px-3 py-2 text-center">
                        <svg class="mr-2 h-5 w-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>
                        Deletar
                      </button>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    <!-- END: table -->
    <!-- START: footer of table -->
    <div class="bg-white sticky sm:flex items-center w-full sm:justify-between bottom-0 right-0 border-t border-gray-200 p-4">
      <div class="flex items-center mb-4 sm:mb-0">
        <a href="#" class="text-gray-500 hover:text-gray-900 cursor-pointer p-1 hover:bg-gray-100 rounded inline-flex justify-center">
          <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>
        </a>
        <a href="#" class="text-gray-500 hover:text-gray-900 cursor-pointer p-1 hover:bg-gray-100 rounded inline-flex justify-center mr-2">
          <svg class="w-7 h-7" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>
        </a>
        <!-- x-text="'1-'+todos.length" -->
        <!-- x-text="todos.length" -->
        <span class="text-sm font-normal text-gray-500">Mostrando <span class="text-gray-900 font-semibold">1-20</span> de <span class="text-gray-900 font-semibold">2000</span></span>
      </div>
      <!-- { include "./includes/navigation_buttons.html" %} -->
    </div>
    <!-- END: footer of table -->
  </div>
{% endblock content %}

{% block js %}
  <!-- https://adamj.eu/tech/2022/10/06/how-to-safely-pass-data-to-javascript-in-a-django-template/#separate-script-files -->
  <script
    src="{% static 'js/todo.js' %}"
    data-csrf="{{ csrf_token }}"
  ></script>
{% endblock js %}
```

Os pontos importantes, de cima para baixo:

* **`x-data="getTodos"`** na `div` que envolve todo o conteúdo: cria o componente do Alpine.js. Tudo o que está dentro dela enxerga as propriedades e métodos do objeto devolvido pela função `getTodos` (definida no `todo.js`).
* **`@submit.prevent="saveData"`** no `form`: ao enviar o formulário, impede o envio normal (o `.prevent` faz o `preventDefault()`) e chama `saveData`.
* **`x-model="task"`** no `input`: liga o valor do campo à propriedade `task` (*two-way binding*).
* **`x-ref="task"`** no mesmo `input`: cria uma referência ao elemento, para devolver o foco a ele depois de salvar (`this.$refs.task.focus()`).
* **`<template x-for="todo in todos" :key="todo.id">`**: repete a linha `<tr>` para cada tarefa da lista `todos`. O `x-for` precisa ficar numa tag `<template>`.
* **`x-show="todo.done"`** no botão verde: o ícone de "concluída" só aparece quando `done` é verdadeiro.
* **`@click="toggleDone(todo)"`** na célula da tarefa: clicar no nome da tarefa marca ou desmarca a tarefa como concluída. Passamos o próprio objeto `todo` da iteração.
* **`:class="{ 'text-gray-500': todo.done, 'text-gray-900': !todo.done }"`**: tarefa concluída fica em cinza claro; não concluída, em cinza escuro.
* **`x-text="todo.task"`**: escreve o nome da tarefa no lugar do texto fixo "tarefa".
* **`@click="deleteTask(todo)"`** no botão vermelho: apaga a tarefa.

No fim, o `{% block js %}` carrega o `todo.js` e passa o token CSRF num atributo `data-csrf`.

O rodapé da tabela ficou com o texto fixo "Mostrando 1-20 de 2000" no vídeo. Se quiser que ele mostre a quantidade real de tarefas, use os dois `x-text` indicados nos comentários:

```html
<span class="text-sm font-normal text-gray-500">Mostrando <span class="text-gray-900 font-semibold" x-text="'1-'+todos.length">1-20</span> de <span class="text-gray-900 font-semibold" x-text="todos.length">2000</span></span>
```

## Passando dados do Django para o JavaScript

Repare neste trecho do template:

```html
<script
  src="{% static 'js/todo.js' %}"
  data-csrf="{{ csrf_token }}"
></script>
```

Ele segue a recomendação do artigo do Adam Johnson, [How to safely pass data to JavaScript in a Django template](https://adamj.eu/tech/2022/10/06/how-to-safely-pass-data-to-javascript-in-a-django-template/), na seção *Separate script files*: o JavaScript fica num arquivo separado, e os valores que vêm do Django (no exemplo do artigo, o `username`; no nosso caso, o `csrf_token`) são passados em atributos `data-*` da própria tag `<script>`. Dentro do arquivo, lemos esses atributos com `document.currentScript.dataset`:

```js
const data = document.currentScript.dataset
const csrftoken = data.csrf
```

`data-csrf` vira `dataset.csrf`. Como o `todo.js` é carregado sem `defer`, o `document.currentScript` funciona, e o arquivo é executado antes do Alpine.js (que está com `defer`) inicializar o componente.

## O JavaScript: todo.js

Crie o arquivo na pasta de estáticos da app `core`:

```bash
touch backend/core/static/js/todo.js
```

Código completo:

```js
// backend/core/static/js/todo.js
const data = document.currentScript.dataset
const csrftoken = data.csrf

const getTodos = () => ({
  url: '/todo/api/v1/',
  todos: [],
  task: '',
  required: false,

  init() {
    this.getData()
  },

  getData() {
    // Pega os dados no backend com fetch.
    fetch(this.url)
      .then(response => response.json())
      .then(data => this.todos = data)
  },

  saveData() {
    // Verifica se task foi preenchido.
    if (!this.task) {
      this.required = true
      return
    }
    // Salva os dados no backend.
    fetch(this.url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
      body: JSON.stringify({
        task: this.task
      })
    })
    .then(response => response.json())
    .then((data) => {
      this.todos.push(data)
      this.task = ''
      this.$refs.task.focus()
    })
  },

  // Marca a tarefa como feita ou não.
  toggleDone(todo) {
    fetch(`/todo/api/v1/${todo.id}/done/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
      body: JSON.stringify({
        done: !todo.done
      })
    })
    .then(response => response.json())
    .then((data) => {
      if (data.success) todo.done = !todo.done
    })
  },

  deleteTask(todo) {
    fetch(`/todo/api/v1/${todo.id}/delete/`, {
      method: 'DELETE',
    })
    .then(response => response.json())
    .then((data) => {
      if (data.success) {
        this.todos.splice(this.todos.indexOf(todo), 1)
      }
    })
  }
})
```

Agora cada parte.

### Estado inicial e listagem

`getTodos` é uma função que devolve um objeto: é ele que o `x-data="getTodos"` usa como estado do componente.

* `url`: o endpoint da API, `/todo/api/v1/`.
* `todos`: a lista de tarefas, começa vazia.
* `task`: o texto do campo "Nova Tarefa...", ligado pelo `x-model`.
* `required`: marca se o usuário tentou salvar com o campo vazio.

O Alpine.js chama `init()` automaticamente quando o componente é criado. Ele chama `getData()`, que faz um `fetch` na URL, converte a resposta em JSON e guarda em `this.todos`. Como o `x-for` está ligado a `todos`, a tabela é desenhada assim que os dados chegam.

### Criando uma tarefa: saveData

1. Se `task` estiver vazio, marca `required` e sai do método.
2. Faz um `POST` em `/todo/api/v1/` com os cabeçalhos `Content-Type: application/json` e **`X-CSRFToken`** (o token lido do `data-csrf`) e o corpo `JSON.stringify({ task: this.task })`.
3. A view devolve a tarefa criada; o `this.todos.push(data)` a coloca como último item da tabela.
4. Limpa o campo (`this.task = ''`) e devolve o foco ao `input` com `this.$refs.task.focus()`, graças ao `x-ref="task"`.

Repare que o endpoint é o mesmo da listagem; o que muda é o método (`POST`), e a view `todos` trata os dois casos.

### Concluindo uma tarefa: toggleDone

Recebe o objeto `todo` e faz um `POST` em `` `/todo/api/v1/${todo.id}/done/` `` (template string com crase) enviando `done: !todo.done`, ou seja, o contrário do valor atual. Se a resposta tiver `success`, inverte `todo.done` também no front-end; o `x-show` e o `:class` atualizam a linha sozinhos.

### Deletando uma tarefa: deleteTask

Faz uma requisição `DELETE` em `` `/todo/api/v1/${todo.id}/delete/` ``, sem cabeçalho nem corpo. Se der certo, remove a tarefa da lista com `this.todos.splice(this.todos.indexOf(todo), 1)`: o `indexOf` acha a posição do objeto e o `splice` remove um item a partir dela.

## Testando

Acesse `http://localhost:8000/todo/` (ou clique em **Tarefas** no menu lateral):

* a tabela mostra as tarefas cadastradas no admin, com o ícone verde nas concluídas;
* digite uma nova tarefa e clique em **Salvar** (ou tecle Enter): ela aparece no fim da tabela, o campo é limpo e continua com o foco;
* clique no nome de uma tarefa para marcá-la ou desmarcá-la como concluída;
* clique em **Deletar** para removê-la.

Tudo isso sem recarregar a página, e com o template renderizado pelo Django.

Também dá para testar a API direto, por exemplo no shell do Django com o cliente de testes:

```python
import json
from django.test import Client

c = Client()
c.post('/todo/api/v1/', json.dumps({'task': 'Estudar Alpine.js'}), content_type='application/json').json()
# {'id': 1, 'task': 'Estudar Alpine.js', 'done': False}
c.post('/todo/api/v1/1/done/', json.dumps({'done': True}), content_type='application/json').json()
# {'success': True}
c.get('/todo/api/v1/').json()
# [{'id': 1, 'task': 'Estudar Alpine.js', 'done': True}]
c.delete('/todo/api/v1/1/delete/').json()
# {'success': True}
```

O cliente de testes não verifica o CSRF por padrão. No navegador, o `POST` em `/todo/api/v1/` sem o cabeçalho `X-CSRFToken` é recusado com **403 Forbidden**, e é por isso que passamos o token para o `todo.js`.

Pronto: com poucas linhas de JavaScript, o Alpine.js consome uma API feita com views simples do Django e deixa a página interativa, sem precisar de um framework front-end completo.
