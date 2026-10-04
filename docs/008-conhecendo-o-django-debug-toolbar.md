# Dica 8 - Conhecendo o Django Debug Toolbar

**Versões usadas no vídeo:** Django 2.2.13, Python 3.8.2 e django-debug-toolbar 2.2.
{: .versoes }

<a href="https://youtu.be/T23bEwMhD6A">
    <img src="../.gitbook/assets/youtube.png">
</a>

Documentação: [https://django-debug-toolbar.readthedocs.io/en/latest/](https://django-debug-toolbar.readthedocs.io/en/latest/)

O Django Debug Toolbar é uma barra lateral que aparece nas páginas do seu projeto durante o desenvolvimento e mostra o que aconteceu no request e no response: quantas queries SQL foram feitas e quanto tempo cada uma levou, quais templates foram renderizados, as configurações do `settings`, os headers, o tempo de CPU, os arquivos estáticos e mais. É a ferramenta mais prática para descobrir por que uma página está lenta.

Neste tutorial vamos criar um projeto, instalar e configurar o Debug Toolbar e ver os painéis funcionando no Admin.

## Pré-requisitos

* Python 3 e um projeto Django. No vídeo, o projeto é criado com o boilerplate simples da [Dica 1](001-django-boilerplate.md).

## Criando o projeto

Gist do boilerplate: [https://gist.github.com/rg3915/b363f5c4a998f42901705b23ccf4b8e8](https://gist.github.com/rg3915/b363f5c4a998f42901705b23ccf4b8e8)

```bash
cd /tmp
mkdir dica08
cd dica08

curl https://gist.githubusercontent.com/rg3915/b363f5c4a998f42901705b23ccf4b8e8/raw/5d0d1cc46d3a52bef6cd73d9d476140ad445be9e/boilerplatesimple.sh -o boilerplatesimple.sh

source boilerplatesimple.sh
```

O script cria a virtualenv `.venv` (e já a deixa ativa), instala o Django 2.2.13, cria o projeto `myproject` com o app `core`, roda as migrações e pergunta se você quer criar o superusuário `admin`. Responda `y` e escolha uma senha, porque vamos usar o Admin para ver a barra.

## Instalação

```bash
pip install django-debug-toolbar
```

```
Collecting django-debug-toolbar
  Using cached django_debug_toolbar-2.2-py3-none-any.whl (198 kB)
Requirement already satisfied: Django>=1.11 in ./.venv/lib/python3.8/site-packages (from django-debug-toolbar) (2.2.13)
Requirement already satisfied: sqlparse>=0.2.0 in ./.venv/lib/python3.8/site-packages (from django-debug-toolbar) (0.3.1)
...
Successfully installed django-debug-toolbar-2.2
```

## Configurando o `settings.py`

São quatro ajustes no `settings.py`.

**1. `INSTALLED_APPS`**: acrescente `'debug_toolbar'`, depois do `'django.contrib.staticfiles'` (a barra usa arquivos estáticos próprios: CSS e JavaScript).

```python
# myproject/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'django_extensions',
    'myproject.core'
]
```

**2. `INTERNAL_IPS`**: a barra só aparece para os IPs listados aqui. Para o desenvolvimento local, basta o `127.0.0.1`. Se precisar, você pode acrescentar outros IPs.

```python
# myproject/settings.py
INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]
```

**3. `MIDDLEWARE`**: acrescente o `DebugToolbarMiddleware`. No vídeo ele foi colocado **por último**, depois de todos os outros.

```python
# myproject/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
```

> A documentação recomenda colocar o middleware o mais cedo possível na lista, mas depois de qualquer middleware que altere o conteúdo da resposta, como o `GZipMiddleware`. Neste projeto não há nenhum, então funciona nas duas posições.

**4. `STATIC_URL`**: confira se ele está definido (o `startproject` já cria):

```python
# myproject/settings.py
STATIC_URL = '/static/'
```

## Configurando o `urls.py`

O Debug Toolbar tem as suas próprias URLs (é por elas que os painéis carregam os detalhes). Elas só devem existir com `DEBUG = True`:

```python
# myproject/urls.py
from django.conf import settings
from django.urls import include, path
from django.contrib import admin


urlpatterns = [
    path('', include('myproject.core.urls', namespace='core')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

* `from django.conf import settings`: para ler o `DEBUG`.
* `import debug_toolbar` fica dentro do `if`, então em produção (`DEBUG = False`) a lib nem precisa ser importada.
* As URLs `__debug__/` são colocadas **antes** das outras.

## Rodando

```bash
python manage.py runserver
```

Abra `http://localhost:8000`. O projeto ainda não tem nenhuma página na raiz, então aparece o "Page not found (404)" do Django, mas a barra já aparece no lado direito, com os painéis **Versions** (Django 2.2.13), **Time**, **Settings**, **Headers**, **Request** e outros. Repare que a lista de URLs da página de erro já mostra o `__debug__/`.

> A barra só é injetada em páginas HTML que tenham a tag `</body>`, e só quando o `DEBUG` é `True` e o seu IP está no `INTERNAL_IPS`.

Agora entre em `http://localhost:8000/admin/` e faça login com o usuário `admin`. Com a barra aberta, clique nos painéis:

* **SQL**: as queries feitas no request ("SQL queries from 1 connection"), o tempo de cada uma, a linha do código que gerou cada query e os botões **Sel** e **Expl** para rodar o `SELECT` ou o `EXPLAIN` da query.
* **Templates**: os templates renderizados (`admin/index.html`, `admin/base_site.html`, `admin/base.html`) e os context processors.
* **Time**: tempo de CPU e tempo total do request.
* **Settings**: todas as configurações do projeto.
* **Headers** e **Request**: os cabeçalhos HTTP, a view chamada, os cookies e a sessão.
* **Static files**: os arquivos estáticos usados na página.

O botão **Hide »** esconde a barra (fica só uma aba pequena no canto da tela para abri-la de novo).

## Conclusão

Com quatro ajustes no `settings.py` e um bloco no `urls.py`, você passa a ver, em cada página, quantas queries foram feitas e quanto tempo levaram. É a forma mais rápida de encontrar problemas como o N+1 (veja a [dica sobre N+1](117-n-mais-1-django-61.md)).

Observação: em versões mais novas do django-debug-toolbar, o `urls.py` pode usar `path('__debug__/', include('debug_toolbar.urls'))` e, a partir da versão 4.x, existe o atalho `debug_toolbar_urls()`. Para reproduzir o vídeo, use a versão 2.2.
