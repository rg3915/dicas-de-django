# 9 - Aplicando djhtml

[djhtml](https://github.com/rtts/djhtml)

```
pip install djhtml
pip freeze | grep djhtml >> requirements.txt
```

Antes:

```html
{\% extends "base.html" %}

{\% block content %}
  <h1 class="text-2xl font-bold">Conteúdo</h1>
  <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Vero tenetur repudiandae id animi, labore magni cumque tempore eum culpa esse exercitationem modi est enim sunt in maxime aut quo deleniti!</p>
  {\% if 'a' == 'a' %}
  {\% if '1' == '1' %}
  <span>A1</span>
  {\% endif %}
  {\% endif %}
{\% endblock content %}
```

```
find backend -name "*.html" | xargs djhtml -t 2 -i
```

Depois:

```html
{\% extends "base.html" %}

{\% block content %}
  <h1 class="text-2xl font-bold">Conteúdo</h1>
  <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Vero tenetur repudiandae id animi, labore magni cumque tempore eum culpa esse exercitationem modi est enim sunt in maxime aut quo deleniti!</p>
  {\% if 'a' == 'a' %}
    {\% if '1' == '1' %}
      <span>A1</span>
    {\% endif %}
  {\% endif %}
{\% endblock content %}
```
