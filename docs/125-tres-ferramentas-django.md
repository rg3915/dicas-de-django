# 3 ferramentas que todo projeto Django devia ter

<!--agendado-->

> 📅 **Vídeo agendado:** será publicado no YouTube em **17/10/2026, às 10:00**.

<!--/agendado-->

<!--yt-block JmpU-HeKBc4 short-->

1. **Django Debug Toolbar**: mostra as consultas de cada página. No exemplo, a listagem fez 51 consultas; com `select_related`, caiu para 1.
2. **Django Extensions**: dezenas de comandos prontos, como o `show_urls`, que lista todas as rotas do projeto.
3. **django-upgrade**: reescreve o código antigo no padrão novo do Django (`admin.site.register` → `@admin.register`, `request.META` → `request.headers`).

```
uvx django-upgrade --target-version 6.1 livros/*.py
```

Neste tutorial você monta uma livraria pequena em Django 6.1 com PostgreSQL e instala as três ferramentas, uma de cada vez: a Debug Toolbar para enxergar as consultas, o Django Extensions para ganhar comandos novos e o django-upgrade para atualizar o código sozinho.

## Pré-requisitos

* Python 3.14 e o `uv`.
* Um PostgreSQL rodando na porta 5432 (veja como subir um com Docker na dica 58, "Postgres em vez de SQLite, até no dev"). Se preferir, os passos funcionam também com o SQLite.

Documentação das ferramentas:

