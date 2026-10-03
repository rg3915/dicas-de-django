# Desenvolvimento Web com Django - palestra

Publicado em 14/07/2025.

**Testado com:** Django 5.2.3 e Python 3.10 ou superior.
{: .versoes }

<a href="https://youtu.be/DGoSA9T-1Qc">
    <img src="../.gitbook/assets/youtube.png">
</a>

Palestra realizada em 26/06/2025 na Semana Tecnológica TADS 2025 no Instituto Federal do Pará, Campus Itajuba.

Esta página reproduz, em forma de tutorial, o exemplo da palestra: partimos de uma página estática, entendemos por que um framework ajuda quando entra banco de dados e construímos com Django uma pequena loja com lista de produtos, painel de admin, views, urls e templates. No final você terá a aplicação rodando e entenderá o padrão MTV.

## Pré-requisitos

* Python 3.10 ou mais recente (a palestra usou o Django 5.2.3).
* PostgreSQL rodando na sua máquina (pode ser via Docker, veja abaixo).
* Noções de HTML, SQL e Python (listas, dicionários, `for`, funções e classes).

## 1. Do HTML estático ao banco de dados

Um `index.html` publicado na internet já é desenvolvimento web: é uma página estática, como um blog. O Python tem "baterias inclusas", então dá para servir essa página sem instalar nada:

```bash
python -m http.server
```

O servidor sobe em `http://localhost:8000`. Se a porta estiver ocupada, o Python mostra um *traceback*. A dica é ler o traceback de baixo para cima: a última linha diz o problema (aqui, "endereço em uso").

O problema começa quando precisamos de banco de dados. Com o `sqlite3` da biblioteca padrão, fazemos tudo à mão:

```python
# exemplo_sqlite.py
import sqlite3

conn = sqlite3.connect('loja.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY,
        titulo TEXT,
        preco REAL
    )
''')

produtos = [
    ('Notebook', 3500.00),
    ('Mouse', 59.90),
    ('Headphone', 199.90),
]
cursor.executemany('INSERT INTO produtos (titulo, preco) VALUES (?, ?)', produtos)

cursor.execute('SELECT * FROM produtos')
print(cursor.fetchall())

conn.commit()
conn.close()  # nunca esqueça de fechar a conexão
```

Para PostgreSQL você trocaria para `psycopg2` (`pip install psycopg2-binary`, porta 5432, exceção `psycopg2.Error`); para MySQL, `mysql.connector` (porta 3306, exceção `mysql.connector.Error`). Cada banco tem sua biblioteca, sua conexão e suas exceções. Ficar reescrevendo isso em todo projeto tira o foco do que importa. É aí que o Django entra: ele traz ORM, admin, autenticação, rotas e templates prontos.

## 2. Ambiente virtual e dependências

Cada projeto deve ter seu próprio ambiente virtual, para isolar as dependências:

```bash
mkdir loja
cd loja
python -m venv .venv
source .venv/bin/activate  # no Windows: .venv\Scripts\activate
```

Crie o `requirements.txt`, a "receita do bolo" do projeto:

```text
# requirements.txt
Django==5.2.3
django-extensions
python-decouple
psycopg2-binary
```

```bash
pip install -r requirements.txt
pip freeze
```

O `pip freeze` lista também as dependências secundárias que vieram junto.

## 3. Criando o projeto e as apps

```bash
django-admin startproject apps .
cd apps
python ../manage.py startapp core
python ../manage.py startapp produto
cd ..
```

O ponto no final do `startproject` faz o `manage.py` ficar na pasta principal. Eu chamo o projeto de `apps` e coloco as apps dentro dele: `core` é a app principal e `produto` cuida dos produtos. Digite `python manage.py` sozinho para ver todos os comandos disponíveis e `python manage.py startapp --help` para a ajuda de um comando.

A estrutura fica assim:

```text
loja/
├── apps/
│   ├── core/
│   ├── produto/
│   ├── settings.py
│   └── urls.py
├── .env
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

Como as apps estão dentro de `apps/`, ajuste o `name` em cada `apps.py`:

```python
# apps/core/apps.py
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
```

```python
# apps/produto/apps.py
from django.apps import AppConfig


class ProdutoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.produto'
```

## 4. Settings: segredos fora do código

A `SECRET_KEY` é um dado sensível e nunca deve ir para o Git. Com o **python-decouple** lemos esse valor de um arquivo `.env`. Os trechos que mudam no `settings.py` são estes:

```python
# apps/settings.py
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # apps de terceiros
    'django_extensions',
    # minhas apps
    'apps.core',
    'apps.produto',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', 'dicas_de_django'),
        'USER': config('POSTGRES_USER', 'postgres'),
        'PASSWORD': config('POSTGRES_PASSWORD', 'postgres'),
        'HOST': config('DB_HOST', 'localhost'),
        'PORT': config('DB_PORT', 5432, cast=int),
    }
}

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'
```

O segundo argumento de `config` é o valor padrão, usado quando a variável não existe no `.env`. O `cast=int` converte a porta para inteiro. Para trocar de PostgreSQL para MySQL, MariaDB ou Oracle, basicamente muda o `ENGINE`; o resto do código continua igual.

```bash
# .env
SECRET_KEY=troque-por-uma-chave-aleatoria
POSTGRES_DB=dicas_de_django
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

