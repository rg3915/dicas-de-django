# Dica 11 - Criando Landpage de produtos

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10 e Tailwind CSS 3 (via CDN, o Play CDN).
{: .versoes }

<a href="https://youtu.be/zpC5qH8-iT8">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`). Se copiar código de lá, remova a `\`.

![](../.gitbook/assets/tags.png)

Hoje vamos criar a landpage do projeto Dicas de Django: uma página com uma lista de produtos (roupas masculinas e femininas) e um formulário de contato, feita com Tailwind CSS.

Não vamos desenhar a página do zero. Vamos usar como base um template estático pronto, o [tailwind-eshop-static-html](https://github.com/itzpradip/tailwind-eshop-static-html), cujo autor tem um vídeo no YouTube explicando passo a passo como montar a página: [https://youtu.be/iNDvh7O2WZM](https://youtu.be/iNDvh7O2WZM). Vamos pegar o `index.html` dele e adaptar para o Django.

Código da aula: [https://github.com/rg3915/dicas-de-django/tree/aula11](https://github.com/rg3915/dicas-de-django/tree/aula11)

## Pré-requisitos

* O projeto das dicas anteriores (a partir da [Dica 06](066-06-projeto-django.md)), com a app `core`, a view `index` e o `runserver` funcionando.

No vídeo, a issue da aula é criada com o script da [Dica 01](061-01-criando-issues-com-api-github.md), já com o link do template no corpo, e em seguida vem a branch:

```bash
python cli/create_issue.py \
--title='Criando Landpage de produtos' \
--body='g ch -b aula11
https://github.com/itzpradip/tailwind-eshop-static-html' \
--labels='frontend'

git checkout -b aula11
```

## O que muda em relação ao template original

Em `backend/core/templates/index.html`, apague todo o conteúdo e cole o `index.html` do template. Depois fiz alguns ajustes:

* **Tailwind via CDN:** o template original compila o Tailwind com `npm` (`tailwind.config.js`, `css/tailwind.css`). Aqui continuamos com o `<script src="https://cdn.tailwindcss.com"></script>`, como no `base.html`.
* **Textos em português e marca:** o logo virou "Dicas de Django", o menu ficou Home, Produtos, Contato, Login e "Carrinho (0)", o título do topo é "Grandes Marcas", as seções são "Coleção Masculina" e "Coleção Feminina", e o rodapé diz "Dicas de Django © 2023" e "by Regis do Python".
* **Fale Conosco:** no lugar da seção de newsletter do original, entrou um formulário "Fale Conosco" (nome, e-mail, título e mensagem), com outras cores e outra foto (`woman.png`). Por enquanto ele não envia nada; vamos usar esse formulário numa dica futura.
* **Arquivos estáticos do Django:** todas as imagens passam a usar a tag `static`.
* **A classe `form-control`:** as classes repetidas dos campos do formulário foram resumidas numa classe só, com `@apply`.

Repare que este `index.html` é uma página completa (tem `<!DOCTYPE html>`, `<head>` e `<body>`): ele **não** estende o `base.html`.

## As imagens

As imagens vêm da pasta `images` do template. Copie-as para a pasta de estáticos da app, com o nome `img`:

```
backend/core/static/img/
├── hero-img.svg
├── products
│   ├── men
│   │   ├── product1.jpg
│   │   ├── product2.jpg
│   │   ├── product3.jpg
│   │   └── product4.jpg
│   └── women
│       ├── product1.jpg
│       ├── product2.jpg
│       ├── product3.jpg
│       └── product4.jpg
└── woman.png
```

A `woman.png` (a foto do "Fale Conosco") não existe no template original; ela e todas as outras imagens estão no repositório, em [aula11/backend/core/static/img](https://github.com/rg3915/dicas-de-django/tree/aula11/backend/core/static/img).

## Imagens com a tag static

No template original, as imagens são caminhos relativos:

```html
<img src="./images/products/men/product1.jpg" class="rounded-tl-lg rounded-tr-lg" />
```

No Django, carregue a tag no topo do arquivo com `{% load static %}` e troque **todas** as imagens por `{% static '...' %}`, com o caminho a partir da pasta `static`:

```html
<img src="{% static 'img/products/men/product1.jpg' %}" class="rounded-tl-lg rounded-tr-lg" />
```

O mesmo vale para o `hero-img.svg`, os outros produtos e a `woman.png`. Sem isso, a página aparece mas as imagens não carregam.

## Resumindo classes com @apply

No template original, cada campo de formulário repete uma lista grande de classes do Tailwind:

```html
<input type="email" placeholder="Enter email address" class="bg-gray-600 text-gray-200 placeholder-gray-400 px-4 py-3 w-full rounded-lg focus:outline-none mb-4" />
```

Como o formulário "Fale Conosco" tem quatro campos, criamos uma classe nova, `form-control`, que junta essas classes. Com o Tailwind via CDN, isso é feito num `<style type="text/tailwindcss">` dentro do `<head>`:

```html
<style type="text/tailwindcss">
  @layer utilities {
    .form-control {
      @apply text-gray-600 placeholder-gray-400 px-4 py-3 w-full rounded-lg focus:outline-none mb-4
    }
  }
