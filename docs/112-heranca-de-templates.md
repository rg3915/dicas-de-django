# Herança de templates

Publicado em 23/01/2026.

**Testado com:** Python 3.7 ou superior e Jinja2 3.1.6 (a herança funciona igual nos templates do Django).
{: .versoes }

<a href="https://youtu.be/poGZ0IXKBEw">
    <img src="../.gitbook/assets/youtube.png">
</a>

Projeto demonstrativo com Jinja2 e Python puro, mas a ideia é a mesma nos templates do Django e do Flask.

Github: [https://github.com/rg3915/heranca-templates-python](https://github.com/rg3915/heranca-templates-python)

Imagine um site com uma página inicial, uma página "Sobre" e outras páginas, todas com o mesmo logo, o mesmo menu e o mesmo rodapé. Se cada arquivo HTML tiver uma cópia desse cabeçalho e rodapé, mudar um item do menu significa editar página por página.

A herança de templates resolve isso: você escreve a estrutura comum uma vez, num `base.html`, e deixa "buracos" com nome (os **blocos**). Cada página **herda** o `base.html` e preenche só os blocos que lhe interessam.

Neste tutorial vamos montar um site de três páginas com Jinja2 e um servidor HTTP feito só com a biblioteca padrão do Python, sem framework. No fim, mostro como a mesma coisa fica no Django.

## Pré-requisitos

* Python 3.7 ou superior.
* Noções básicas de HTML.

## Estrutura do projeto

```
heranca-templates-python/
├── app.py                  # servidor HTTP com Jinja2
├── requirements.txt
└── templates/
    ├── base.html           # template base
    ├── index.html          # página inicial
    ├── about.html          # página "Sobre"
    ├── templates.html      # página que explica herança de templates
    └── includes/
        └── navbar.html     # menu reutilizável
```

## Instalação

```bash
git clone https://github.com/rg3915/heranca-templates-python.git
cd heranca-templates-python

python -m venv .venv
source .venv/bin/activate   # no Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

A única dependência é o Jinja2:

```
# requirements.txt
Jinja2==3.1.6
```

Se for montar do zero, crie as pastas e os arquivos vazios:

```bash
mkdir -p templates/includes
touch templates/base.html templates/index.html templates/about.html templates/templates.html
touch templates/includes/navbar.html
touch app.py
```

## O servidor com Jinja2

```python
# app.py
from jinja2 import Environment, FileSystemLoader
from http.server import HTTPServer, BaseHTTPRequestHandler

env = Environment(loader=FileSystemLoader('templates'))


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            template = env.get_template('index.html')
            html = template.render(
                nome='Regis',
                videos=[
                    {
                        'titulo': 'Mini Curso A Essência do Django',
                        'descricao': 'Aprenda os conceitos fundamentais do Django e como criar seu primeiro projeto.',
                        'link': 'https://youtu.be/mlaCLGItR7Q?si=7AFw4dJVkmoK7vCR',
                        'thumbnail': 'https://img.youtube.com/vi/mlaCLGItR7Q/maxresdefault.jpg'
                    },
                    # ... (mais vídeos, veja o arquivo completo no GitHub)
                ]
            )

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        # ... (rotas /templates e /sobre, iguais à de cima; veja o arquivo completo no GitHub)

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<h1>404 - Pagina nao encontrada</h1>')


if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), MyHandler)
    print('Servidor rodando em http://localhost:8000')
    server.serve_forever()
