# Dica 05 - htmx simples

**Versões usadas no vídeo:** não usa Django; htmx 1.8.4, Tailwind CSS 3 (Play CDN) e Python 3.10.6 (só para o `http.server`).
{: .versoes }


<a href="https://youtu.be/GioIXTokrA8">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django) (branch `aula05`)

Playlist sobre htmx: [https://www.youtube.com/watch?v=W4AKpCh1Sj0&list=PLsGCdfxkV9upBW0CS7CyvkP64GoxvTDDd](https://www.youtube.com/watch?v=W4AKpCh1Sj0&list=PLsGCdfxkV9upBW0CS7CyvkP64GoxvTDDd)

Nesta dica vamos ver, de uma forma bem simples, como funciona o [htmx](https://htmx.org/). Vamos fazer uma tabela com um campo de texto e um botão **Adicionar**: a cada clique, o htmx busca um pedaço de HTML (um "componente") e acrescenta uma nova linha na tabela, sem escrever nenhuma linha de JavaScript.

Repare que o htmx não tem nada a ver com o Django: ele só faz uma requisição e coloca no DOM o HTML que voltou. Aqui o HTML vem de um arquivo estático servido pelo `http.server`; mais adiante no projeto, ele virá de uma view do Django.

## Criando a issue e a branch

Com o [script da dica 01](061-01-criando-issues-com-api-github.md):

```bash
python cli/create_issue.py \
--title='htmx simples - Frontend' \
--body='g ch -b aula05
https://htmx.org/' \
--labels='frontend'
```

```
Successfully created Issue "htmx simples - Frontend"
```

A issue criada foi a **#96**. Então criamos a branch:

```bash
git checkout -b aula05
```

## Estrutura e servidor

São dois arquivos: a página (`index.html`) e o componente que será inserido nela (`component.html`). Suba o servidor na **raiz do projeto**, como na [dica do http.server](062-02-usando-http-server.md):

```bash
mkdir -p src/pages/htmx
touch src/pages/htmx/index.html
touch src/pages/htmx/component.html

python -m http.server 8000
```

## A página `index.html`

A página usa o Tailwind via CDN (como na [dica anterior](064-04-template-tailwindcss.md)) para estilizar a tabela, o campo e o botão, e carrega o htmx também via CDN:

```html
<!-- htmx -->
<script src="https://unpkg.com/htmx.org@1.8.4"></script>
```

A tabela tem um `<tbody id="tbody">` com uma linha (`tr`) contendo um `input`. O botão **Adicionar** recebe três atributos do htmx:

* `hx-get="/src/pages/htmx/component.html"`: ao clicar, o htmx faz um `GET` nessa URL. É o caminho do arquivo a partir da raiz onde o `http.server` está rodando.
* `hx-target="#tbody"`: o HTML que voltar vai para o elemento com `id="tbody"`.
* `hx-swap="beforeend"`: o HTML é inserido **no fim** do conteúdo do alvo, ou seja, como uma nova linha depois das que já existem. (O padrão, `innerHTML`, substituiria todo o conteúdo do `tbody`.)

O código completo:

```html
<!-- index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
  <link rel="shortcut icon" href="https://tailwindcss.com/favicons/favicon-32x32.png?v=3">
  <title>htmx</title>

  <!-- TailwindCSS -->
  <script src="https://cdn.tailwindcss.com"></script>

  <!-- htmx -->
  <script src="https://unpkg.com/htmx.org@1.8.4"></script>
</head>
<body>
  <div class="flex flex-col sm:w-1/2">
    <div class="overflow-x-auto sm:-mx-6 lg:-mx-8">
      <div class="py-2 inline-block min-w-full sm:px-6 lg:px-8">
        <div class="overflow-hidden">
          <table class="min-w-full">
            <thead class="border-b">
              <tr>
                <th scope="col" class="text-sm font-medium text-gray-900 px-6 py-4 text-left">
                  Nome
                </th>
              </tr>
            </thead>
            <tbody id="tbody">
              <tr class="border-b">
                <td class="text-sm text-gray-900 font-light px-6 py-4 whitespace-nowrap">
                  <div class="mb-3 xl:w-96">
                    <input
                      type="text"
                      class="
                        form-control
                        block
                        w-full
                        px-3
                        py-1.5
                        text-base
                        font-normal
                        text-gray-700
                        bg-white bg-clip-padding
                        border border-solid border-gray-300
                        rounded
                        transition
                        ease-in-out
                        m-0
                        focus:text-gray-700
                        focus:bg-white
                        focus:border-blue-600
                        focus:outline-none
                      "/>
                  </div>
                </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="flex space-x-2 justify-center">
      <button
        type="button"
        class="
          inline-block
          px-6
          py-2.5
          bg-blue-600
          text-white
          font-medium
          text-xs
          leading-tight
          uppercase
          rounded
          shadow-md
          hover:bg-blue-700
          hover:shadow-lg
          focus:bg-blue-700
          focus:shadow-lg
          focus:outline-none
          focus:ring-0
          active:bg-blue-800
          active:shadow-lg
          transition
          duration-150
          ease-in-out
        "
        hx-get="/src/pages/htmx/component.html"
        hx-target="#tbody"
        hx-swap="beforeend"
      >
        Adicionar
      </button>
    </div>
  </div>

</body>
</html>
```

## O componente `component.html`

O componente é só uma linha da tabela com o `input`, igual à primeira linha do `tbody`. Ele não tem `<html>`, `<head>` nem `<body>`, porque é um pedaço de HTML para ser encaixado na página:

```html
<!-- component.html -->
<tr class="border-b">
  <td class="text-sm text-gray-900 font-light px-6 py-4 whitespace-nowrap">
    <div class="mb-3 xl:w-96">
      <input
        type="text"
        class="
          form-control
          block
          w-full
          px-3
          py-1.5
          text-base
          font-normal
          text-gray-700
          bg-white bg-clip-padding
          border border-solid border-gray-300
          rounded
          transition
          ease-in-out
          m-0
          focus:text-gray-700
          focus:bg-white
          focus:border-blue-600
          focus:outline-none
        "/>
    </div>
  </td>
</tr>
```

## Resultado

Abra `http://localhost:8000/src/pages/htmx/`. A tabela aparece com o cabeçalho **Nome**, um campo de texto e o botão azul **ADICIONAR** (o Tailwind deixa o texto em maiúsculas com a classe `uppercase`). A cada clique no botão, o htmx busca o `component.html` e acrescenta mais um campo na tabela. No terminal do `http.server` aparece um `GET /src/pages/htmx/component.html` por clique.

Tudo isso é só front-end: quando o botão faz o `GET` naquela URL, o htmx pega o conteúdo do HTML retornado e o coloca dentro do `tbody`, no final.

## Fechando a issue

O vídeo termina com o exemplo funcionando. No repositório, o commit é `htmx simples - Frontend. close #96`, na branch `aula05`:

```bash
git add .
git commit -m 'htmx simples - Frontend. close #96'
git push
```

## Conclusão

Com três atributos (`hx-get`, `hx-target` e `hx-swap`), o htmx busca HTML no servidor e o insere na página. Isso é uma pequena amostra; para entender todos os atributos, veja a playlist sobre htmx indicada no início.

## Links

[https://htmx.org/](https://htmx.org/)