E o `.gitignore` garante que nada disso suba para o repositório:

```text
# .gitignore
.env
.venv/
__pycache__/
*.sqlite3
```

Se você não tem o PostgreSQL instalado, suba um com Docker:

```bash
docker run -d --name loja-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=dicas_de_django -p 5432:5432 postgres:16-alpine
```

Use o mesmo banco em desenvolvimento e em produção. O SQLite, por exemplo, aceita 101 caracteres num `CharField(max_length=100)`; o PostgreSQL recusa. Se você só descobre isso em produção, já é tarde.

## 5. migrate e createsuperuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

O `migrate` já aplica as migrações que vêm de brinde: usuários, grupos e permissões, entre outras. O `createsuperuser` pede usuário (eu usei `admin`), e-mail (opcional) e senha. Nada de `INSERT` manual.

## 6. O ORM no shell

O `python manage.py shell` do Django 5.2 já importa os models automaticamente (use `-v 2` para ver a lista). O `shell_plus` do django-extensions importa ainda mais coisas, como `Sum`, `Max` e `Count`:

```bash
python manage.py shell_plus
```

```python
>>> users = User.objects.all()          # SELECT * FROM auth_user
>>> users.count()
2
>>> User.objects.filter(username='admin')  # WHERE username = 'admin'
<QuerySet [<User: admin>]>
>>> for user in users:
...     print(user.id, user.username, user.password)
```

O campo `password` mostra apenas um hash (PBKDF2 com SHA256). Não existe como "descobrir a senha" de alguém no banco, nem a sua. Para trocar a senha, use `get`, que retorna um único objeto (e levanta erro se não encontrar nenhum):

```python
>>> user = User.objects.get(username='admin')
>>> user.set_password('demo')
>>> user.save()
```

Isso é o ORM (mapeamento objeto-relacional): você trabalha com objetos Python e o Django gera o SQL certo para cada banco.

## 7. O model Produto

```python
# apps/produto/models.py
from django.db import models


class Produto(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)
    sku = models.CharField(max_length=8, unique=True)
    preco = models.DecimalField(max_digits=9, decimal_places=2)

    class Meta:
        ordering = ('titulo',)

    def __str__(self):
        return self.titulo
```

* `CharField(max_length=100)` equivale a um `varchar(100)`. Sem `null`/`blank`, o preenchimento é obrigatório.
* `TextField` não precisa de tamanho; com `null=True, blank=True` fica opcional.
* `sku` é o código do produto, com `unique=True`: dois produtos não podem ter o mesmo código.
* Dinheiro é sempre `DecimalField`, nunca `FloatField`. `max_digits=9` conta todos os dígitos, inclusive os 2 depois da vírgula, então o máximo é 9.999.999,99.
* `ordering = ('titulo',)` devolve os produtos em ordem alfabética.

Gere e aplique a migração:

```bash
python manage.py makemigrations
python manage.py migrate
```

O `makemigrations` cria o arquivo `apps/produto/migrations/0001_initial.py`; o `migrate` executa o `CREATE TABLE` no banco.

## 8. Admin

```python
# apps/produto/admin.py
from django.contrib import admin

from .models import Produto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'sku', 'preco')
    search_fields = ('titulo', 'sku')
```

```bash
python manage.py runserver
```

Acesse `http://localhost:8000/admin/` e você tem o CRUD completo de produtos e usuários, além de grupos e permissões (dá para criar um grupo que adiciona, edita e visualiza produtos, mas não exclui). O `runserver` é só para desenvolvimento. E o admin é para você e para o dono do projeto, não para o usuário final: nele é possível excluir usuários e trocar senhas.

## 9. Views

No Django, quem faz o papel de controlador é o `views.py`. Uma view recebe o `request` (a requisição do navegador) e devolve uma resposta.

```python
# apps/core/views.py
from django.shortcuts import render


def index(request):
    template_name = 'index.html'
    return render(request, template_name)
```

```python
# apps/produto/views.py
from django.shortcuts import render

from .models import Produto


def produto_list(request):
    template_name = 'produto/produto_list.html'
    object_list = Produto.objects.all()
    context = {'object_list': object_list}
    return render(request, template_name, context)
```

O `context` é um dicionário: a chave `object_list` é o nome que o template vai usar. Eu padronizo como `object_list` para conseguir reaproveitar templates entre apps.

## 10. URLs

São três arquivos: o principal e um por app.

```python
# apps/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('apps.core.urls')),
    path('produto/', include('apps.produto.urls')),
    path('admin/', admin.site.urls),
]
```

