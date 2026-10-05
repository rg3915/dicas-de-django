# Dica 20 - Templates

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, django-widget-tweaks 1.4.12 e Tailwind CSS com o template Windster (Flowbite).
{: .versoes }

<a href="https://youtu.be/uQ4OMkzoBvY">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`). Se copiar código de lá, remova a `\`.

![](../.gitbook/assets/tags.png)

Até aqui o projeto **Dicas de Django** tem login e um dashboard, mas o dashboard é só um template: nada nele retorna dados reais. Nesta dica vamos fazer o item **Usuários** do menu funcionar e, com isso, criar um **padrão de templates** que será repetido em todas as apps do projeto:

* uma subpasta em `templates` com o mesmo nome da app;
* `<model>_list.html` (lista), `<model>_detail.html` (detalhes) e `<model>_form.html` (formulário de adicionar e de editar);
* uma pasta `includes` com os pedaços reaproveitáveis (breadcrumb, busca, botões de navegação e modal de exclusão);
* as urls e views `list`, `create`, `detail` e `update`, sempre na mesma ordem.

Neste vídeo o formulário ainda não salva; isso fica para as próximas dicas.

## Pré-requisitos

* O projeto das dicas anteriores, na branch `main` do repositório [rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django).
* O `docker-compose` do projeto com PostgreSQL, pgAdmin e MailHog. O banco fica no container (porta 5431), mas o Django roda na máquina local (`localhost:8000`).
* O usuário customizado com login por e-mail (dica 14), o `Profile` na app `accounts` (dica 19.7) e o `CustomUserForm` (dica 17).
* `django-widget-tweaks` instalado e com `'widget_tweaks'` em `INSTALLED_APPS`.

Suba os containers, rode as migrations e crie os usuários:

```bash
docker-compose up -d
python manage.py migrate
python manage.py createsuperuser  # admin@email.com
python manage.py createsuperuser  # regis@email.com
python manage.py runserver
```

## A estrutura de pastas

O Django sugere que, dentro de `templates`, exista uma subpasta com o **mesmo nome da app**. Assim o template é referenciado como `accounts/user_list.html` e não colide com templates de mesmo nome de outras apps.

A app `accounts` já tinha `templates/email` e `templates/registration`. Vamos criar `templates/accounts` e, dentro dela, a pasta `includes`:

```bash
mkdir -p backend/accounts/templates/accounts/includes
```

No vídeo a pasta foi criada primeiro como `include`, no singular, e depois renomeada com `mv backend/accounts/templates/accounts/include/ backend/accounts/templates/accounts/includes`.

Agora os arquivos. Um truque para criar cada arquivo já com um comentário dizendo o nome dele é usar `echo`:

```bash
echo '<!-- user_list.html -->' > backend/accounts/templates/accounts/user_list.html
echo '<!-- user_detail.html -->' > backend/accounts/templates/accounts/user_detail.html
echo '<!-- user_form.html -->' > backend/accounts/templates/accounts/user_form.html

echo '<!-- breadcrumb.html -->' > backend/accounts/templates/accounts/includes/breadcrumb.html
echo '<!-- delete_modal.html -->' > backend/accounts/templates/accounts/includes/delete_modal.html
echo '<!-- navigation_buttons.html -->' > backend/accounts/templates/accounts/includes/navigation_buttons.html
echo '<!-- search.html -->' > backend/accounts/templates/accounts/includes/search.html
```

Com `tree backend/accounts` a parte de templates fica assim:

```
templates
├── accounts
│   ├── includes
│   │   ├── breadcrumb.html
│   │   ├── delete_modal.html
│   │   ├── navigation_buttons.html
│   │   └── search.html
│   ├── user_detail.html
│   ├── user_form.html
│   └── user_list.html
├── email
│   └── account_activation_email.html
└── registration
    ├── login.html
    ├── password_reset_complete.html
    ├── password_reset_confirm.html
    ├── password_reset_done.html
    ├── password_reset_email.html
    ├── password_reset_form.html
    └── registration_form.html
