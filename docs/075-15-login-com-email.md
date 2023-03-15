# Dica 15 - Login com e-mail no Django

<a href="https://youtu.be/5F4uQeTmOLg">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** remova a `\` no meio das tags.

![](../.gitbook/assets/tags.png)


```
mkdir -p backend/accounts/templates/registration
touch backend/accounts/templates/registration/login.html
```

Edite `index.html`

```html
<a href="{\% url 'login' %}" class="text-gray-600 hover:text-purple-600 p-4 px-3 sm:px-4">Login</a>
```

Edite `settings.py`

```python
# settings.py

LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'core:index'
```

Edite `backend/urls.py`

```python
# backend/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('backend.core.urls', namespace='core')),  # noqa E501
    path('accounts/', include('backend.accounts.urls')),  # noqa E501
    ...
]
```

Edite `accounts/urls.py`

```python
# accounts/urls.py
from django.contrib.auth.views import LoginView
from django.urls import path


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # noqa E501
]

```

Edite `backend/core/templates/base_login.html`

```html
<!-- base_login.html -->
{\% load static %}
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
    <link rel="stylesheet" href="{\% static 'css/app.css' %}">
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

    {\% block content %}{\% endblock content %}

    <script async defer src="https://buttons.github.io/buttons.js"></script>
    <script src="{\% static 'js/app.bundle.js' %}"></script>
  </body>
</html>
```

Edite `backend/accounts/templates/registration/login.html`

```html
<!-- login.html -->
<!-- login.html -->
{\% extends "base_login.html" %}

{\% block content %}
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
            {\% csrf_token %}
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
{\% endblock content %}
```

Edite core/views.py

```python
# core/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    template_name = 'dashboard.html'
    return render(request, template_name)
```
