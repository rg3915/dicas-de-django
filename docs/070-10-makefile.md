# Dica 10 - Criando Makefile

**Versões usadas no vídeo:** GNU Make (Linux), com isort 5.10.1, autopep8 2.0.0, djhtml 1.5.2 e Python 3.10, no projeto da Dica 09 (Django 4.1.3).
{: .versoes }

<a href="https://youtu.be/HdsDqWXNHSc">
    <img src="../.gitbook/assets/youtube.png">
</a>

Nas dicas anteriores vimos três formatadores de código: o isort e o autopep8 ([Dica 08](068-08-isort-autopep8.md)) e o djhtml ([Dica 09](069-09-djhtml.md)). Cada um tem um comando comprido para digitar. Hoje vamos criar um `Makefile` para rodar esses comandos com um atalho curto, e todos de uma vez com `make lint`.

Código da aula: [https://github.com/rg3915/dicas-de-django/tree/aula10](https://github.com/rg3915/dicas-de-django/tree/aula10)

## Pré-requisitos

* O projeto da Dica 09, com `isort`, `autopep8` e `djhtml` instalados no ambiente virtual.
* O programa `make`, que já vem no Linux e no macOS. Uma pequena desvantagem: no Windows ele não vem instalado, e os comandos `find` e `xargs` usados aqui também são do Linux.

## Criando o Makefile

```bash
git checkout -b aula10

touch Makefile
```

Edite `Makefile`

```makefile
# Makefile
indenter:
	find backend -name "*.html" | xargs djhtml -t 2 -i

autopep8:
	find backend -name "*.py" | xargs autopep8 --max-line-length 120 --in-place

isort:
	isort -m 3 *

up:
	docker-compose up -d

lint: autopep8 isort indenter
```

**Atenção:** a linha de comando abaixo de cada alvo tem de começar com um **TAB**, e não com espaços. Com espaços, o `make` reclama com `*** missing separator.  Stop.`

Como funciona:

* Cada bloco é um **alvo** (`indenter`, `autopep8`, `isort`, `up`, `lint`), seguido de dois-pontos. As linhas indentadas abaixo dele são os comandos que o alvo roda.
* `indenter`: o djhtml em todos os `.html` da pasta `backend`, com indentação de 2 espaços (`-t 2`) e alterando os próprios arquivos (`-i`).
* `autopep8`: o autopep8 em todos os `.py` da pasta `backend`, aceitando linhas de até 120 caracteres.
* `isort`: ordena os imports de todo o projeto, no modo 3 (*vertical hanging indent*).
* `up`: sobe os containers do docker-compose da [Dica 07](067-07-docker-compose.md).
* `lint`: não tem comando próprio; depois dos dois-pontos ficam as **dependências**, os alvos que o `make` roda antes, nessa ordem: `autopep8`, `isort` e `indenter`.

Para rodar um alvo, é `make` e o nome dele:

```bash
make isort
make up
```

## Rodando make lint

```bash
make lint
```

O `make` mostra cada comando antes de rodá-lo:

```
find backend -name "*.py" | xargs autopep8 --max-line-length 120 --in-place
isort -m 3 *
find backend -name "*.html" | xargs djhtml -t 2 -i
reindented backend/core/templates/base.html
1 template has been reindented.
4 templates were already perfect!
```

Os arquivos Python já estavam em ordem (foram formatados na Dica 08), mas o djhtml achou o que arrumar no `base.html`: o `<head>` e o `<body>` estavam encostados na margem, e agora ficaram um nível para dentro do `<html>`. O `git diff` mostra a mudança, e o arquivo ficou assim:

```html
<!-- backend/core/templates/base.html -->
{% load static %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
    <link rel="shortcut icon" href="https://www.djangoproject.com/favicon.ico">
    <title>Django</title>

    <!-- TailwindCSS -->
    <script src="https://cdn.tailwindcss.com"></script>

    <link rel="stylesheet" href="{% static 'css/style.css' %}">

  </head>
  <body class="flex flex-col min-h-screen">
    {% include "includes/menu.html" %}

    <main class="flex-auto">
      {% block content %}{% endblock content %}
    </main>

    {% include "includes/footer.html" %}

    <script src="{% static 'js/main.js' %}"></script>
  </body>
</html>
```

## Conclusão

Com o `Makefile`, em vez de lembrar três comandos compridos, basta um `make lint` antes de cada commit. Vamos usar e ampliar esse `Makefile` daqui para frente.