* Django Debug Toolbar: [https://django-debug-toolbar.readthedocs.io/](https://django-debug-toolbar.readthedocs.io/)
* Django Extensions: [https://django-extensions.readthedocs.io/](https://django-extensions.readthedocs.io/)
* django-upgrade: [https://github.com/adamchainz/django-upgrade](https://github.com/adamchainz/django-upgrade)

## Passo 1: o projeto livraria

```
mkdir livraria && cd livraria
uv init
uv add django "psycopg[binary]" python-decouple django-debug-toolbar django-extensions django-upgrade
uv run django-admin startproject config .
uv run python manage.py startapp livros
```

```toml
# pyproject.toml
[project]
name = "livraria"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.14"
dependencies = [
    "django>=6.1.1",
    "django-debug-toolbar>=8.0.0",
    "django-extensions>=4.1",
    "django-upgrade>=1.32.0",
    "psycopg[binary]>=3.3.6",
    "python-decouple>=3.8",
]
```

O `django-upgrade` não precisa estar nas dependências (dá para rodar com `uvx`, como você vai ver no passo 5); ele está aqui só para ficar à mão.

### Models

```python
# livros/models.py
from django.db import models


class Autor(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo
```

### View, urls e template

A primeira versão da view é o jeito "de sempre", e tem dois detalhes antigos de propósito: o `Livro.objects.all()` (que vai gerar o N+1) e o `request.META["HTTP_USER_AGENT"]` (que o django-upgrade vai reescrever no final).

```python
# livros/views.py
from django.shortcuts import render

from .models import Livro


def livro_list(request):
    livros = Livro.objects.all()
    navegador = request.META["HTTP_USER_AGENT"]
    return render(request, "livros/livro_list.html", {"livros": livros, "navegador": navegador})
```

```python
# livros/urls.py
from django.urls import path

from . import views

app_name = "livros"

urlpatterns = [
    path("", views.livro_list, name="livro_list"),
]
```

```html
<!-- livros/templates/livros/livro_list.html -->
<!doctype html>
<html lang="pt-br">
<head><meta charset="utf-8"><title>Livros</title>
<style>body{font-family:system-ui,sans-serif;margin:24px;font-size:20px}li{margin:4px 0}@media (prefers-color-scheme:dark){body{background:#1d1f24;color:#eee}}</style></head>
<body>
<h1>Livros</h1>
<ul>
{% for livro in livros %}<li>{{ livro.titulo }} — {{ livro.autor }}</li>
{% endfor %}</ul>
</body>
</html>
```

Atenção: a Debug Toolbar só aparece em páginas HTML completas, com a tag `</body>`. É nela que a barra é injetada.

E o admin, também no estilo antigo:

```python
# livros/admin.py
from django.contrib import admin

from .models import Livro


class LivroAdmin(admin.ModelAdmin):
    list_display = ["titulo", "autor"]


admin.site.register(Livro, LivroAdmin)
```

## Passo 2: Django Debug Toolbar

### settings.py

```python
# config/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'debug_toolbar',
    'livros',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'livraria',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

INTERNAL_IPS = ['127.0.0.1']
```

As três peças da Debug Toolbar:

* `'debug_toolbar'` no `INSTALLED_APPS` (o `django.contrib.staticfiles` precisa estar lá, porque a barra tem CSS e JavaScript próprios).
* `DebugToolbarMiddleware` o mais cedo possível no `MIDDLEWARE`, mas depois de qualquer middleware que codifique a resposta (como o `GZipMiddleware`, se você usar).
* `INTERNAL_IPS`: a barra só aparece para os IPs desta lista, e só com `DEBUG = True`. Se o Django roda dentro do Docker, o seu navegador não chega como `127.0.0.1`; nesse caso, veja na documentação como configurar o `SHOW_TOOLBAR_CALLBACK`.

Os dados de conexão estão escritos no settings só para simplificar o exemplo; num projeto real, leia-os do `.env` com o `python-decouple` (o `django-admin startproject` também gera uma `SECRET_KEY`, que deve sair do código pelo mesmo motivo).

### urls.py

```python
# config/urls.py
from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("livros.urls")),
] + debug_toolbar_urls()
```

`debug_toolbar_urls()` adiciona as rotas internas da barra (em `/__debug__/`). Quando `DEBUG` é `False`, ela não adiciona nada.

### Banco e dados de exemplo

Crie o banco `livraria` no seu Postgres (por exemplo, `createdb -h localhost -U postgres livraria`, ou com `POSTGRES_DB: livraria` no `compose.yaml`) e rode as migrations. A Debug Toolbar 8 tem uma migration própria (para o painel de histórico), então o `migrate` também é necessário para ela:

```
uv run python manage.py makemigrations livros
uv run python manage.py migrate
```

Crie 50 livros, cada um com um autor diferente:

```
uv run python manage.py shell
```

```python
for i in range(1, 51):
    autor = Autor.objects.create(nome=f'Autor {i}')
    Livro.objects.create(titulo=f'Livro {i}', autor=autor)
```

### As 51 queries

Rode o servidor e abra `http://127.0.0.1:8000/`:

```
uv run python manage.py runserver
```

A barra aparece na lateral da página. Clique no painel **SQL**: são **51 consultas**. Uma busca os livros; as outras 50 são iguais, uma por livro, buscando o autor. Isso acontece porque, no template, `{{ livro.autor }}` acessa a `ForeignKey`, e cada acesso vai ao banco. O painel ainda marca essas consultas como **duplicadas** (ou "similares"), que é o sinal clássico do problema N+1.

### select_related: de 51 para 1

Troque uma linha na view:

```python
# livros/views.py
from django.shortcuts import render

from .models import Livro


def livro_list(request):
    livros = Livro.objects.select_related("autor")
    navegador = request.META["HTTP_USER_AGENT"]
    return render(request, "livros/livro_list.html", {"livros": livros, "navegador": navegador})
```

Recarregue a página: o painel SQL mostra **1 consulta**. O `select_related("autor")` faz um `JOIN` com a tabela de autores e traz tudo de uma vez. No painel, clique na consulta para ver o SQL completo e use o botão **Explain** para ver o plano de execução do Postgres.

Os outros painéis também valem a visita: **Time** (tempo da requisição), **Templates** (quais templates foram usados e com que contexto), **Cache**, **Signals** e **Headers**.

## Passo 3: Django Extensions

O Django Extensions já está no `INSTALLED_APPS` como `'django_extensions'`. Isso basta para ganhar dezenas de comandos novos no `manage.py`. O mais útil no dia a dia é o `show_urls`, que lista todas as rotas do projeto:

```
uv run python manage.py show_urls
```

Um trecho da saída (cada linha tem a URL, a view e o nome da rota):

```
/	livros.views.livro_list	livros:livro_list
/__debug__/history_refresh/	debug_toolbar.panels.history.views.history_refresh	djdt:history_refresh
/__debug__/render_panel/	debug_toolbar.views.render_panel	djdt:render_panel
/__debug__/sql_explain/	debug_toolbar.panels.sql.views.sql_explain	djdt:sql_explain
/__debug__/sql_select/	debug_toolbar.panels.sql.views.sql_select	djdt:sql_select
/admin/	django.contrib.admin.sites.index	admin:index
/admin/livros/livro/	django.contrib.admin.options.changelist_view	admin:livros_livro_changelist
/admin/livros/livro/<path:object_id>/change/	django.contrib.admin.options.change_view	admin:livros_livro_change
/admin/livros/livro/add/	django.contrib.admin.options.add_view	admin:livros_livro_add
/admin/login/	django.contrib.admin.sites.login	admin:login
```

Aparecem as suas rotas, as da Debug Toolbar e as do admin. É o jeito mais rápido de descobrir o nome de uma rota para usar no `{% url %}` ou de achar qual view atende uma URL. Para uma saída em tabela, use `show_urls --format aligned`.

Outros comandos que valem conhecer:

* `shell_plus`: um shell com todos os models já importados (o `shell` do Django faz isso sozinho desde a versão 5.2, mas o `shell_plus` ainda tem opções como `--print-sql`, que mostra o SQL de cada consulta).
* `graph_models`: gera um diagrama dos models (precisa do `pygraphviz` ou do `pydot`).
* `runserver_plus`: o `runserver` com o depurador do Werkzeug no navegador (precisa do `Werkzeug`).
* `list_model_info`: lista os campos e métodos de cada model.
* `print_settings`: mostra os valores finais do settings.
* `reset_db`: apaga e recria o banco (só em desenvolvimento).
* `generate_secret_key`: gera uma `SECRET_KEY` nova.
* `admin_generator`: gera um `admin.py` inicial para uma app.
* `validate_templates`: procura erros de sintaxe nos templates.

A lista completa está em [https://django-extensions.readthedocs.io/en/latest/command_extensions.html](https://django-extensions.readthedocs.io/en/latest/command_extensions.html).

## Passo 4: django-upgrade

O Django evolui, e o código antigo continua funcionando por um tempo, até virar aviso de depreciação e depois erro. O django-upgrade lê os seus arquivos e reescreve o que tem um jeito mais novo, de acordo com a versão alvo do Django.

### Rodando com uvx

Com o `uvx`, você nem precisa instalar o pacote no projeto:

```
uvx django-upgrade --target-version 6.1 livros/*.py
```

Saída:

```
Rewriting livros/admin.py
Rewriting livros/views.py
```

O que mudou (`git diff`):

```diff
--- a/livros/admin.py
+++ b/livros/admin.py
@@ -3,8 +3,8 @@ from django.contrib import admin
 from .models import Livro
 
 
+@admin.register(Livro)
 class LivroAdmin(admin.ModelAdmin):
     list_display = ["titulo", "autor"]
 
 
-admin.site.register(Livro, LivroAdmin)
--- a/livros/views.py
+++ b/livros/views.py
@@ -5,5 +5,5 @@ from .models import Livro
 
 def livro_list(request):
     livros = Livro.objects.select_related("autor")
-    navegador = request.META["HTTP_USER_AGENT"]
+    navegador = request.headers["user-agent"]
     return render(request, "livros/livro_list.html", {"livros": livros, "navegador": navegador})
```

* `admin.site.register(Livro, LivroAdmin)` virou o decorador `@admin.register(Livro)`.
* `request.META["HTTP_USER_AGENT"]` virou `request.headers["user-agent"]`. O `request.headers` (desde o Django 2.2) não diferencia maiúsculas de minúsculas e dispensa o prefixo `HTTP_`.

Outros exemplos do que ele reescreve: `url()` com regex para `path()`, o `CheckConstraint(check=...)` para `CheckConstraint(condition=...)`, `index_together` para `indexes`, e `assertFormError` para a assinatura nova. Para ver todos os fixers:

```
uvx django-upgrade --list-fixers
```

Dicas de uso:

* Rode com o git limpo, para revisar as mudanças com `git diff` antes do commit.
* `--check` só lista os arquivos que mudariam, sem alterar nada (útil na CI).
* Para rodar em todo o projeto: `git ls-files -z -- '*.py' | xargs -0 uvx django-upgrade --target-version 6.1`.

### Com pre-commit

Para que ninguém da equipe esqueça, coloque o django-upgrade no pre-commit. Ele roda nos arquivos alterados a cada commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/adamchainz/django-upgrade
    rev: "1.33.0"
    hooks:
      - id: django-upgrade
        args: [--target-version, "6.1"]
```

```
uvx pre-commit install
```

Se o hook reescrever algum arquivo, o commit é interrompido; você revisa, faz `git add` e commita de novo. Para conhecer o pre-commit: [https://pre-commit.com/](https://pre-commit.com/).

## Resumo

* **Debug Toolbar**: mostra as consultas de cada página. A listagem com 51 consultas caiu para 1 com `select_related`.
* **Django Extensions**: comandos prontos como o `show_urls`, que lista todas as rotas.
* **django-upgrade**: reescreve o código no padrão novo do Django (`@admin.register`, `request.headers`), com `uvx` ou no pre-commit.

As duas primeiras são ferramentas de desenvolvimento: em produção, deixe `DEBUG = False` (a barra some) ou tire-as do `INSTALLED_APPS` com um settings separado.