```

Código completo: [app.py](https://github.com/rg3915/heranca-templates-python/blob/0acaf6581e5b77269defacfecb31245366cbec57/app.py)

O que acontece aqui:

* **`Environment(loader=FileSystemLoader('templates'))`** cria o ambiente do Jinja2 e diz que os templates ficam na pasta `templates`. É por esse loader que o `{% extends "base.html" %}` e o `{% include 'includes/navbar.html' %}` encontram os arquivos.
* **`MyHandler`** herda de `BaseHTTPRequestHandler`, do módulo `http.server` da biblioteca padrão. O método `do_GET` é chamado a cada requisição `GET`, e `self.path` traz o caminho pedido.
* Para cada rota, `env.get_template()` carrega o template e `render()` devolve o HTML como string. Na página inicial passamos duas variáveis: `nome` (uma string) e `videos` (uma lista de dicionários).
* `send_response`, `send_header` e `end_headers` montam a resposta HTTP; `wfile.write` envia o corpo em bytes.
* Qualquer outro caminho cai no `else` e recebe 404.

É um roteamento feito à mão com `if/elif`, exatamente o que um framework como Django ou Flask faz por você. Serve para o estudo; não use isso em produção.

## O template base

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="pt-BR" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Meu Site{% endblock %}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'includes/navbar.html' %}

    <main class="container">
        {% block content %}
        <!-- Conteúdo padrão aqui -->
        {% endblock %}
    </main>

    <footer class="container">
        {% block footer %}
        <p>&copy; 2026 Meu Site</p>
        {% endblock %}
    </footer>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

Este arquivo é o esqueleto de todas as páginas. Os blocos:

* **`title`** tem um valor padrão, "Meu Site". A página que não sobrescrever o bloco fica com esse título; as outras trocam só o título.
* **`extra_css`** começa vazio. Uma página que precisar de um CSS próprio preenche o bloco; as demais não precisam fazer nada.
* **`content`** é onde entra o conteúdo de cada página.
* **`footer`** tem um rodapé padrão, que pode ser trocado por uma página específica.
* **`extra_js`**, no fim do `body`, é o lugar para scripts específicos de uma página.

Você pode criar quantos blocos quiser. A regra prática é: tudo que é comum fica no base; tudo que varia vira um bloco.

O `data-theme="light"` fixa o tema claro do Pico CSS, um framework que estiliza as tags HTML direto, sem precisar de classes.

## O include: a navbar

```html
<!-- templates/includes/navbar.html -->
<nav class="container">
    <ul>
        <li><strong>Projeto Jinja2</strong></li>
    </ul>
    <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/templates">Templates</a></li>
        <li><a href="/sobre">Sobre</a></li>
    </ul>
</nav>
```

O `{% include 'includes/navbar.html' %}` no `base.html` simplesmente cola o conteúdo desse arquivo naquele ponto. Como o include está no base, o menu aparece em todas as páginas que herdam dele. Mudou um link? Muda aqui e pronto.

A diferença entre os dois mecanismos:

* **`extends`** define o **esqueleto** da página: a página filha diz "eu sou um base.html com estes blocos trocados";
* **`include`** insere um **pedaço** reutilizável (navbar, card, formulário) dentro de um template.

## As páginas filhas

### Página inicial

```html
<!-- templates/index.html (simplificado) -->
{% extends "base.html" %}

{% block title %}Home - Projeto Jinja2{% endblock %}

{% block content %}
<section>
    <hgroup>
        <h1>Boas-vindas, {{ nome }}!</h1>
        <p>Projeto de demonstração de herança de templates com Jinja2 e PicoCSS</p>
    </hgroup>

    <div class="grid">
        <article>
            <h3>Herança de Templates</h3>
            <p>Aprenda como funciona a herança de templates, blocos, includes e muito mais.</p>
            <a href="/templates" role="button">Ver Templates</a>
        </article>

        <article>
            <h3>Sobre o Canal</h3>
            <p>Conheça o canal Regis do Python e aprenda Python e Django.</p>
            <a href="/sobre" role="button" class="secondary">Saiba Mais</a>
        </article>
    </div>
</section>

<section>
    <h2>Vídeos sobre Django - Canal Regis do Python</h2>

    <div class="grid">
        {% for video in videos %}
        <article>
            <header>
                <img src="{{ video.thumbnail }}" alt="{{ video.titulo }}" style="width: 100%; height: auto; border-radius: 8px;">
            </header>
            <h3>{{ video.titulo }}</h3>
            <p>{{ video.descricao }}</p>
            <footer>
                <a href="{{ video.link }}" target="_blank" rel="noopener" role="button">Assistir no YouTube</a>
            </footer>
        </article>
        {% endfor %}
    </div>
</section>
{% endblock %}
```

No repositório o `index.html` tem ainda uma seção que mostra o próprio código do loop na tela (usando a tag `raw` do Jinja2 para que as tags não sejam interpretadas); omiti essa parte aqui.

Pontos importantes:

* **`{% extends "base.html" %}`** precisa ser a primeira tag do arquivo. A partir dela, o Jinja2 usa o base como esqueleto.
* A página **não repete** `<html>`, `<head>`, menu nem rodapé. Ela só define `title` e `content`.
* Tudo o que estiver **fora** de um bloco num template filho é ignorado. Por isso o conteúdo precisa estar dentro de `{% block content %}`.
* Não declare o mesmo bloco duas vezes no mesmo arquivo: o Jinja2 dá erro. É um engano comum ao copiar e colar código.
* **`{{ nome }}`** exibe a variável passada no `render()`. **`{% for video in videos %}`** percorre a lista, e `video.titulo` acessa a chave do dicionário (o Jinja2 aceita a notação de ponto para chaves de dicionário).

### Página "Sobre"

```html
<!-- templates/about.html (resumido) -->
{% extends "base.html" %}