```

## As urls

As rotas de usuário ficam numa lista própria, `user_patterns`, incluída em `users/`:

```python
# accounts/urls.py
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from backend.accounts import views as v

# A ordem das urls é importante por causa do slug, quando existir.
user_patterns = [
    path('', v.user_list, name='user_list'),  # noqa E501
    path('create/', v.user_create, name='user_create'),  # noqa E501
    path('<int:pk>/', v.user_detail, name='user_detail'),  # noqa E501
    path('<int:pk>/update/', v.user_update, name='user_update'),  # noqa E501
]

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # noqa E501
    path('logout/', LogoutView.as_view(), name='logout'),  # noqa E501
    ...
    path('users/', include(user_patterns)),
]
```

* O `# noqa E501` serve só para o linter não reclamar de linha longa (e o autopep8 não quebrar a linha); fica mais fácil de ler.
* Termine sempre a rota com `/`, para manter o padrão.
* A ordem é `list`, `create`, `detail`, `update`. Ela importa quando a rota usa slug: `create/` precisa vir antes de `<slug:slug>/`, senão a palavra "create" seria interpretada como um slug.

Como a app `accounts` é incluída em `accounts/`, as rotas ficam `/accounts/users/`, `/accounts/users/create/`, `/accounts/users/1/` e `/accounts/users/1/update/`.

## A lista de usuários

### Primeiro, o mínimo

Todo template começa com `extends` e `block content`. Para testar a rota, comece com uma tabela fixa:

```html
<!-- user_list.html -->
{% extends "base.html" %}

{% block content %}
  <h1>Lista</h1>

  <table>
    <tbody>
      <tr>
        <td>Usuário 1</td>
      </tr>
      <tr>
        <td>Usuário 1</td>
      </tr>
      <tr>
        <td>Usuário 1</td>
      </tr>
    </tbody>
  </table>
{% endblock content %}
```

E a view:

```python
# accounts/views.py
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomUserForm
from .models import User


def user_list(request):
    template_name = 'accounts/user_list.html'
    object_list = User.objects.all()
    context = {'object_list': object_list}
    return render(request, template_name, context)
```

O padrão de nomes é sempre o mesmo: `template_name`, `object_list` para listas, `object` para um item e `context`. Repare que o `User` é importado de `.models`: estamos usando o usuário **customizado** do projeto, e não o `User` padrão do Django.

No menu lateral (`core/templates/includes/aside.html`), ligue o item **Usuários** à rota nova (as urls de `accounts` não têm namespace):

```html
<!-- core/templates/includes/aside.html -->
<a href="{% url 'user_list' %}" class="text-base text-gray-900 font-normal rounded-lg hover:bg-gray-100 flex items-center p-2 group ">
  ...
  <span class="ml-3 flex-1 whitespace-nowrap">Usuários</span>
</a>
```

### Escondendo o admin

A lista mostra todos os usuários, inclusive o admin. Para mostrar todo mundo **menos** o admin, troque `all()` por `exclude()`:

```python
# accounts/views.py
def user_list(request):
    template_name = 'accounts/user_list.html'
    object_list = User.objects.exclude(email='admin@email.com')
    context = {'object_list': object_list}
    return render(request, template_name, context)
```

### O template completo

Agora troque o conteúdo de `user_list.html` pelo template no estilo do dashboard (Tailwind, template Windster). Ele usa três includes, um link para criar usuário, a tabela com os dados do usuário e do perfil, e os botões **Editar** e **Deletar** de cada linha:

