# Dica 13 - Dashboard com Django e Tailwind CSS

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10 e Tailwind CSS 3.2.4 (CSS já compilado do template Windster).
{: .versoes }

<a href="https://youtu.be/mTpJx4_rTJQ">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`), por causa do GitBook. Aqui elas já estão escritas do jeito certo, sem a barra.

![](../.gitbook/assets/tags.png)

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django) (branch `aula13`)

Vamos criar o **dashboard** (a área interna) do *Projeto Dicas de Django*. Em vez de desenhar tudo do zero, usamos o **Windster**, um template de dashboard gratuito e de código aberto feito com Tailwind CSS pela Themesberg ([demo](https://demo.themesberg.com/windster/) e [código no GitHub](https://github.com/themesberg/tailwind-dashboard-windster)). Ele tem menu lateral, barra superior, gráfico, tabelas e cards, e nós vamos quebrá-lo em templates do Django: um `base.html` com a estrutura, três *includes* (barra superior, menu lateral e rodapé) e a página `dashboard.html`.

Esta dica continua a [Dica 12 - Fale conosco com formulário para enviar mensagem](072-012-fale-co-nosco-form-email.md). Até aqui o projeto só tinha a página inicial (`index.html`, a landpage da [Dica 11](071-11-landpage.md)), que é um template independente e não herda do `base.html`.

## Pré-requisitos

* O projeto das dicas anteriores, com a app `core` em `backend/core`.
* Os dois arquivos estáticos do Windster já compilados (veja a seção *Arquivos estáticos*, mais abaixo).

No vídeo, o Regis cria a branch da aula:

```bash
git checkout -b aula13
```

## A rota do dashboard

No `index.html`, o link **Home** do menu passa a apontar para o dashboard:

```html
<!-- backend/core/templates/index.html -->
<a href="{% url 'core:dashboard' %}" class="text-gray-600 hover:text-purple-600 p-4 px-3 sm:px-4">Home</a>
```

Em `core/urls.py`, copie a linha da `index` e crie a rota `dashboard/`:

```python
# backend/core/urls.py
from django.urls import path

from backend.core import views as v

app_name = 'core'


urlpatterns = [
    path('', v.index, name='index'),  # noqa E501
    path('dashboard/', v.dashboard, name='dashboard'),  # noqa E501
]
```

E em `core/views.py`, a view `dashboard` é uma cópia da `index` que renderiza outro template:

```python
# backend/core/views.py
from django.shortcuts import render


def index(request):
    template_name = 'index.html'
    return render(request, template_name)


def dashboard(request):
    template_name = 'dashboard.html'
    return render(request, template_name)
```

## Arquivos estáticos

O Windster usa classes do Tailwind CSS 3 e um JavaScript próprio (que inclui o [ApexCharts](https://apexcharts.com/), usado no gráfico de vendas, e o abre e fecha do menu no celular). No vídeo, o Regis compilou o projeto do Windster e copiou os dois arquivos gerados para dentro da app `core`:

```
backend/core/static/
├── css
│   └── app.css          # Tailwind CSS 3.2.4 compilado, com as classes do Windster
└── js
    └── app.bundle.js    # JavaScript do Windster (com o ApexCharts)
```

Não precisa compilar nada: baixe os dois arquivos prontos do repositório (branch `aula13`) e salve nesses caminhos:

* [backend/core/static/css/app.css](https://github.com/rg3915/dicas-de-django/blob/aula13/backend/core/static/css/app.css)
* [backend/core/static/js/app.bundle.js](https://github.com/rg3915/dicas-de-django/blob/aula13/backend/core/static/js/app.bundle.js)

Repare que o dashboard **não** usa o Tailwind pela CDN, como a landpage: ele usa o `app.css` compilado, que só tem as classes usadas pelo Windster.

## O template base

O `base.html` foi trocado pela estrutura do Windster. Os pontos importantes:

* carrega a fonte Inter do Google Fonts, o `css/app.css` e, no fim do `<body>`, o `js/app.bundle.js`;
* inclui a barra superior (`includes/nav.html`) e, dentro de um `div` flexível, o menu lateral (`includes/aside.html`);
* o `div#sidebarBackdrop` é o fundo escuro que aparece atrás do menu quando ele é aberto no celular;
* o `div#main-content` (com `lg:ml-64`, a largura do menu lateral) recebe o `{% block content %}` e o rodapé (`includes/footer.html`).

As `<meta>` de Twitter e Facebook vieram junto com o template original e não fazem diferença para o funcionamento.

