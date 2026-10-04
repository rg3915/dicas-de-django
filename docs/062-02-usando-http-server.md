# Dica 02 - Usando http.server

**Versões usadas no vídeo:** não usa Django; Python 3.10.6 (módulo `http.server` da biblioteca padrão) e Skeleton CSS 2.0.4.
{: .versoes }

<a href="https://youtu.be/D4FeNPq8UTY">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django) (branch `aula02`)

Você sabia que o Python tem um módulo que roda um servidor web no seu computador? É o `http.server`, da biblioteca padrão: não precisa instalar nada. Ele serve os arquivos da pasta em que você está, e é ótimo para ver uma página HTML estática no navegador. Nas próximas dicas (Bulma, Tailwind e htmx) vamos usá-lo para testar os templates antes de levá-los para o Django.

## Criando a issue e a branch

Esta é a aula 2 do Projeto Dicas de Django. Seguindo o fluxo da [dica anterior](061-01-criando-issues-com-api-github.md), primeiro criamos a issue com o nosso script:

```bash
python cli/create_issue.py --title='Usando http.server' --body='g ch -b aula02' --labels='backend'
```

A issue criada foi a **#93**, e o script anotou no `tarefas.txt`:

```
[ ] 93 - Usando http.server
    backend

    g ch -b aula02

    ml; g add . ; g co -m 'Usando http.server. close #93'; gp
```

(`g ch` é o alias do Regis para `git checkout`, `ml` para `make lint` e `gp` para `git push`.) Então criamos a branch da aula:

```bash
git checkout -b aula02
```

## A página HTML

Crie a pasta `public` e um `index.html` dentro dela:

```bash
mkdir public
touch public/index.html
```

Vamos usar o [Skeleton](http://getskeleton.com/), o CSS mais simples que existe, carregado via CDN. A página tem só um título, uma frase e um botão:

```html
<!-- public/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
  <link rel="shortcut icon" href="http://getskeleton.com/dist/images/favicon.png">
  <title>Skeleton CSS</title>

  <!-- Skeleton -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css">
</head>
<body>
  <h1>Skeleton template example</h1>
  <p>Esta página está usando <a href="http://getskeleton.com/">skeleton CSS</a>.</p>
  <button class="button-primary">Botão</button>
</body>
</html>
```

A classe `button-primary` é do Skeleton e deixa o botão azul.

## Rodando o servidor

Na raiz do projeto (não dentro de `public`), simplesmente digite:

```bash
python -m http.server 8000
```

```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

A porta é opcional: sem ela, o `http.server` usa a 8000. Se a 8000 estiver ocupada, use outra, por exemplo `python -m http.server 8001`.

Abra [http://localhost:8000](http://localhost:8000) no navegador. Como não há um `index.html` na raiz, o servidor mostra a listagem das pastas. Clique em `public/` (ou abra direto `http://localhost:8000/public/`) e a página aparece com o título **Skeleton template example**, a frase e o botão azul. Cada acesso aparece no terminal como uma linha de log, e para parar o servidor use `Ctrl+C`.

## Fechando a issue

O vídeo termina com a página no ar. Para fechar a issue, faça o commit que ficou anotado no `tarefas.txt` (no repositório, é o commit `Usando http.server. close #93` da branch `aula02`):

```bash
git add .
git commit -m 'Usando http.server. close #93'
git push
```

## Conclusão

Com um único comando, `python -m http.server`, você tem um servidor web local para ver páginas estáticas, sem instalar nada. Atenção: ele serve para desenvolvimento e testes; não é um servidor para produção.

## Links

[http://getskeleton.com/](http://getskeleton.com/)

[https://cdnjs.com/libraries/skeleton](https://cdnjs.com/libraries/skeleton)