```html
<!-- user_list.html -->
{% extends "base.html" %}

{% block content %}
  <!-- ... -->
        {% include "./includes/breadcrumb.html" %}
        <h1 class="text-xl sm:text-2xl font-semibold text-gray-900">Usuários</h1>
      <!-- ... -->
        {% include "./includes/search.html" %}
  <!-- ... (botões Adicionar e Exportar e o início da tabela) -->
              {% for object in object_list %}
                <tr class="hover:bg-gray-100">
                  <!-- ... (checkbox e foto) -->
                    <div class="text-sm font-normal text-gray-500">
                      <div class="text-base font-semibold text-gray-900">
                        <a href="{{ object.get_absolute_url }}" class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg">{{ object.get_full_name }}</a>
                      </div>
                      <div class="text-sm font-normal text-gray-500">{{ object.email }}</div>
                    </div>
                  </td>
                  <td class="p-4 whitespace-nowrap text-base font-medium text-gray-900">{{ object.profile.linkedin|default:"---" }}</td>
                  <td class="p-4 whitespace-nowrap text-base font-medium text-gray-900">{{ object.profile.birthday|date:"d/m/Y"|default:"---" }}</td>
                  <!-- ... (status: bolinha verde Ativo ou vermelha Inativo, conforme object.is_active) -->
                  <td class="p-4 whitespace-nowrap space-x-2">
                    <!-- ... (botão Editar) -->
                    <button type="button" data-modal-toggle="delete-user-modal" onclick="openModal()" class="text-white bg-red-600 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm inline-flex items-center px-3 py-2 text-center">
                      Deletar
                    </button>
                  </td>
                </tr>
              {% endfor %}
  <!-- ... (rodapé da tabela: veja o arquivo completo no GitHub) -->
  {% include "./includes/delete_modal.html" %}

{% endblock content %}

{% block js %}
  <script>
    const targetEl = document.getElementById('delete-user-modal')
    const modal = new Modal(targetEl)

    openModal = () => {
      modal.show()
    }
    closeModal = () => {
      modal.hide()
    }
  </script>
{% endblock js %}
```

