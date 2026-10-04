# Dica 04 - Criando um template com Tailwind CSS

**Versões usadas no vídeo:** não usa Django; Tailwind CSS 3 (Play CDN, `cdn.tailwindcss.com`) e Python 3.10.6 (só para o `http.server`).
{: .versoes }

<a href="https://youtu.be/1aNSwcv5jIM">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django) (branch `aula04`)

Nesta dica vamos experimentar o [Tailwind CSS](https://tailwindcss.com/), um framework CSS de baixo nível, baseado em classes utilitárias (`flex`, `h-16`, `bg-slate-800`, `text-2xl`...) e pensado com a ideia de *mobile first*. Vamos montar um layout de dashboard com cabeçalho, barra lateral, área principal e rodapé, e usar `absolute` e `relative` para mostrar como posicionar elementos.

É mais um framework CSS da série, depois do Skeleton ([dica 02](062-02-usando-http-server.md)) e do Bulma ([dica 03](063-03-template-bulma-css.md)).

## Formas de instalar

Na documentação, em **Docs > Installation**, o Tailwind oferece algumas opções: Tailwind CLI, PostCSS, guias por framework e o **Play CDN**. Vamos usar o CDN, que é a forma mais simples e rápida, com praticamente o mesmo resultado para o nosso teste:

```html
<script src="https://cdn.tailwindcss.com"></script>
```

O CDN é um script que gera o CSS das classes que você usa, direto no navegador. Serve para desenvolvimento e experimentos; em produção o recomendado é gerar o CSS com o CLI.

Duas ferramentas úteis:

* [Tailwind Play](https://play.tailwindcss.com/): um editor online em que você escreve o HTML e vê o resultado em tempo real. No vídeo, trocar a classe `text-...` por `text-red-600` muda a cor do texto na hora.
* [Tailwind Toolbox](https://www.tailwindtoolbox.com/starter-templates): templates prontos e gratuitos feitos com Tailwind, como o dashboard **Winstein** mostrado no vídeo.

## Criando a issue e a branch

Com o [script da dica 01](061-01-criando-issues-com-api-github.md):

```bash
python cli/create_issue.py \
--title='Criando um template com Tailwind CSS - Frontend' \
--body='g ch -b aula04
https://tailwindcss.com/' \
--labels='frontend'
```

```
Successfully created Issue "Criando um template com Tailwind CSS - Frontend"
```

A issue criada foi a **#95**. Então criamos a branch:

```bash
git checkout -b aula04
```

## Estrutura e servidor

```bash
mkdir -p src/pages/tailwind
touch src/pages/tailwind/index.html

python -m http.server 8000
```

## O código completo

```html
<!-- src/pages/tailwind/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
  <link rel="shortcut icon" href="https://tailwindcss.com/favicons/favicon-32x32.png?v=3">
  <title>TailwindCSS</title>

  <!-- TailwindCSS -->
  <script src="https://cdn.tailwindcss.com"></script>

  <style>
    .main-content {
      height: calc(100vh - 4rem - 4rem);
    }
  </style>
</head>
<body class="flex flex-col min-h-screen">
  <header class="h-16 bg-slate-800 text-gray-100 flex justify-center items-center">
    <h1 class="text-2xl font-bold">TailwindCSS</h1>
  </header>

  <main class="flex-auto">
    <div class="flex main-content">
      <!-- aside -->
      <div class="flex flex-col relative w-1/6 bg-stone-800 border-r border-gray-200">
        <!-- button -->
        <button class="absolute -right-4 top-12 h-8 w-8 bg-slate-800 text-gray-50 rounded-full border border-gray-200 z-10"><</button>
      </div>
      <!-- main -->
      <div class="relative w-5/6 bg-zinc-800">
        <div class="absolute h-10 w-10 bg-yellow-500 flex items-center justify-center">1</div>
        <div class="absolute right-0 h-10 w-10 bg-yellow-500 flex items-center justify-center">2</div>
        <div class="absolute right-0 bottom-0 h-10 w-10 bg-yellow-500 flex items-center justify-center">3</div>
        <div class="absolute bottom-0 h-10 w-10 bg-yellow-500 flex items-center justify-center">4</div>
        <div class="absolute top-1/2 left-1/2 h-10 w-10 bg-red-500 flex items-center justify-center">5</div>
        <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 h-10 w-10 bg-yellow-500 flex items-center justify-center">
        5
        <!-- ball -->
        <span class="absolute -right-1.5 -top-1.5 h-3 w-3 bg-blue-500 rounded-full"></span>
        </div>
      </div>
    </div>
  </main>

  <footer class="h-16 bg-slate-800 text-gray-100 flex justify-between items-center px-4 text-lg">
    <h1>Dicas de Django © 2023</h1>
    <h1>by Regis do Python</h1>
  </footer>

</body>
</html>
```

## Explicando o layout

### Rodapé sempre embaixo

O `body` tem `flex flex-col min-h-screen`: ele é um flexbox em coluna com, no mínimo, a altura da tela. O `main` tem `flex-auto`, então ocupa todo o espaço que sobra entre o `header` e o `footer`. Resultado: o rodapé fica sempre na parte de baixo da tela, mesmo com pouco conteúdo.

### Altura da área principal com `calc`

O cabeçalho e o rodapé têm `h-16`, ou seja, `4rem` de altura cada. Por isso a classe própria `.main-content` usa:

```css
.main-content {
  height: calc(100vh - 4rem - 4rem);
}
```

`100vh` é a altura da tela inteira; tirando os `4rem` do cabeçalho e os `4rem` do rodapé, a área do meio ocupa exatamente o resto. Assim o layout também fica responsivo na vertical.

### Barra lateral e área principal

Dentro de `.main-content` há duas `div` lado a lado (`flex`):

* a barra lateral, com `w-1/6` (um sexto da largura), `bg-stone-800` e uma borda à direita (`border-r border-gray-200`);
* a área principal, com `w-5/6` e `bg-zinc-800`.

### Posicionamento com `relative` e `absolute`

Um elemento `absolute` é posicionado em relação ao ancestral mais próximo que tem `relative`. Por isso as duas `div` têm `relative`:

* O botão `<` da barra lateral tem `absolute -right-4 top-12`: fica `1rem` para fora da borda direita (o `-` torna o valor negativo) e `3rem` abaixo do topo, metade sobre a barra e metade sobre a área principal. O `z-10` deixa o botão por cima. `h-8 w-8 rounded-full` o transforma num círculo.
* Os quadrados amarelos 1, 2, 3 e 4 vão para os cantos da área principal: sem nada (canto superior esquerdo), `right-0` (superior direito), `right-0 bottom-0` (inferior direito) e `bottom-0` (inferior esquerdo).
* O quadrado vermelho 5 tem `top-1/2 left-1/2`: o seu canto superior esquerdo fica no centro, então ele aparece deslocado.
* O quadrado amarelo 5 tem, além disso, `transform -translate-x-1/2 -translate-y-1/2`, que o move metade da própria largura e altura para trás: agora ele fica exatamente centralizado, sobrepondo parte do vermelho.
* A bolinha azul (`span` com `absolute -right-1.5 -top-1.5 h-3 w-3 rounded-full`) fica no canto superior direito do quadrado amarelo 5, como um selo de notificação.

### Cores

As cores do Tailwind têm variações de tonalidade de 50 a 900: `text-slate-500`, `text-slate-600`, `text-slate-900` etc. Veja a paleta em [Customizing Colors](https://tailwindcss.com/docs/customizing-colors) e o funcionamento do flexbox em [Flex](https://tailwindcss.com/docs/flex).

## Resultado

Abra `http://localhost:8000/src/pages/tailwind/`. Você verá o cabeçalho escuro com **TailwindCSS** centralizado, a barra lateral com o botão redondo `<` na borda, os quatro quadrados amarelos nos cantos, os quadrados 5 no centro e o rodapé com "Dicas de Django © 2023" à esquerda e "by Regis do Python" à direita. Redimensione a janela (ou abra o DevTools): o layout se ajusta tanto na horizontal quanto na vertical.

## Fechando a issue

O vídeo termina com a página pronta. No repositório, o commit é `Criando um template com Tailwind CSS - Frontend. close #95`, na branch `aula04`:

```bash
git add .
git commit -m 'Criando um template com Tailwind CSS - Frontend. close #95'
git push
```

## Conclusão

Com o Tailwind você monta o layout direto no HTML, combinando classes utilitárias, e só precisou de uma linha de CSS próprio (o `calc` da altura). Na próxima dica vamos usar o Tailwind junto com o htmx.

## Links

[https://tailwindcss.com/](https://tailwindcss.com/)

[https://play.tailwindcss.com/](https://play.tailwindcss.com/)

[https://merakiui.com](https://merakiui.com)

Tailwind Elements (tailwind-elements.com)

[https://www.tailwindtoolbox.com/starter-templates](https://www.tailwindtoolbox.com/starter-templates)

[https://flowbite.com/](https://flowbite.com/)
