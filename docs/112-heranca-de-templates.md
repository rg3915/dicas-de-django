# Herança de templates

Publicado em 23/01/2026.

<a href="https://youtu.be/poGZ0IXKBEw">
    <img src="../.gitbook/assets/youtube.png">
</a>

Projeto demonstrativo com Jinja2 e Python puro, mas a ideia é a mesma nos templates do Django e do Flask.

Github: [https://github.com/rg3915/heranca-templates-python](https://github.com/rg3915/heranca-templates-python)

## Pontos principais

* Logo, menu e rodapé repetidos em toda página? Coloque tudo num `base.html` e faça as páginas herdarem com `{% extends 'base.html' %}`.
* No `base.html`, deixe um `{% block title %}` com um título padrão. Cada página sobrescreve só o título.
* Crie blocos vazios como `extra_css` e `js`: a página que precisar de CSS ou script próprio preenche o bloco.
* Use `extends` para o esqueleto da página e `include` para pedaços reutilizáveis, como `includes/navbar.html`.

Tecnologias: Python 3, Jinja2 e PicoCSS.
