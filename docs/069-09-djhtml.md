# Dica 09 - Aplicando djhtml

**Versões usadas no vídeo:** djhtml 1.5.2 e Python 3.10, no projeto da Dica 08 (Django 4.1.3).
{: .versoes }

<a href="https://youtu.be/23mdIXcUp_o">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`). Se copiar código de lá, remova a `\`.

![](../.gitbook/assets/tags.png)

O [djhtml](https://github.com/rtts/djhtml) é uma biblioteca que formata (reindenta) arquivos HTML levando em conta as template tags do Django. Os formatadores de HTML comuns entendem as tags HTML, mas não sabem que um `{% if %}` abre um bloco que termina no `{% endif %}`; o djhtml sabe, e alinha tudo de acordo.

Na [Dica 08](068-08-isort-autopep8.md) formatamos o Python; agora é a vez dos templates.

Código da aula: [https://github.com/rg3915/dicas-de-django/tree/aula09](https://github.com/rg3915/dicas-de-django/tree/aula09)

## Instalação

```bash
git checkout -b aula09

pip install djhtml
```

```
Collecting djhtml
  Using cached djhtml-1.5.2-py3-none-any.whl
Installing collected packages: djhtml
Successfully installed djhtml-1.5.2
```

```bash
pip freeze | grep djhtml >> requirements.txt
```

## Desalinhando o template de propósito

Para ver o efeito, edite o `index.html` da app `core` e acrescente dois `if` aninhados, sem indentação nenhuma dentro deles. Muitos editores deixam assim, porque não se preocupam com o alinhamento das template tags.

Antes:

```html
<!-- backend/core/templates/index.html -->
{% extends "base.html" %}

{% block content %}
  <h1 class="text-2xl font-bold">Conteúdo</h1>
  <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Vero tenetur repudiandae id animi, labore magni cumque tempore eum culpa esse exercitationem modi est enim sunt in maxime aut quo deleniti!</p>
  {% if 'a' == 'a' %}
  {% if '1' == '1' %}
  <span>A1</span>
  {% endif %}
  {% endif %}
{% endblock content %}
```

## Rodando o djhtml

No vídeo, rodei no arquivo do template:

```bash
djhtml -t 2 -i backend/core/templates/index.html
```

```
reindented backend/core/templates/index.html
1 template has been reindented.
```

* `-t 2`: indentação de 2 espaços (o padrão é 4).
* `-i`: altera o próprio arquivo (*in-place*). Sem ele, o resultado só aparece na tela.

Para aplicar em todos os templates do projeto de uma vez, combine com `find` e `xargs`, como fizemos com o autopep8:

```bash
find backend -name "*.html" | xargs djhtml -t 2 -i
```

Depois:

```html
<!-- backend/core/templates/index.html -->
{% extends "base.html" %}

{% block content %}
  <h1 class="text-2xl font-bold">Conteúdo</h1>
  <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Vero tenetur repudiandae id animi, labore magni cumque tempore eum culpa esse exercitationem modi est enim sunt in maxime aut quo deleniti!</p>
  {% if 'a' == 'a' %}
    {% if '1' == '1' %}
      <span>A1</span>
    {% endif %}
  {% endif %}
{% endblock content %}
```

O segundo `if` ficou dentro do primeiro, e o `<span>` dentro do segundo, cada nível com 2 espaços a mais. O código ficou bem mais fácil de ler.

## Conclusão

O djhtml cuida do alinhamento de todo o HTML com template tags. Junto com o isort e o autopep8, ele entra no `make lint` da [Dica 10](070-10-makefile.md).
