# Dica 15 - Login com e-mail no Django

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10 e Tailwind CSS 3.2.4 (CSS compilado do template Windster).
{: .versoes }

<a href="https://youtu.be/5F4uQeTmOLg">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`), por causa do GitBook. Aqui elas já estão escritas do jeito certo, sem a barra.

![](../.gitbook/assets/tags.png)

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django) (branch `aula15`)

Na [Dica 14 - Django Custom User com e-mail](074-14-django-custom-user-email.md) trocamos o usuário do projeto por um usuário que se identifica pelo **e-mail**. Agora vamos fazer a tela de **login** com e-mail e senha, usando a `LoginView` que já vem pronta no Django, e proteger o dashboard da [Dica 13](073-13-dashboard.md) para que só usuários autenticados entrem nele.

Não precisa escrever nenhuma view de login: a `LoginView` (de `django.contrib.auth.views`) já mostra o formulário, autentica e redireciona. Como o `USERNAME_FIELD` do nosso `User` é o `email`, o "username" que ela recebe é o e-mail.

## Pré-requisitos

* O projeto da Dica 14, com a app `backend.accounts`, o `AUTH_USER_MODEL = 'accounts.User'` e um superusuário criado com `createsuperuser`.
* Os arquivos estáticos do Windster (`css/app.css` e `js/app.bundle.js`) da Dica 13.

```bash
git checkout -b aula15
```

## Pasta de templates do login

A `LoginView` procura, por padrão, o template `registration/login.html`. Vamos criá-lo dentro da app `accounts`:

```bash
mkdir -p backend/accounts/templates/registration
touch backend/accounts/templates/registration/login.html
```

## Link de login na página inicial

No menu do `index.html`, o link **Login** passa a apontar para a URL de nome `login`:

```html
<!-- backend/core/templates/index.html -->
<a href="{% url 'login' %}" class="text-gray-600 hover:text-purple-600 p-4 px-3 sm:px-4">Login</a>
```

## Redirecionamentos no settings

No fim do `settings.py`:

```python
# backend/settings.py
LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'core:index'
```

* `LOGIN_REDIRECT_URL`: para onde o usuário vai depois de fazer login (quando não há um `next` na requisição). Aqui, o dashboard.
* `LOGOUT_REDIRECT_URL`: para onde ele vai depois do logout (usado na [Dica 16](076-16-logout.md)). Aqui, a página inicial.

Os dois aceitam o nome da URL (com namespace), não só o caminho.

## URLs da app accounts

No `urls.py` principal, inclua as URLs da app `accounts` com o prefixo `accounts/`:

```python
# backend/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('backend.core.urls', namespace='core')),  # noqa E501
    path('accounts/', include('backend.accounts.urls')),  # noqa E501
    path('crm/', include('backend.crm.urls', namespace='crm')),  # noqa E501
    path('admin/', admin.site.urls),  # noqa E501
]
```

Repare em dois detalhes:

* O prefixo é `accounts/` porque o `LOGIN_URL` padrão do Django é `/accounts/login/`. É para essa URL que o `@login_required` manda quem não está logado.
* Aqui **não** usamos `namespace`, então as URLs ficam com os nomes "puros": `{% url 'login' %}`, e não `accounts:login`. É o padrão do Django para as URLs de autenticação, e algumas views dele (como as de redefinição de senha, que aparecem nas próximas dicas) procuram as URLs exatamente por esses nomes.

Crie o `accounts/urls.py`. A rota `login/` usa direto a `LoginView` do Django; não precisa mexer no `accounts/views.py`:

```python
# backend/accounts/urls.py
from django.contrib.auth.views import LoginView
from django.urls import path

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # noqa E501
]
```

## O template base do login

A tela de login não tem menu lateral nem barra superior, então ela não herda do `base.html` do dashboard. Criamos um `base_login.html`, que é o `base.html` da Dica 13 sem os *includes*: carrega a fonte Inter, o `css/app.css` e o `js/app.bundle.js`, e tem só o `{% block content %}` no `<body>`.

```html
<!-- backend/core/templates/base_login.html -->
{% load static %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Get started with a free and open source Tailwind CSS admin dashboard featuring a sidebar layout, advanced charts, and hundreds of components based on Flowbite">
    <meta name="author" content="Themesberg">
    <meta name="generator" content="Hugo 0.107.0">

    <title>Dicas de Django | Login</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{% static 'css/app.css' %}">
    <link rel="apple-touch-icon" sizes="180x180" href="https://demo.themesberg.com/windster/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="https://demo.themesberg.com/windster/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="https://demo.themesberg.com/windster/favicon-16x16.png">
    <link rel="icon" type="image/png" href="https://demo.themesberg.com/windster/favicon.ico">
    <link rel="mask-icon" href="https://demo.themesberg.com/windster/safari-pinned-tab.svg" color="#5bbad5">
    <meta name="msapplication-TileColor" content="#ffffff">
    <meta name="theme-color" content="#ffffff">
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@">
    <meta name="twitter:creator" content="@">
    <meta name="twitter:title" content="Tailwind CSS Login - Windster">
    <meta name="twitter:description" content="Get started with a free and open source Tailwind CSS admin dashboard featuring a sidebar layout, advanced charts, and hundreds of components based on Flowbite">
    <meta name="twitter:image" content="https://demo.themesberg.com/windster/">

    <!-- Facebook -->
    <meta property="og:url" content="https://demo.themesberg.com/windster/">
    <meta property="og:title" content="Tailwind CSS Login - Windster">
    <meta property="og:description" content="Get started with a free and open source Tailwind CSS admin dashboard featuring a sidebar layout, advanced charts, and hundreds of components based on Flowbite">
    <meta property="og:type" content="website">
    <meta property="og:image" content="https://demo.themesberg.com/docs/images/og-image.jpg">
    <meta property="og:image:type" content="image/png">

  </head>
  <body class="bg-gray-50">

    {% block content %}{% endblock content %}

    <script async defer src="https://buttons.github.io/buttons.js"></script>
    <script src="{% static 'js/app.bundle.js' %}"></script>
  </body>
</html>
```

## O template de login

O `login.html` é a página de login do Windster adaptada:

```html
<!-- backend/accounts/templates/registration/login.html -->
{% extends "base_login.html" %}

{% block content %}
  <main class="bg-gray-50">
    <div class="mx-auto md:h-screen flex flex-col justify-center items-center px-6 pt-8 pt:mt-0">
      <a href="https://demo.themesberg.com/windster/" class="text-2xl font-semibold flex justify-center items-center mb-8 lg:mb-10">
        <img src="https://demo.themesberg.com/windster/images/logo.svg" class="h-10 mr-4" alt="Windster Logo">
        <span class="self-center text-2xl font-bold whitespace-nowrap">Dicas de Django</span>
      </a>
      <!-- Card -->
      <div class="bg-white shadow rounded-lg md:mt-0 w-full sm:max-w-screen-sm xl:p-0">
        <div class="p-6 sm:p-8 lg:p-16 space-y-8">
          <h2 class="text-2xl lg:text-3xl font-bold text-gray-900">
            Login
          </h2>
          <form class="mt-8 space-y-6" action="." method="POST">
            {% csrf_token %}
            <div>
              <label for="id_email" class="text-sm font-medium text-gray-900 block mb-2">E-mail</label>
              <input
                id="id_email"
                type="email"
                name="username"
                class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5"
                placeholder="nome@example.com"
                required
                autofocus
              >
            </div>
            <div>
              <label for="id_password" class="text-sm font-medium text-gray-900 block mb-2">Senha</label>
              <input
                id="id_password"
                type="password"
                name="password"
                placeholder="••••••••"
                class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5"
                required
              >
            </div>
            <div class="flex items-start">
              <!-- <div class="flex items-center h-5">
                <input id="remember" aria-describedby="remember" name="remember" type="checkbox" class="bg-gray-50 border-gray-300 focus:ring-3 focus:ring-cyan-200 h-4 w-4 rounded">
              </div>
              <div class="text-sm ml-3">
                <label for="remember" class="font-medium text-gray-900">Remember me</label>
              </div> -->
              <a href="" class="text-sm text-teal-500 hover:underline ml-auto">Esqueceu a senha?</a>
            </div>
            <button type="submit" class="text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium rounded-lg text-base px-5 py-3 w-full sm:w-auto text-center">Login</button>
            <div class="text-sm font-medium text-gray-500">
              Não cadastrado? <a href="." class="text-teal-500 hover:underline">Criar conta</a>
            </div>
          </form>
        </div>
      </div>
    </div>

  </main>
{% endblock content %}
```

O que faz o formulário funcionar:

* `method="POST"` e o `{% csrf_token %}`.
* `action="."` envia o formulário para a própria URL, `/accounts/login/`, onde está a `LoginView`.
* O campo de e-mail tem `type="email"`, mas `name="username"`. O formulário da `LoginView` (o `AuthenticationForm`) tem os campos `username` e `password`; como o `USERNAME_FIELD` do nosso usuário é o `email`, o valor digitado em `username` é comparado com o e-mail.
* O campo de senha tem `name="password"`.
* Os links **Esqueceu a senha?** e **Criar conta** ainda estão vazios; eles serão ligados nas dicas de [cadastro](077-17-cadastro.md) e de [esqueci a senha](078-18-esqueci-senha.md).

## Protegendo o dashboard

Por fim, em `core/views.py`, o decorator `@login_required` protege o dashboard:

```python
# backend/core/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def index(request):
    template_name = 'index.html'
    return render(request, template_name)


@login_required
def dashboard(request):
    template_name = 'dashboard.html'
    return render(request, template_name)
```

Se o usuário não estiver autenticado, o `@login_required` redireciona para `/accounts/login/?next=/dashboard/`.

## Testando

```bash
python manage.py runserver
```

1. Acesse [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/) sem estar logado: você é redirecionado para a tela de login. (No vídeo, a primeira tentativa deu `TemplateDoesNotExist` porque o `login.html` ainda não tinha sido salvo.)
2. Tente entrar com um e-mail que não está cadastrado: o login não acontece e a mesma tela volta.
3. Entre com o e-mail e a senha do superusuário (no vídeo, `admin@email.com`): você vai para o dashboard.
4. Para sair, por enquanto, use o **Encerrar sessão** do admin (o logout do site fica para a próxima dica). Depois disso, ao acessar `/dashboard/` ou clicar em **Login** na página inicial, a tela de login aparece de novo.

Observação: este template não mostra as mensagens de erro do formulário. Se o e-mail ou a senha estiverem errados, a página só é exibida de novo. Para mostrar o erro, dá para colocar `{{ form.non_field_errors }}` dentro do `<form>`.

Na [Dica 16 - Logout](076-16-logout.md) vamos colocar o nome do usuário e o botão **Sair** na barra superior do dashboard.