{% block title %}Sobre - Regis do Python{% endblock %}

{% block content %}
<section>
    <hgroup>
        <h1>Sobre o Canal Regis do Python</h1>
        <p>Aprenda Python de forma prática e objetiva</p>
    </hgroup>
</section>

<section>
    <article>
        <h2>O Canal</h2>
        <p>
            O <strong>Regis do Python</strong> é um canal no YouTube dedicado ao ensino de Python
            e desenvolvimento web com Django.
        </p>
    </article>
</section>
{% endblock %}
```

O arquivo original tem mais alguns `<article>` com texto e links; a estrutura é a mesma. O `templates.html` segue o mesmo padrão e traz, na própria página, uma explicação de cada recurso do Jinja2.

### O teste mais simples

Para sentir o poder da herança, deixe um template só com uma linha:

```html
{% extends "base.html" %}
```

A página já aparece com título "Meu Site", menu, o conteúdo padrão do bloco `content` (vazio, no caso) e o rodapé. Depois acrescente um `{% block content %}...{% endblock %}` e veja só o miolo mudar.

## Rodando

```bash
python app.py
```

Acesse `http://localhost:8000`, `http://localhost:8000/templates` e `http://localhost:8000/sobre`. Repare que o menu e o rodapé são iguais nas três páginas, mas o título da aba muda. Agora altere um link em `includes/navbar.html`, recarregue e veja a mudança em todas as páginas de uma vez (o `Environment` recarrega templates alterados; se não aparecer, reinicie o servidor).

## O paralelo com o Django

A linguagem de templates do Django tem as mesmas tags para herança: `extends`, `block` e `include`. Os templates deste projeto funcionariam no Django praticamente sem mudança. O que muda é quem carrega e renderiza:

```python
# settings.py (trecho)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        # ...
    },
]
```

```python
# views.py
from django.shortcuts import render


def index(request):
    context = {
        'nome': 'Regis',
        'videos': [...],
    }
    return render(request, 'index.html', context)
```

* `DIRS` faz o papel do `FileSystemLoader('templates')`; `APP_DIRS=True` também procura em `templates/` de cada app.
* `render(request, 'index.html', context)` faz o `get_template` + `render` + resposta HTTP que escrevemos à mão no `do_GET`.
* As rotas vão para o `urls.py`, no lugar do `if self.path == ...`.

Diferenças pequenas entre as duas linguagens que vale conhecer:

| Recurso | Jinja2 | Django |
|---|---|---|
| Conteúdo do bloco pai | `{{ super() }}` | `{{ block.super }}` |
| Chamar métodos | `{{ lista.count(1) }}` (com argumentos) | `{{ objeto.metodo }}` (sem argumentos) |
| Arquivos estáticos | caminho direto | `{% load static %}` e `{% static 'css/style.css' %}` |
| Mostrar tags sem interpretar | tag `raw` (fechada com `endraw`) | tag `verbatim` (fechada com `endverbatim`) |

No Django, a convenção é ter um `base.html` no projeto e templates de cada app estendendo-o, com includes em pastas como `includes/` ou `partials/`. No Flask, que usa Jinja2, é exatamente o código deste tutorial.

## Resumo

* Logo, menu e rodapé repetidos em toda página? Coloque tudo num `base.html` e faça as páginas herdarem com `{% extends 'base.html' %}`.
* No `base.html`, deixe um `{% block title %}` com um título padrão. Cada página sobrescreve só o título.
* Crie blocos vazios como `extra_css` e `extra_js`: a página que precisar de CSS ou script próprio preenche o bloco.
* Use `extends` para o esqueleto da página e `include` para pedaços reutilizáveis, como `includes/navbar.html`.

Documentação: [herança de templates no Jinja2](https://jinja.palletsprojects.com/en/stable/templates/#template-inheritance) e [no Django](https://docs.djangoproject.com/en/6.0/ref/templates/language/#template-inheritance).
