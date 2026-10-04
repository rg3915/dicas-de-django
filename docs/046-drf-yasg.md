# Dica 46 - DRF: drf-yasg - Yet another Swagger generator

**Versões usadas no vídeo:** Django 3.2.6, Django REST framework 3.12.4, drf-yasg 1.20.0 e Python 3.9.6.
{: .versoes }

<a href="https://youtu.be/TytDfV3PVFU">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/drf-example](https://github.com/rg3915/drf-example)

Doc: [https://drf-yasg.readthedocs.io/en/stable/](https://drf-yasg.readthedocs.io/en/stable/)

Doc: [https://github.com/axnsan12/drf-yasg/](https://github.com/axnsan12/drf-yasg/)

[drf-yasg](https://github.com/axnsan12/drf-yasg/) é uma outra biblioteca para gerar a documentação com Swagger e reDoc.

O nome é um acrônimo de **Yet Another Swagger Generator**. Ela lê as rotas, viewsets e serializers do Django REST framework e gera a especificação OpenAPI (Swagger 2.0) da API, com duas interfaces prontas: o **Swagger UI**, onde dá para testar cada endpoint direto no navegador, e o **ReDoc**, uma página de documentação. A própria documentação do Django REST framework, na seção de schemas, a recomenda como pacote de terceiros.

Neste tutorial vamos acrescentar o drf-yasg ao projeto da [Dica 45](045-drf-scaffold.md).

## Pré-requisitos

O projeto é o do repositório [drf-example](https://github.com/rg3915/drf-example), criado na dica anterior com o `dr_scaffold`: um projeto `backend` com os apps `blog`, `product` e `ecommerce`. Se ainda não tem, clone e rode o projeto:

```bash
git clone https://github.com/rg3915/drf-example.git
cd drf-example
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install python-decouple
python contrib/env_gen.py
python manage.py migrate
```

O `contrib/env_gen.py` gera o arquivo `.env` com a `SECRET_KEY`, que o `settings.py` lê com o python-decouple.

## Instalando

```bash
pip install -U drf-yasg

pip freeze | grep drf-yasg >> requirements.txt
```

O `pip freeze | grep drf-yasg` mostra `drf-yasg==1.20.0`, e o `>>` acrescenta essa linha no final do `requirements.txt`, que fica assim:

```
# requirements.txt
Django==3.2.6
djangorestframework==3.12.4
dr-scaffold==1.4.3
drf-yasg==1.20.0
```

## Configurando o settings.py

O drf-yasg precisa do `django.contrib.staticfiles`, que serve os arquivos CSS e JavaScript da interface do Swagger. Ele já vem no projeto. Basta acrescentar o `drf_yasg`:

```python
# backend/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # required for serving swagger ui's css/js files
    # 3rd apps
    'rest_framework',
    'dr_scaffold',
    'drf_yasg',
    # my apps
    'blog',
    'product',
    'ecommerce',
]
```

## Configurando o urls.py

O código abaixo vem do Quickstart da documentação do drf-yasg. O `get_schema_view` cria a view que gera o schema, com as informações que aparecem no topo da documentação (título, versão, descrição, termos de uso, contato e licença). O `public=True` inclui todos os endpoints, independente do usuário logado, e o `AllowAny` deixa qualquer um ver a documentação.

Como o nosso `urls.py` já tinha um `urlpatterns`, as rotas do Swagger entram num segundo bloco, concatenado com `+=`:

```python
# backend/urls.py
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('blog/', include('blog.urls')),
    path('product/', include('product.urls')),
    path('ecommerce/', include('ecommerce.urls')),
    path('admin/', admin.site.urls),
]

# swagger
urlpatterns += [
   url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),  # noqa E501
   url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # noqa E501
   url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # noqa E501
]
```

As três rotas:

* `swagger.json` e `swagger.yaml`: o schema puro, sem interface, em JSON ou YAML;
* `swagger/`: a interface do Swagger UI;
* `redoc/`: a interface do ReDoc.

O `# noqa E501` só serve para o linter não reclamar das linhas longas.

Para trocar o título "Snippets API" e os demais dados de exemplo pelos do seu projeto, edite o `openapi.Info`.

## Rodando

```bash
python manage.py migrate
python manage.py runserver
```

Abra `http://localhost:8000/swagger/`. A página mostra o título "Snippets API" com a versão v1, a descrição, os links de termos de uso e de contato, a licença e, abaixo, todos os endpoints agrupados por app: `blog`, `ecommerce` e `product`. Cada endpoint mostra o método (GET, POST, PUT, PATCH, DELETE), a rota e o nome da operação, por exemplo `GET /blog/authors/ blog_authors_list` e `POST /blog/authors/ blog_authors_create`.

Para testar, abra `POST /blog/authors/`, clique em **Try it out**, preencha o corpo da requisição e clique em **Execute**:

```json
{
  "name": "Luciano Ramalho"
}
```

A resposta é `201 Created`. Depois, em `GET /blog/authors/`, **Try it out** e **Execute** listam os autores cadastrados, já com o novo.

Em `http://localhost:8000/redoc/` fica a mesma documentação no formato do ReDoc: o menu lateral com os grupos `blog`, `ecommerce` e `product`, cada operação com o schema do corpo da requisição (por exemplo, `name`: string, até 255 caracteres, nullable), os códigos de resposta e exemplos de payload. O botão **Download** baixa a especificação OpenAPI.

E `http://localhost:8000/swagger.json` devolve o schema em JSON, útil para gerar clientes da API automaticamente.

Observação: o `django.conf.urls.url()` foi removido no Django 4.0. Em versões mais novas, use `re_path` (de `django.urls`) no lugar de `url`, com as mesmas expressões regulares.