Código completo: [backend/accounts/templates/accounts/user_list.html](https://github.com/rg3915/dicas-de-django/blob/b7a986cac36e0554c362a70e9c7279668e29565d/backend/accounts/templates/accounts/user_list.html)

Destaques:

* `{% include "./includes/..." %}`: o `./` faz o caminho ser relativo ao template atual, ou seja, `accounts/includes/...`.
* O nome é um link para `{{ object.get_absolute_url }}`, que vamos criar no model a seguir.
* `object.profile.linkedin` e `object.profile.birthday` vêm do `Profile` (OneToOne com o usuário); o filtro `default:"---"` mostra `---` quando o valor está vazio.
* O status usa `is_active`: bolinha verde "Ativo" ou vermelha "Inativo".
* A paginação ("Mostrando 1-20 de 2290") e a busca ainda são fixas; serão feitas em dicas futuras.

### O bloco js e o modal de exclusão

O template original abria o modal de exclusão com o atributo `data-modal-toggle` do Flowbite, mas no vídeo isso não funcionou de jeito nenhum. A solução foi abrir e fechar o modal com JavaScript, usando a classe `Modal` do Flowbite (que vem no `app.bundle.js` do template). Para isso o `base.html` ganha um bloco `js` no final do `body`, depois do script do template:

```html
<!-- core/templates/base.html -->
    <script async defer src="https://buttons.github.io/buttons.js"></script>
    <script src="{% static 'js/app.bundle.js' %}"></script>

    {% block js %}{% endblock js %}
  </body>
</html>
```

No `user_list.html`, o bloco `js` (visto acima) pega o elemento `delete-user-modal`, cria um `new Modal(targetEl)` e define `openModal()` e `closeModal()`. O botão **Deletar** chama `openModal()` e os botões de fechar do modal chamam `closeModal()`. A exclusão de fato fica para uma próxima aula.

## Os includes

### includes/breadcrumb.html

```html
<!-- breadcrumb.html -->
<nav class="flex mb-5" aria-label="Breadcrumb">
  <ol class="inline-flex items-center space-x-1 md:space-x-2">
    <li class="inline-flex items-center">
      <a href="#" class="text-gray-700 hover:text-gray-900 inline-flex items-center">
        <svg class="w-5 h-5 mr-2.5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path></svg>
        Home
      </a>
    </li>
    <li>
      <div class="flex items-center">
        <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>
        <a href="#" class="text-gray-700 hover:text-gray-900 ml-1 md:ml-2 text-sm font-medium">Usuários</a>
      </div>
    </li>
    <li>
      <div class="flex items-center">
        <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>
        <span class="text-gray-400 ml-1 md:ml-2 text-sm font-medium" aria-current="page">Lista</span>
      </div>
    </li>
  </ol>
</nav>
```

### includes/search.html

```html
<!-- search.html -->
<div class="hidden sm:flex items-center sm:divide-x sm:divide-gray-100 mb-3 sm:mb-0">
  <form class="lg:pr-3" action="#" method="GET">
    <label for="users-search" class="sr-only">Busca</label>
    <div class="mt-1 relative lg:w-64 xl:w-96">
      <input id="id_search" name="search" type="text" class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5" placeholder="Busca...">
    </div>
  </form>
  <div class="flex space-x-1 pl-0 sm:pl-2 mt-3 sm:mt-0">
    <a href="#" class="text-gray-500 hover:text-gray-900 cursor-pointer p-1 hover:bg-gray-100 rounded inline-flex justify-center">
      <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"></path></svg>
    </a>
    <a href="#" class="text-gray-500 hover:text-gray-900 cursor-pointer p-1 hover:bg-gray-100 rounded inline-flex justify-center">
      <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>
    </a>
    <a href="#" class="text-gray-500 hover:text-gray-900 cursor-pointer p-1 hover:bg-gray-100 rounded inline-flex justify-center">
      <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>
    </a>
    <a href="#" class="text-gray-500 hover:text-gray-900 cursor-pointer p-1 hover:bg-gray-100 rounded inline-flex justify-center">
      <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"></path></svg>
    </a>
  </div>
</div>
```

### includes/navigation_buttons.html

```html
<!-- navigation_buttons.html -->
<div class="flex items-center space-x-3">
  <a href="" class="flex-1 text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center">
    <svg class="-ml-1 mr-1 h-5 w-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
      <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"></path>
    </svg>
    Anterior
  </a>
  <a href="" class="flex-1 text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium inline-flex items-center justify-center rounded-lg text-sm px-3 py-2 text-center">
    Próximo
    <svg class="-mr-1 ml-1 h-5 w-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
      <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
    </svg>
  </a>
</div>
```

### includes/delete_modal.html

O `id="delete-user-modal"` é o elemento que o JavaScript do `user_list.html` procura.

```html
<!-- delete_modal.html -->
<!-- Delete User Modal -->
<div class="hidden overflow-x-hidden overflow-y-auto fixed top-4 left-0 right-0 md:inset-0 z-50 justify-center items-center h-modal sm:h-full" id="delete-user-modal">
  <div class="relative w-full max-w-md px-4 h-full md:h-auto">
    <!-- Modal content -->
    <div class="bg-white rounded-lg shadow relative">
      <!-- Modal header -->
      <div class="flex justify-end p-2">
        <button type="button" onclick="closeModal()" class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center" data-modal-toggle="delete-user-modal">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
        </button>
      </div>
      <!-- Modal body -->
      <div class="p-6 pt-0 text-center">
        <svg class="w-20 h-20 text-red-600 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <h3 class="text-xl font-normal text-gray-500 mt-5 mb-6">Tem certeza que você quer deletar este registro?</h3>
        <a href="#" class="text-white bg-red-600 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-base inline-flex items-center px-3 py-2.5 text-center mr-2">
          Sim, deletar
        </a>
        <a href="#" onclick="closeModal()" class="text-gray-900 bg-white hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 border border-gray-200 font-medium inline-flex items-center rounded-lg text-base px-3 py-2.5 text-center" data-modal-toggle="delete-user-modal">
          Não, cancelar
        </a>
      </div>
    </div>
  </div>
</div>
```

## Detalhes de um usuário

A view recebe o `pk` da url, busca o usuário com `get_object_or_404` (que devolve 404 se não existir) e manda para o template com o nome `object`:

```python
# accounts/views.py
def user_detail(request, pk):
    template_name = 'accounts/user_detail.html'
    instance = get_object_or_404(User, pk=pk)

    context = {'object': instance}
    return render(request, template_name, context)
```

No model `User`, crie o `get_absolute_url`, que devolve a url de detalhes do próprio objeto. É ele que a lista usa no link do nome:

```python
# accounts/models.py
from django.urls import reverse_lazy

...


class User(AbstractBaseUser, PermissionsMixin):
    ...

    def get_absolute_url(self):
        return reverse_lazy('user_detail', kwargs={'pk': self.pk})
```

O template de detalhes:

```html
<!-- user_detail.html -->
{% extends "base.html" %}

{% block content %}
  <div class="bg-white shadow rounded-lg p-4 sm:p-6 xl:p-8 ">
    <div class="mb-4">
      {% include "./includes/breadcrumb.html" %}
      <h1 class="text-xl sm:text-2xl font-semibold text-gray-900">Detalhes: {{ object.get_full_name }}</h1>
    </div>
    <div class="mb-5">
      <a href="javascript: history.go(-1)" class="text-base font-medium text-cyan-600 hover:bg-gray-100 rounded-lg">Voltar</a>
    </div>
    <!-- ... (foto, nome e e-mail) -->

    <!-- Nascimento -->
    <div class="block w-full overflow-x-auto">
      <div class="mt-2">
        <div class="text-sm font-normal text-gray-500">Nascimento</div>
        {% if object.profile.birthday %}
          <div class="text-base font-semibold text-gray-900">{{ object.profile.birthday|date:"l" }}, {{ object.profile.birthday }}</div>
        {% else %}
          <div class="text-base font-semibold text-gray-900">---</div>
        {% endif %}
      </div>
    </div>
    <!-- ... (LinkedIn, CPF e RG) -->

    <!-- Inscrito -->
    <div class="block w-full overflow-x-auto">
      <div class="mt-2">
        <div class="text-sm font-normal text-gray-500">Inscrito</div>
        <div class="text-base font-semibold text-gray-900">{{ object.date_joined|date:"d/m/Y H:i" }}</div>
      </div>
    </div>
    <!-- ... (Ativo e Admin, com bolinha verde ou vermelha: veja o arquivo completo no GitHub) -->

  </div>
{% endblock content %}
```

Código completo: [backend/accounts/templates/accounts/user_detail.html](https://github.com/rg3915/dicas-de-django/blob/b7a986cac36e0554c362a70e9c7279668e29565d/backend/accounts/templates/accounts/user_detail.html)

Alguns filtros de data:

* `{{ object.profile.birthday|date:"l" }}` mostra o dia da semana por extenso. Com o idioma em português, uma data de nascimento cadastrada no perfil pelo admin aparece como "sexta-feira, 28 de Dezembro de 1979".
* `{{ object.date_joined|date:"d/m/Y H:i" }}` mostra dia/mês/ano hora:minuto.
* Para os booleanos (`is_active` e `is_admin`) usamos `{% if %}`, com bolinha verde ou vermelha. Se você desmarcar "ativo" de um usuário no admin, ele aparece como **Inativo**.

## O formulário de adicionar

Primeiro o template, o básico que você vai usar em qualquer formulário:

* `<form action="." method="POST">`;
* `enctype="multipart/form-data"`, **obrigatório** quando o formulário faz upload de arquivos;
* `{% csrf_token %}`;
* um `for` em `form.visible_fields`, renderizando cada campo com o `render_field` do `django-widget-tweaks` (que permite passar as classes CSS do Tailwind direto no template);
* um botão do tipo `submit`.

```html
<!-- user_form.html -->
{% extends "base.html" %}
{% load widget_tweaks %}

{% block content %}
  <div class="mx-auto md:h-screen flex flex-col px-6 pt-8 pt:mt-0">
    <!-- Card -->
    <div class="bg-white shadow rounded-lg md:mt-0 w-full sm:max-w-screen-sm xl:p-0">
      <div class="p-6 sm:p-8 lg:p-16 space-y-8">
        <h2 class="text-2xl lg:text-3xl font-bold text-gray-900">
          {% if object.pk %}
            Editar
          {% else %}
            Adicionar
          {% endif %}
          Usuário
        </h2>
        <form class="mt-8 space-y-6" action="." method="POST" enctype="multipart/form-data">
          {% csrf_token %}
          {% for field in form.visible_fields %}
            <div>
              <label class="text-sm font-medium text-gray-900 block mb-2">{{ field.label }}</label>
              {% render_field field class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5" %}
            </div>
            <span class="text-sm font-medium text-gray-500">{{ field.help_text }}</span>
            {% for error in field.errors %}
              <span class="text-red-500">{{ error }}</span> <br>
            {% endfor %}
          {% endfor %}

          <div class="flex flex-col sm:flex-row">
            <button type="submit" class="text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium rounded-lg text-base px-5 py-3 w-full sm:w-auto text-center">Salvar</button>
            <a href="{% url 'user_list' %}" class="text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 focus:ring-4 focus:ring-cyan-200 font-medium rounded-lg text-sm px-5 py-3 mt-2 sm:mt-0 sm:ml-2 w-full sm:w-auto text-center">
              Cancelar
            </a>
          </div>
        </form>
      </div>
    </div>
  </div>
{% endblock content %}
```

O **Cancelar** volta para a lista de usuários. O título mostra **Editar** quando existe `object.pk` (edição) e **Adicionar** quando não existe.

A view usa o `CustomUserForm`, criado anteriormente em `accounts/forms.py`:

```python
# accounts/forms.py
from django import forms

from backend.accounts.models import User


class CustomUserForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nome',
        max_length=150,
    )
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
    )
    email = forms.EmailField(
        label='E-mail',
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )
```

```python
# accounts/views.py
def user_create(request):
    template_name = 'accounts/user_form.html'
    form = CustomUserForm(request.POST or None)

    context = {'form': form}
    return render(request, template_name, context)
```

`request.POST or None`: num GET o formulário vem vazio; num POST ele recebe os dados enviados. Por enquanto a view só exibe o formulário; salvar fica para a próxima aula.

Repare que o padrão é sempre o mesmo nome de template, `user_form.html`, tanto para adicionar quanto para editar. Se a view apontar para outro nome (no vídeo, um `user_create.html` digitado por engano), o Django dá `TemplateDoesNotExist`.

## O formulário de editar

A edição precisa saber **qual** usuário editar, por isso a rota tem o `pk`. A view é uma mistura da `user_detail` com a `user_create`:

```python
# accounts/views.py
def user_update(request, pk):
    template_name = 'accounts/user_form.html'
    instance = get_object_or_404(User, pk=pk)
    form = CustomUserForm(request.POST or None, instance=instance)

    context = {
        'object': instance,
        'form': form,
    }
    return render(request, template_name, context)
```

* `instance=instance` faz o formulário vir preenchido com os dados do usuário.
* `'object': instance` no contexto faz o título do template mostrar **Editar**.

O botão **Editar** da lista já aponta para `{% url 'user_update' object.pk %}`.

## Testando

Cadastre mais um usuário pelo admin (no vídeo, "Donald") e volte para **Usuários**: ele aparece na lista. Clicando no nome, vemos os detalhes; em **Editar**, o formulário vem preenchido; em **Adicionar**, o formulário vem vazio; em **Deletar**, o modal abre e fecha.

## Resumo do padrão

| Ação | url | name | view | template |
|---|---|---|---|---|
| Lista | `users/` | `user_list` | `user_list` | `accounts/user_list.html` |
| Adicionar | `users/create/` | `user_create` | `user_create` | `accounts/user_form.html` |
| Detalhes | `users/<int:pk>/` | `user_detail` | `user_detail` | `accounts/user_detail.html` |
| Editar | `users/<int:pk>/update/` | `user_update` | `user_update` | `accounts/user_form.html` |

Nas próximas dicas, salvar o formulário e validar os dados ([Dica 22](088-22-validacao.md)) e repetir o mesmo padrão para os produtos ([Dica 23](089-23-crud-produtos.md)).

Observação: o serviço de imagens `via.placeholder.com`, usado nos templates para a foto do usuário, não funciona mais; troque por outra imagem se for rodar hoje.
