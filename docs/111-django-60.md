# Novidades do Django 6.0

Publicado em 05/01/2026.

<a href="https://youtu.be/zug6K_Lks9k">
    <img src="../.gitbook/assets/youtube.png">
</a>

Doc: [https://docs.djangoproject.com/en/6.0/releases/6.0/](https://docs.djangoproject.com/en/6.0/releases/6.0/)

Github: [https://github.com/rg3915/django60](https://github.com/rg3915/django60)

## Python 3.12+

O Django 6.0 exige **Python 3.12 ou superior**. Confira a versão do Python antes de atualizar o projeto.

## Content Security Policy nativo

CSP agora é nativo: ative o middleware de CSP no `settings.py` e use o nonce nos templates, sem instalar o `django-csp`.

## Template partials

Defina um fragmento e reutilize no mesmo template, sem criar arquivo separado:

```html
{% partialdef card %}
  <div class="card">...</div>
{% endpartialdef %}

{% partial card %}
```

## Tasks

O Django 6.0 trouxe uma API nativa de tasks: decore a função com `@task` e chame `.enqueue()`. Quem executa é o backend configurado, como o do **django-tasks**.

Com o backend de banco do django-tasks, rode o worker em outro terminal:

```
python manage.py db_worker
```
