# Dica 24 - Alpine.js e Django

```
cd backend
python ../manage.py todo
cd ..
```


Edite `urls.py`

```python
path('todo/', include('backend.todo.urls', namespace='todo')),  # noqa E501
```

Edite `settings.py`

```python
INSTALLED_APPS = [
    ...
    'backend.todo',
]
```

Edite `todo/apps.py`

```python
name = 'backend.todo'
```



Edite `todo/models.py`

```python
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

Edite `todo/admin.py`

```python
from django.contrib import admin

from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'done')
    search_fields = ('task',)
    list_filter = ('done',)
```



Edite `todo/urls.py`

```python
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



Edite `todo/views.py`

```python
from django.views.decorators.http import require_http_methods
import json
from django.http import JsonResponse
from django.shortcuts import render

from .models import Todo
from django.views.decorators.csrf import csrf_exempt


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

Edite `core/templates/base.html`

```html
<!-- Alpine.js -->
<script src="//unpkg.com/alpinejs" defer></script>
```


Edite core/templates/includes/aside.html

```html
<li>
  <a href="{% url 'todo:todo_list' %}" target="_blank" class="text-base text-gray-900 font-normal rounded-lg hover:bg-gray-100 group transition duration-75 flex items-center p-2">
    <svg class="w-6 h-6 text-gray-500 flex-shrink-0 group-hover:text-gray-900 transition duration-75" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"></path><path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"></path></svg>
    <span class="ml-3">Tarefas</span>
  </a>
</li>
```

Crie a pasta

```
mkdir -p backend/todo/templates/todo
touch backend/todo/templates/todo/todo_list.html
```

todo_list.html versão base:

```html
<!-- todo_list.html versão base: -->
<!-- todo_list.html -->
{% extends "base.html" %}
{% load static %}

{% block content %}
<!-- x-data="" -->
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
        <form class="lg:pr-3">
          <div class="hidden sm:flex items-center sm:divide-x sm:divide-gray-100 mb-3 sm:mb-0">
            <label for="users-search" class="sr-only">Tarefa</label>
            <div class="mt-1 relative lg:w-64 xl:w-96">
              <!-- x-model="task" e x-ref="task" -->
              <input
                type="text"
                class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5"
                placeholder="Nova Tarefa..."
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
              <template>
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
                      >
                      <svg fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"></path>
                      </svg>
                    </button>
                  </td>
                  <!-- @click="toggleDone(todo)" -->
                  <td
                    class="p-4 flex items-center whitespace-nowrap space-x-6 mr-12 lg:mr-0"
                  >
                    <div class="text-sm font-normal text-gray-500">
                      <!-- :class="{ 'text-gray-500': todo.done, 'text-gray-900': !todo.done }"
                        x-text="todo.task" -->
                      <div
                        class="text-base font-semibold"
                      >
                        tarefa
                      </div>
                    </div>
                  </td>
                  <td class="p-4 whitespace-nowrap space-x-2">
                    <!-- @click="deleteTask(todo)" -->
                    <button type="button" class="text-white bg-red-600 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm inline-flex items-center px-3 py-2 text-center">
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

```html
<!-- versão final -->
<!-- todo_list.html -->
{% extends "base.html" %}
{% load static %}

{% block content %}
<!-- x-data="" -->
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
      <span class="text-sm font-normal text-gray-500">Mostrando <span class="text-gray-900 font-semibold" x-text="'1-'+todos.length">1-20</span> de <span class="text-gray-900 font-semibold" x-text="todos.length">2000</span></span>
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


Crie `todo.js`

```
touch backend/core/static/js/todo.js
```

```js
// todo.js
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
      .then(data => {
        this.todos = data
      })
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
        headers: { 'Content-Type': 'application/json' },
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