```python
# apps/core/urls.py
from django.urls import path

from apps.core import views as v

app_name = 'core'

urlpatterns = [
    path('', v.index, name='index'),
]
```

```python
# apps/produto/urls.py
from django.urls import path

from apps.produto import views as v

app_name = 'produto'

urlpatterns = [
    path('', v.produto_list, name='produto_list'),
]
```

O `app_name` mais o `name` formam a rota nomeada `produto:produto_list`. Para ver todas as rotas do projeto, use o django-extensions:

```bash
python manage.py show_urls
```

```text
/           apps.core.views.index             core:index
/produto/   apps.produto.views.produto_list   produto:produto_list
```

Em um projeto grande que você acabou de pegar, comece por aqui: da URL você chega na view, e da view chega no model.

## 11. Templates

O Django tem sua própria linguagem de templates, parecida com o Jinja2. Crie as pastas `apps/core/templates/includes/` e `apps/produto/templates/produto/`.

```html
<!-- apps/core/templates/base.html -->
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Loja</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
</head>
<body>
  <main class="container">
    {% include "includes/menu.html" %}
    {% block content %}{% endblock content %}
  </main>
</body>
</html>
```

```html
<!-- apps/core/templates/includes/menu.html -->
<nav>
  <ul>
    <li><strong>Loja</strong></li>
  </ul>
  <ul>
    <li><a href="{% url 'core:index' %}">Início</a></li>
    <li><a href="{% url 'produto:produto_list' %}">Produtos</a></li>
  </ul>
</nav>
```

```html
<!-- apps/core/templates/index.html -->
{% extends "base.html" %}

{% block content %}
  <h1>Minha landing page</h1>
{% endblock content %}
```

```html
<!-- apps/produto/templates/produto/produto_list.html -->
{% extends "base.html" %}

{% block content %}
  <h1>Produtos</h1>
  <table>
    <thead>
      <tr>
        <th>Título</th>
        <th>SKU</th>
        <th>Preço</th>
      </tr>
    </thead>
    <tbody>
      {% for object in object_list %}
        <tr>
          <td>{{ object.titulo }}</td>
          <td>{{ object.sku }}</td>
          <td>{{ object.preco }}</td>
        </tr>
      {% empty %}
        <tr>
          <td colspan="3">Nenhum produto cadastrado.</td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
{% endblock content %}
```

* `{% include %}` insere um pedaço de HTML (o menu).
* `{% block content %}` é um espaço que cada página preenche.
* `{% extends "base.html" %}` herda tudo do base, inclusive o menu. O que se repete em todas as páginas vai no base.
* `{% url 'produto:produto_list' %}` gera o endereço a partir do nome da rota. Se um dia `/produto/` virar `/product/`, você muda só o `urls.py`.
* `{{ object.titulo }}` exibe o atributo de cada item de `object_list`, o mesmo nome da chave do `context`.

O CSS vem do [Pico CSS](https://picocss.com/), que estiliza o HTML sem precisar de classes.

## 12. Rodando e testando

```bash
python manage.py runserver
```

Cadastre alguns produtos pelo admin ou pelo shell:

```python
>>> Produto.objects.create(titulo='Notebook', sku='NTB00001', preco='3500.00')
>>> Produto.objects.create(titulo='Mouse', sku='MOU00001', preco='59.90')
>>> Produto.objects.all()
```

Acesse `http://localhost:8000/` (landing page) e `http://localhost:8000/produto/` (tabela de produtos, em ordem alfabética, com o menu herdado do base).

## 13. O padrão MTV

O Django segue o MTV, parecido com o MVC:

* **Model**: os dados (a classe `Produto`).
* **View**: o controlador; recebe a URL, busca os dados e escolhe o template.
* **Template**: a apresentação (HTML, mas pode ser TXT, PDF etc.).

O caminho de uma requisição é: o navegador acessa uma URL, o `urls.py` encontra a view, a view pede os dados ao model, o model consulta o banco pelo ORM e devolve objetos, a view renderiza o template e o resultado aparece na tela.

## Para continuar

* Documentação oficial: [https://docs.djangoproject.com/en/5.2/](https://docs.djangoproject.com/en/5.2/)
* Tutorial oficial: [https://docs.djangoproject.com/en/5.2/intro/tutorial01/](https://docs.djangoproject.com/en/5.2/intro/tutorial01/)
* python-decouple: [https://github.com/HBNetwork/python-decouple](https://github.com/HBNetwork/python-decouple)
* django-extensions: [https://django-extensions.readthedocs.io/](https://django-extensions.readthedocs.io/)

Livros citados na palestra: *Django 3 by Example*, de Antonio Melé, *Django Admin Cookbook* e *Two Scoops of Django*.

Aprender Django parece muito no começo porque junta várias disciplinas: HTML, banco de dados e Python. Estude uma parte de cada vez e depois junte tudo.
