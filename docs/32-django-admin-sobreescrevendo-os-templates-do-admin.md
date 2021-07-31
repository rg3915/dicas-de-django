# 32 - Django Admin: Sobreescrevendo os templates do Admin

<a href="https://youtu.be/0d9VcL8ssTg">
    <img src="../.gitbook/assets/youtube.png">
</a>

![img/botao_admin.png](../.gitbook/assets/botao_admin.png)

Se você olhar em 

https://github.com/django/django/tree/main/django/contrib/admin/templates/admin

verá todos os templates usados no Admin.

Na pasta da virtualenv do seu projeto também.

```
ls -l .venv/lib/python3.8/site-packages/django/contrib/admin/templates/admin/
cat .venv/lib/python3.8/site-packages/django/contrib/admin/templates/admin/change_list.html
```

Olhando na doc do Django em [Set up your projects admin template directories](https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#set-up-your-projects-admin-template-directories) nós vemos que devemos ter a seguinte estrutura de pastas:

```
myproject
├── core
│   ├── templates
│   │   ├── admin
│   │   │   ├── base_site.html
│   │   │   ├── login.html
│   │   │   ├── core
│   │   │   │   ├── article
│   │   │   │   │   └── change_list.html
│   │   │   │   └── change_list.html
```

Então vamos criar nossas pastas

```
mkdir -p myproject/core/templates/admin/core/article
```

Agora vamos criar o primeiro `change_list.html`

```
touch myproject/core/templates/admin/core/change_list.html
```

E seu conteúdo será:

```html
{% extends "admin/change_list.html" %}

{% block object-tools-items %}
  {{ block.super }}
  <li>
    <a href="botao-da-app/">
      Novo botão
    </a>
  </li>
{% endblock %}
```

Depois

```
touch myproject/core/templates/admin/core/article/change_list.html
```

Com o conteúdo:

```html
{% extends "admin/change_list.html" %}

{% block object-tools-items %}
  {{ block.super }}
  <li>
    <a href="botao-artigo/">
      Botão do Artigo
    </a>
  </li>
{% endblock %}
```

Para que o Django Admin reconheça esses templates precisamos configurar o `settings.py`

```python
# settings.py
TEMPLATES = [
    {
        ...
        'DIRS': [
            BASE_DIR,
            os.path.join(BASE_DIR, 'templates')
        ],
        ...
    },
]
```

Agora edite `admin.py`

```python
from django.contrib import admin, messages
# admin.py
from django.shortcuts import redirect
from django.urls import path


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    ...

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                'botao-artigo/',
                self.admin_site.admin_view(self.minha_funcao, cacheable=True)
            ),
        ]
        return my_urls + urls

    def minha_funcao(self, request):
        print('Ao clicar no botão, faz alguma coisa...')
        messages.add_message(
            request,
            messages.INFO,
            'Ação realizada com sucesso.'
        )
        return redirect('admin:core_article_changelist')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ...

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                'botao-da-app/',
                self.admin_site.admin_view(self.minha_funcao_category, cacheable=True)
            ),
        ]
        return my_urls + urls

    def minha_funcao_category(self, request):
        print('Ao clicar no botão, faz alguma coisa em category...')
        messages.add_message(
            request,
            messages.INFO,
            'Ação realizada com sucesso.'
        )
        return redirect('admin:core_category_changelist')
```

## Sobreescrevendo a tela de login do Admin

<a href="https://youtu.be/ci4LtLxDCRM">
    <img src="../.gitbook/assets/youtube.png">
</a>

![img/login.png](../.gitbook/assets/login.png)

Em [AdminSite attributes](https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#adminsite-attributes) nós temos o atributo [AdminSite.login_template](https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#django.contrib.admin.AdminSite.login_template).

A partir daí podemos fazer

```python
# admin.py
admin.site.login_template = 'myproject/core/templates/admin/login.html'
```

Vendo

```
cat .venv/lib/python3.8/site-packages/django/contrib/admin/templates/admin/login.html
cat .venv/lib/python3.8/site-packages/django/contrib/admin/templates/admin/base_site.html
```

E nos templates

```
touch myproject/core/templates/admin/login.html
```


```html
<!-- myproject/core/templates/admin/login.html -->
{% extends "admin/login.html" %}
{% load static %}

{% block branding %}
  <h1 id="site-name">
    <a href="{% url 'admin:index' %}">
      <img src="{% static 'img/django-logo-negative.png' %}" alt="django-logo-negative.png" width="100px">
    </a>
  </h1>
{% endblock %}

{% block extrastyle %}
  {{ block.super }}
  <link rel="stylesheet" type="text/css" href="{% static "css/login.css" %}" />
  {{ form.media }}
{% endblock %}
```

E pra caprichar no CSS

```css
/* myproject/core/static/css/login.css */
body.login {
    background: url("../img/headset.jpg") no-repeat center center;
    background-size: 100% auto;
}

html {
    min-height: 100%;
}
```

https://www.djangoadmintutorials.com/how-to-customize-django-admin-login-page/


## Inserindo um logo no header do Admin

<a href="https://youtu.be/7NcghC_eySs">
    <img src="../.gitbook/assets/youtube.png">
</a>

![img/header_admin.png](../.gitbook/assets/header_admin.png)

Basta criar `base_site.html`

```
touch myproject/core/templates/admin/base_site.html
```

```html
{% extends "admin/base_site.html" %}
{% load static %}

{% block branding %}
  <h1 id="site-name">
    <a href="{% url 'admin:index' %}">
      <img src="{% static 'img/django-logo-negative.png' %}" alt="django-logo-negative.png" width="70px">
    </a>
  </h1>
{% endblock %}
```

**Importante:** mude a ordem das `apps` em `settings.py`

```python
# settings.py
INSTALLED_APPS = [
    'myproject.core',
    'django.contrib.admin',
    ...
]
```

https://books.agiliq.com/projects/django-admin-cookbook/en/latest/logo.html