</style>
```

* `type="text/tailwindcss"`: faz o script do CDN processar esse CSS, entendendo as diretivas do Tailwind.
* `@layer utilities`: define em qual camada do Tailwind a nova classe entra.
* `@apply`: aplica todas aquelas classes utilitárias na classe `.form-control`.

E nos campos fica só `class="form-control"`:

```html
<input
  id="id_email"
  name="email"
  type="email"
  class="form-control"
  placeholder="Seu E-mail"
/>
```

## O index.html

```html
<!-- backend/core/templates/index.html -->
{% load static %}
<!-- ... (head, navegação e hero: veja o arquivo completo no GitHub) -->
        <div class="grid grid-flow-row grid-cols-1 md:grid-cols-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-10">
          <div class="shadow-lg rounded-lg">
            <a href="#">
              <img src="{% static 'img/products/men/product1.jpg' %}" class="rounded-tl-lg rounded-tr-lg" />
            </a>
            <div class="p-5">
              <h3><a href="#">Mens T-Shirt</a></h3>
              <!-- ... (cores, tamanhos e botões; os outros produtos repetem este bloco) -->
<!-- ... -->
      <div id="contato" class="flex flex-row rounded-lg shadow-lg my-20">
        <div class="lg:w-3/5 w-full rounded-lg bg-gradient-to-r from-gray-200 to-gray-200 lg:from-gray-400 lg:via-gray-300 lg:to-transparent text-gray-700 p-12">
          <div class="lg:w-1/2">
            <h3 class="text-2xl font-extrabold mb-4">Fale Conosco</h3>
            <p class="mb-4 leading-relaxed">Envie uma mensagem e diga como podemos te ajudar.</p>
            <div>
              <form action="." method="POST">
                {% csrf_token %}
                <input
                  id="id_name"
                  name="name"
                  type="text"
                  class="form-control"
                  placeholder="Seu Nome"
                />
                <input
                  id="id_email"
                  name="email"
                  type="email"
                  class="form-control"
                  placeholder="Seu E-mail"
                />
                <input
                  id="id_title"
                  name="title"
                  type="text"
                  class="form-control"
                  placeholder="Título da mensagem"
                />
                <textarea
                  id="id_body"
                  name="body"
                  type="text"
                  class="form-control"
                  rows="5"
                ></textarea>
                <button type="submit" class="bg-purple-600 hover:bg-purple-700 text-white py-3 rounded-lg w-full">Enviar</button>
              </form>
<!-- ... (veja o arquivo completo no GitHub) -->
```

Código completo: [backend/core/templates/index.html](https://github.com/rg3915/dicas-de-django/blob/b7f815620eb42584e5edc6bfc905156a6ed5a990/backend/core/templates/index.html)

Os blocos de cada produto são iguais, mudando só a imagem e o nome. O formulário já tem `{% csrf_token %}` e os campos com `name` (`name`, `email`, `title` e `body`), prontos para quando ele for ligado a uma view.

## Rodando

```bash
python manage.py runserver
```

Em [http://localhost:8000](http://localhost:8000) aparece o topo com o menu, a seção "Grandes Marcas" com a ilustração, a "Coleção Masculina" (camiseta, calça, tênis e relógio), a "Coleção Feminina", o formulário "Fale Conosco" com a foto e o rodapé.

## Links

[https://github.com/itzpradip/tailwind-eshop-static-html](https://github.com/itzpradip/tailwind-eshop-static-html)

[https://youtu.be/iNDvh7O2WZM](https://youtu.be/iNDvh7O2WZM)