```html
<!-- backend/core/templates/base.html -->
{% load static %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- ... -->
    <link rel="stylesheet" href="{% static 'css/app.css' %}">
    <!-- ... (ícones e metas de Twitter e Facebook: veja o arquivo completo no GitHub) -->
  </head>
  <body class="bg-gray-50">

    {% include "includes/nav.html" %}
    <div class="flex overflow-hidden bg-white pt-16">

      {% include "includes/aside.html" %}

      <div class="bg-gray-900 opacity-50 hidden fixed inset-0 z-10" id="sidebarBackdrop"></div>

      <div id="main-content" class="h-full w-full bg-gray-50 relative overflow-y-auto lg:ml-64">
        {% block content %}{% endblock content %}
        {% include "includes/footer.html" %}

      </div>

    </div>

    <script async defer src="https://buttons.github.io/buttons.js"></script>
    <script src="{% static 'js/app.bundle.js' %}"></script>
  </body>
</html>
```

Código completo: [backend/core/templates/base.html](https://github.com/rg3915/dicas-de-django/blob/36efcf1749c49ef041ac1c4bf499ef3ef071ed08/backend/core/templates/base.html)

## O menu lateral

Crie o arquivo do menu lateral:

```bash
touch backend/core/templates/includes/aside.html
```

Ele tem um campo de busca (visível só no celular), os itens do menu e links para a documentação do Flowbite. Por enquanto, só o item **Dashboard** aponta para uma URL do projeto (`core:dashboard`); **Usuários**, **Produtos**, **Login** e **Cadastre-se** ficam com `href=""` e serão ligados nas próximas dicas.

```html
<!-- backend/core/templates/includes/aside.html -->
<aside id="sidebar" class="fixed hidden z-20 h-full top-0 left-0 pt-16 flex lg:flex flex-shrink-0 flex-col w-64 transition-width duration-75" aria-label="Sidebar">
  <div class="relative flex-1 flex flex-col min-h-0 border-r border-gray-200 bg-white pt-0">
    <div class="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
      <div class="flex-1 px-3 bg-white divide-y space-y-1">
        <ul class="space-y-2 pb-2">
          <!-- ... -->
          <li>
            <a href="{% url 'core:dashboard' %}" class="text-base text-gray-900 font-normal rounded-lg flex items-center p-2 hover:bg-gray-100 group">
              <svg class="w-6 h-6 text-gray-500 group-hover:text-gray-900 transition duration-75" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z"></path><path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z"></path></svg>
              <span class="ml-3">Dashboard</span>
            </a>
          </li>
          <li>
            <a href="" class="text-base text-gray-900 font-normal rounded-lg hover:bg-gray-100 flex items-center p-2 group ">
              <svg class="w-6 h-6 text-gray-500 flex-shrink-0 group-hover:text-gray-900 transition duration-75" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path></svg>
              <span class="ml-3 flex-1 whitespace-nowrap">Usuários</span>
            </a>
          </li>
          <!-- ... (veja o arquivo completo no GitHub) -->
        </ul>
        <!-- ... -->
      </div>
    </div>
  </div>
</aside>
```

Código completo: [backend/core/templates/includes/aside.html](https://github.com/rg3915/dicas-de-django/blob/36efcf1749c49ef041ac1c4bf499ef3ef071ed08/backend/core/templates/includes/aside.html)

## A barra superior

Crie também o `nav.html`:

```bash
touch backend/core/templates/includes/nav.html
```

É a barra fixa no topo, com o botão que abre e fecha o menu lateral no celular (`#toggleSidebarMobile`, controlado pelo `app.bundle.js`), o nome **Dicas de Django**, o campo de busca e o botão de estrela do GitHub do Windster (o script `buttons.github.io/buttons.js` do `base.html` desenha esse botão).

```html
<!-- backend/core/templates/includes/nav.html -->
<nav class="bg-white border-b border-gray-200 fixed z-30 w-full">
  <div class="px-3 py-3 lg:px-5 lg:pl-3">
    <div class="flex items-center justify-between">
      <div class="flex items-center justify-start">
        <button id="toggleSidebarMobile" aria-expanded="true" aria-controls="sidebar" class="lg:hidden mr-2 text-gray-600 hover:text-gray-900 cursor-pointer p-2 hover:bg-gray-100 focus:bg-gray-100 focus:ring-2 focus:ring-gray-100 rounded">
          <svg id="toggleSidebarMobileHamburger" class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h6a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path></svg>
          <svg id="toggleSidebarMobileClose" class="w-6 h-6 hidden" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
        </button>
        <a href="https://demo.themesberg.com/windster/" class="text-xl font-bold flex items-center lg:ml-2.5">
          <img src="https://demo.themesberg.com/windster/images/logo.svg" class="h-6 mr-2" alt="Windster Logo">
          <span class="self-center whitespace-nowrap">Dicas de Django</span>
        </a>
        <form action="#" method="GET" class="hidden lg:block lg:pl-32">
          <label for="topbar-search" class="sr-only">Search</label>
          <div class="mt-1 relative lg:w-64">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"></path></svg>
            </div>
            <input type="text" name="email" id="topbar-search" class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full pl-10 p-2.5" placeholder="Search">
          </div>
        </form>
      </div>
      <div class="flex items-center">

        <button id="toggleSidebarMobileSearch" type="button" class="lg:hidden text-gray-500 hover:text-gray-900 hover:bg-gray-100 p-2 rounded-lg">
          <span class="sr-only">Search</span>

          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"></path></svg>
        </button>
        <div class="hidden lg:flex items-center">
          <span class="text-base font-normal text-gray-500 mr-5">Open source ❤️</span>
          <div class="-mb-1">
            <a class="github-button" href="https://github.com/themesberg/windster-tailwind-css-dashboard" data-color-scheme="no-preference: dark; light: light; dark: light;" data-icon="octicon-star" data-size="large" data-show-count="true" aria-label="Star themesberg/windster-tailwind-css-dashboard on GitHub">Star</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</nav>
```

## O rodapé

O `includes/footer.html` já existia (era o rodapé do `base.html` antigo). Apague o conteúdo dele e coloque o rodapé do Windster, com os links institucionais, os ícones de redes sociais e o crédito:

```html
<!-- backend/core/templates/includes/footer.html -->
<footer class="bg-white md:flex md:items-center md:justify-between shadow rounded-lg p-4 md:p-6 xl:p-8 my-6 mx-4">
  <ul class="flex items-center flex-wrap mb-6 md:mb-0">
    <li><a href="#" class="text-sm font-normal text-gray-500 hover:underline mr-4 md:mr-6">Terms and conditions</a></li>
    <li><a href="#" class="text-sm font-normal text-gray-500 hover:underline mr-4 md:mr-6">Privacy Policy</a></li>
    <li><a href="#" class="text-sm font-normal text-gray-500 hover:underline mr-4 md:mr-6">Licensing</a></li>
    <li><a href="#" class="text-sm font-normal text-gray-500 hover:underline mr-4 md:mr-6">Cookie Policy</a></li>
    <li><a href="{% url 'core:index' %}#contato" class="text-sm font-normal text-gray-500 hover:underline">Contact</a></li>
  </ul>
  <div class="flex sm:justify-center space-x-6">
    <a href="#" class="text-gray-500 hover:text-gray-900">
      <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path fill-rule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" clip-rule="evenodd" />
      </svg>
    </a>
    <a href="#" class="text-gray-500 hover:text-gray-900">
      <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path fill-rule="evenodd" d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.45 2.525c.636-.247 1.363-.416 2.427-.465C8.901 2.013 9.256 2 11.685 2h.63zm-.081 1.802h-.468c-2.456 0-2.784.011-3.807.058-.975.045-1.504.207-1.857.344-.467.182-.8.398-1.15.748-.35.35-.566.683-.748 1.15-.137.353-.3.882-.344 1.857-.047 1.023-.058 1.351-.058 3.807v.468c0 2.456.011 2.784.058 3.807.045.975.207 1.504.344 1.857.182.466.399.8.748 1.15.35.35.683.566 1.15.748.353.137.882.3 1.857.344 1.054.048 1.37.058 4.041.058h.08c2.597 0 2.917-.01 3.96-.058.976-.045 1.505-.207 1.858-.344.466-.182.8-.398 1.15-.748.35-.35.566-.683.748-1.15.137-.353.3-.882.344-1.857.048-1.055.058-1.37.058-4.041v-.08c0-2.597-.01-2.917-.058-3.96-.045-.976-.207-1.505-.344-1.858a3.097 3.097 0 00-.748-1.15 3.098 3.098 0 00-1.15-.748c-.353-.137-.882-.3-1.857-.344-1.023-.047-1.351-.058-3.807-.058zM12 6.865a5.135 5.135 0 110 10.27 5.135 5.135 0 010-10.27zm0 1.802a3.333 3.333 0 100 6.666 3.333 3.333 0 000-6.666zm5.338-3.205a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z" clip-rule="evenodd" />
      </svg>
    </a>
    <a href="#" class="text-gray-500 hover:text-gray-900">
      <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
      </svg>
    </a>
    <a href="https://github.com/rg3915/dicas-de-django" target="_blank" class="text-gray-500 hover:text-gray-900">
      <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" />
      </svg>
    </a>
    <a href="#" class="text-gray-500 hover:text-gray-900">
      <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path fill-rule="evenodd" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10c5.51 0 10-4.48 10-10S17.51 2 12 2zm6.605 4.61a8.502 8.502 0 011.93 5.314c-.281-.054-3.101-.629-5.943-.271-.065-.141-.12-.293-.184-.445a25.416 25.416 0 00-.564-1.236c3.145-1.28 4.577-3.124 4.761-3.362zM12 3.475c2.17 0 4.154.813 5.662 2.148-.152.216-1.443 1.941-4.48 3.08-1.399-2.57-2.95-4.675-3.189-5A8.687 8.687 0 0112 3.475zm-3.633.803a53.896 53.896 0 013.167 4.935c-3.992 1.063-7.517 1.04-7.896 1.04a8.581 8.581 0 014.729-5.975zM3.453 12.01v-.26c.37.01 4.512.065 8.775-1.215.25.477.477.965.694 1.453-.109.033-.228.065-.336.098-4.404 1.42-6.747 5.303-6.942 5.629a8.522 8.522 0 01-2.19-5.705zM12 20.547a8.482 8.482 0 01-5.239-1.8c.152-.315 1.888-3.656 6.703-5.337.022-.01.033-.01.054-.022a35.318 35.318 0 011.823 6.475 8.4 8.4 0 01-3.341.684zm4.761-1.465c-.086-.52-.542-3.015-1.659-6.084 2.679-.423 5.022.271 5.314.369a8.468 8.468 0 01-3.655 5.715z" clip-rule="evenodd" />
      </svg>
    </a>
  </div>
</footer>
<p class="text-center text-sm text-gray-500 my-10">
  Dicas de Django &copy; 2023 <a href="https://themesberg.com" class="hover:underline" target="_blank">Themesberg</a>. Regis do Python.
</p>
```

## A página do dashboard

Por fim, crie o `dashboard.html`. Ele herda do `base.html` e preenche o `{% block content %}` com o conteúdo de exemplo do Windster: o card de vendas da semana com o gráfico (o `div#main-chart`, desenhado pelo ApexCharts do `app.bundle.js`), a tabela de últimas transações, três cards de indicadores, a lista de últimos clientes e a tabela de origem dos acessos. Os dados são fixos no HTML; a ideia aqui é ter o layout pronto.

```html
<!-- backend/core/templates/dashboard.html -->
{% extends "base.html" %}

{% block content %}
  <main>

    <div class="pt-6 px-4">
      <div class="w-full grid grid-cols-1 xl:grid-cols-2 2xl:grid-cols-3 gap-4">
        <div class="bg-white shadow rounded-lg p-4 sm:p-6 xl:p-8  2xl:col-span-2">

          <div class="flex items-center justify-between mb-4">
            <div class="flex-shrink-0">
              <span class="text-2xl sm:text-3xl leading-none font-bold text-gray-900">$45,385</span>
              <h3 class="text-base font-normal text-gray-500">Sales this week</h3>
            </div>
            <div class="flex items-center justify-end flex-1 text-green-500 text-base font-bold">
              12.5%
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd"
                  d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z"
                  clip-rule="evenodd"></path>
              </svg>
            </div>
          </div>
          <div id="main-chart"></div>

        </div>
        <!-- ... (tabela de transações, cards de indicadores, últimos clientes e origem dos acessos: veja o arquivo completo no GitHub) -->
      </div>
    </div>
  </main>
{% endblock content %}
```

Código completo: [backend/core/templates/dashboard.html](https://github.com/rg3915/dicas-de-django/blob/36efcf1749c49ef041ac1c4bf499ef3ef071ed08/backend/core/templates/dashboard.html)

## Rodando

```bash
python manage.py runserver
```

Abra [http://localhost:8000](http://localhost:8000) e clique em **Home** no menu da landpage: você vai para [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/), com o menu lateral, a barra superior, o gráfico de vendas, as tabelas e o rodapé.

Se aparecer `TemplateDoesNotExist` para algum dos *includes* (no vídeo aconteceu com o `nav.html`), confira se o arquivo foi salvo em `backend/core/templates/includes/`.

O visual do dashboard (verde-água, do Windster) ficou diferente do da landpage (roxo). Fica como exercício trocar as cores para deixar os dois parecidos.

## Links

[https://demo.themesberg.com/windster/](https://demo.themesberg.com/windster/)

[https://github.com/themesberg/tailwind-dashboard-windster](https://github.com/themesberg/tailwind-dashboard-windster)
