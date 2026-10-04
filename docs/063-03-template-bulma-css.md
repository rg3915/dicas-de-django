# Dica 03 - Criando um template com Bulma CSS

**Versões usadas no vídeo:** não usa Django; Bulma 0.9.4 (via CDN) e Python 3.10.6 (só para o `http.server`).
{: .versoes }

<a href="https://youtu.be/AmzQJm0jPrA">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django) (branch `aula03`)

Nesta dica vamos experimentar o [Bulma](https://bulma.io/), um framework CSS só de classes (sem JavaScript), com nomes bem intuitivos: `container`, `notification`, `columns`, `column`, `card`, `button is-primary`. Vamos montar uma página com um aviso no topo, duas colunas (um card e um formulário) e alguns botões, tudo copiado da [documentação do Bulma](https://bulma.io/documentation/).

Até aqui o Projeto Dicas de Django ainda é só front-end: na [dica anterior](062-02-usando-http-server.md) vimos o Skeleton, agora o Bulma e na próxima o [Tailwind CSS](064-04-template-tailwindcss.md).

## Criando a issue e a branch

Como nas dicas anteriores, a issue foi criada com o [script da dica 01](061-01-criando-issues-com-api-github.md):

```bash
python cli/create_issue.py \
--title='Criando um template com Bulma CSS - Frontend' \
--body='g ch -b aula03
https://bulma.io/' \
--labels='frontend'
```

```
Successfully created Issue "Criando um template com Bulma CSS - Frontend"
```

A issue criada foi a **#94**. Então criamos a branch:

```bash
git checkout -b aula03
```

## Estrutura e servidor

Crie a pasta e o arquivo, e suba o servidor do Python na raiz do projeto, como vimos na [dica do http.server](062-02-usando-http-server.md):

```bash
mkdir -p src/pages/bulma
touch src/pages/bulma/index.html

python -m http.server 8000
```

## Montando o template passo a passo

### 1. O `head` com o Bulma via CDN

O Bulma é um único arquivo CSS. Basta o `<link>` para a versão minificada no jsDelivr:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
```

### 2. O esqueleto do `body`

Antes de colar os componentes, monte a estrutura e deixe um comentário marcando o lugar de cada um. Isso evita se perder nas `div`:

* `container`: centraliza o conteúdo e controla a largura máxima (veja **Layout > Container** na documentação).
* `notification is-primary`: uma caixa de aviso na cor primária do Bulma (verde-água).
* `columns` (no plural) é a linha; cada `column` (no singular) é uma coluna. Sem informar tamanho, as colunas dividem o espaço igualmente.

```html
<body>
  <div class="container">
    <div class="notification is-primary">
      <p>Esta página está usando <a href="https://bulma.io/">Bulma CSS</a>.</p>
    </div>

    <div class="columns">
      <div class="column">
        <!-- card -->
        <!-- https://bulma.io/documentation/components/card/ -->
      </div>

      <div class="column">
        <!-- form -->
        <!-- https://bulma.io/documentation/form/general/#complete-form-example -->
      </div>
    </div>

    <!-- buttons -->
    <!-- https://bulma.io/documentation/elements/button/#colors -->
  </div>
</body>
```

Na primeira tentativa do vídeo, a página carregou mas não ficou em duas colunas: uma `div` fechada no lugar errado tirou a segunda `column` de dentro de `columns`. A solução foi refazer o esqueleto acima e só depois colar os componentes. Se isso acontecer com você, confira se as duas `<div class="column">` estão dentro da mesma `<div class="columns">`.

### 3. Os componentes

* **Card** (primeira coluna): o exemplo da página [Card](https://bulma.io/documentation/components/card/), com imagem, mídia (foto, nome e @usuário) e conteúdo.
* **Formulário** (segunda coluna): o [Complete form example](https://bulma.io/documentation/form/general/#complete-form-example), com campos de texto, um campo válido (`is-success`), um inválido (`is-danger`), select, textarea, checkbox, radio e os botões Submit e Cancel.
* **Botões** (fora das colunas): as [cores de botão](https://bulma.io/documentation/elements/button/#colors), agrupadas em `div.buttons`.

## O código completo

```html
<!-- src/pages/bulma/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
  <link rel="shortcut icon" href="https://bulma.io/favicons/favicon-32x32.png?v=201701041855">
  <title>Bulma CSS</title>

  <!-- Bulma -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
</head>
<body>
  <div class="container">
    <div class="notification is-primary">
      <p>Esta página está usando <a href="https://bulma.io/">Bulma CSS</a>.</p>
    </div>

    <div class="columns">
      <div class="column">
        <!-- card -->
        <div class="card">
          <div class="card-image">
            <figure class="image is-4by3">
              <img src="https://bulma.io/images/placeholders/1280x960.png" alt="Placeholder image">
            </figure>
          </div>
          <div class="card-content">
            <div class="media">
              <div class="media-left">
                <figure class="image is-48x48">
                  <img src="https://bulma.io/images/placeholders/96x96.png" alt="Placeholder image">
                </figure>
              </div>
              <div class="media-content">
                <p class="title is-4">John Smith</p>
                <p class="subtitle is-6">@johnsmith</p>
              </div>
            </div>

            <div class="content">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit.
              Phasellus nec iaculis mauris. <a>@bulmaio</a>.
              <a href="#">#css</a> <a href="#">#responsive</a>
              <br>
              <time datetime="2016-1-1">11:09 PM - 1 Jan 2016</time>
            </div>
          </div>
        </div>
      </div>

      <div class="column">
        <!-- form -->
        <div class="field">
          <label class="label">Name</label>
          <div class="control">
            <input class="input" type="text" placeholder="Text input">
          </div>
        </div>

        <div class="field">
          <label class="label">Username</label>
          <div class="control has-icons-left has-icons-right">
            <input class="input is-success" type="text" placeholder="Text input" value="bulma">
            <span class="icon is-small is-left">
              <i class="fas fa-user"></i>
            </span>
            <span class="icon is-small is-right">
              <i class="fas fa-check"></i>
            </span>
          </div>
          <p class="help is-success">This username is available</p>
        </div>

        <div class="field">
          <label class="label">Email</label>
          <div class="control has-icons-left has-icons-right">
            <input class="input is-danger" type="email" placeholder="Email input" value="hello@">
            <span class="icon is-small is-left">
              <i class="fas fa-envelope"></i>
            </span>
            <span class="icon is-small is-right">
              <i class="fas fa-exclamation-triangle"></i>
            </span>
          </div>
          <p class="help is-danger">This email is invalid</p>
        </div>

        <div class="field">
          <label class="label">Subject</label>
          <div class="control">
            <div class="select">
              <select>
                <option>Select dropdown</option>
                <option>With options</option>
              </select>
            </div>
          </div>
        </div>

        <div class="field">
          <label class="label">Message</label>
          <div class="control">
            <textarea class="textarea" placeholder="Textarea"></textarea>
          </div>
        </div>

        <div class="field">
          <div class="control">
            <label class="checkbox">
              <input type="checkbox">
              I agree to the <a href="#">terms and conditions</a>
            </label>
          </div>
        </div>

        <div class="field">
          <div class="control">
            <label class="radio">
              <input type="radio" name="question">
              Yes
            </label>
            <label class="radio">
              <input type="radio" name="question">
              No
            </label>
          </div>
        </div>

        <div class="field is-grouped">
          <div class="control">
            <button class="button is-link">Submit</button>
          </div>
          <div class="control">
            <button class="button is-link is-light">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- buttons -->
    <div class="buttons">
      <button class="button is-primary">Primary</button>
      <button class="button is-link">Link</button>
    </div>

    <div class="buttons">
      <button class="button is-info">Info</button>
      <button class="button is-success">Success</button>
      <button class="button is-warning">Warning</button>
      <button class="button is-danger">Danger</button>
    </div>

  </div>
</body>
</html>
```

Os ícones do formulário (`<i class="fas fa-user"></i>` etc.) são do Font Awesome, que não foi carregado nesta página; por isso eles não aparecem. Se quiser os ícones, acrescente o CSS do Font Awesome no `head`.

## Resultado

Abra [http://localhost:8000](http://localhost:8000) e navegue até `src/` > `pages/` > `bulma/` (ou abra direto `http://localhost:8000/src/pages/bulma/`). A página mostra:

* a faixa verde-água com "Esta página está usando Bulma CSS.";
* à esquerda, o card com a imagem de exemplo 1280×960, John Smith e o texto Lorem ipsum;
* à direita, o formulário completo, com o campo Username em verde e o Email em vermelho;
* abaixo, os botões Primary e Link, e na linha seguinte Info, Success, Warning e Danger.

## Fechando a issue

Com a página pronta, o commit fecha a issue (no repositório, é o commit `Criando um template com Bulma CSS - Frontend. close #94` da branch `aula03`):

```bash
git add .
git commit -m 'Criando um template com Bulma CSS - Frontend. close #94'
git push
```

## Conclusão

Com um `<link>` e classes com nomes fáceis de lembrar, o Bulma monta uma página com layout em colunas, card, formulário e botões sem escrever uma linha de CSS. Na próxima dica faremos um template com Tailwind CSS.

## Links

[https://bulma.io/](https://bulma.io/)

[https://bulma.io/documentation/components/card/](https://bulma.io/documentation/components/card/)

[https://bulma.io/documentation/form/general/#complete-form-example](https://bulma.io/documentation/form/general/#complete-form-example)

[https://bulma.io/documentation/elements/button/#colors](https://bulma.io/documentation/elements/button/#colors)
