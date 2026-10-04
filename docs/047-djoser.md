# Dica 47 - DRF: djoser - Django REST framework

**Versões usadas no vídeo:** Django 3.2.7, Django REST framework 3.12.4, djoser 2.1.0, drf-yasg 1.20.0 e Python 3.8.10.
{: .versoes }

<a href="https://youtu.be/HUtG2Eg47Gw">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/drf-example](https://github.com/rg3915/drf-example)

[https://djoser.readthedocs.io/en/latest/](https://djoser.readthedocs.io/en/latest/)

O **djoser** é uma biblioteca que faz toda a parte de autenticação de usuários de uma API em Django REST framework: cadastro de usuário, login e logout por token, dados do usuário logado, troca e reset de senha e de username, ativação de conta e, se quiser, JWT (que veremos numa próxima dica). Você só configura e ganha os endpoints prontos.

Neste tutorial vamos acrescentar o djoser ao projeto das dicas [45](045-drf-scaffold.md) e [46](046-drf-yasg.md) e testar os endpoints pelo **Postman**, pelo **Swagger** e com **curl**.

## Pré-requisitos

O projeto é o do repositório [drf-example](https://github.com/rg3915/drf-example): um projeto `backend` com os apps `blog`, `product` e `ecommerce` (gerados com o `dr_scaffold`) e a documentação com o drf-yasg. Ative o ambiente virtual do projeto antes de começar.

## Os endpoints do djoser

Na seção **Getting started** da documentação está a lista de endpoints que o djoser oferece:

* `/users/`
* `/users/me/`
* `/users/confirm/`
* `/users/resend_activation/`
* `/users/set_password/`
* `/users/reset_password/`
* `/users/reset_password_confirm/`
* `/users/set_username/`
* `/users/reset_username/`
* `/users/reset_username_confirm/`
* `/token/login/` (Token Based Authentication)
* `/token/logout/` (Token Based Authentication)
* `/jwt/create/` (JSON Web Token Authentication)
* `/jwt/refresh/` (JSON Web Token Authentication)
* `/jwt/verify/` (JSON Web Token Authentication)

## Instalando

```bash
pip install -U djoser
pip freeze | grep djoser >> requirements.txt
```

O `pip freeze | grep djoser` mostra `djoser==2.1.0`. Repare que o djoser instala junto outras dependências, como o `djangorestframework-simplejwt`, o `social-auth-app-django` e o `django-templated-mail`.

No vídeo, o `requirements.txt` foi arrumado e ficou assim:

```
# requirements.txt
click==8.0.*
django-extensions
Django==3.2.*
djangorestframework==3.12.*
djoser==2.1.*
dr-scaffold==1.4.*
drf-yasg==1.20.*
python-decouple
```

Se faltar alguma biblioteca no seu ambiente (no vídeo deu `ModuleNotFoundError: No module named 'decouple'` e depois `No module named 'dr_scaffold'`), instale tudo de uma vez:

```bash
pip install -r requirements.txt
```

## Configurando o settings.py

Configure `INSTALLED_APPS`. São três novidades:

* `rest_framework.authtoken`: o app de tokens do Django REST framework, que cria a tabela de tokens (por isso precisa rodar o `migrate`);
* `django_extensions`: usado aqui para o comando `show_urls`;
* `djoser`.

```python
# backend/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd apps
    'rest_framework',
    'rest_framework.authtoken',  # <-- rode ./manage.py migrate
    'django_extensions',
    'dr_scaffold',
    'drf_yasg',
    'djoser',  # <--
    # my apps
    'blog',
    'product',
    'ecommerce',
]
```

E, logo abaixo, a configuração do Django REST framework. Como pede a seção **Authentication Backends** da documentação do djoser, acrescentamos o `TokenAuthentication`. E, com o `IsAuthenticated` como permissão padrão, toda a API passa a exigir autenticação:

```python
# backend/settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
```

(Mais adiante, para o Swagger, vamos acrescentar também o `BasicAuthentication`.)

## Configurando o urls.py

No `backend/urls.py`, acrescente um bloco para o djoser, entre o `urlpatterns` principal e o bloco do Swagger. O `djoser.urls` traz os endpoints de usuário e o `djoser.urls.authtoken` traz o login e o logout por token. A documentação usa `auth/` como prefixo; aqui usamos `api/v1/` e `api/v1/auth/`:

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

# djoser
urlpatterns += [
    path('api/v1/', include('djoser.urls')),
    path('api/v1/auth/', include('djoser.urls.authtoken')),
]

# swagger
urlpatterns += [
   url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),  # noqa E501
   url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # noqa E501
   url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # noqa E501
]
```

## Migrations e rotas

```bash
python manage.py migrate
```

Saída (trecho):

```
Running migrations:
  Applying authtoken.0001_initial... OK
  Applying authtoken.0002_auto_20160226_1747... OK
  Applying authtoken.0003_tokenproxy... OK
```

Para ver todas as rotas que o djoser criou, use o `show_urls` do django-extensions:

```bash
python manage.py show_urls
```

Saída (só as rotas do djoser, sem as variações com `.<format>`):

```
/api/v1/                               rest_framework.routers.APIRootView   api-root
/api/v1/auth/token/login/              djoser.views.TokenCreateView         login
/api/v1/auth/token/logout/             djoser.views.TokenDestroyView        logout
/api/v1/users/                         djoser.views.UserViewSet             user-list
/api/v1/users/<id>/                    djoser.views.UserViewSet             user-detail
/api/v1/users/activation/              djoser.views.UserViewSet             user-activation
/api/v1/users/me/                      djoser.views.UserViewSet             user-me
/api/v1/users/resend_activation/       djoser.views.UserViewSet             user-resend-activation
/api/v1/users/reset_password/          djoser.views.UserViewSet             user-reset-password
/api/v1/users/reset_password_confirm/  djoser.views.UserViewSet             user-reset-password-confirm
/api/v1/users/reset_username/          djoser.views.UserViewSet             user-reset-username
/api/v1/users/reset_username_confirm/  djoser.views.UserViewSet             user-reset-username-confirm
/api/v1/users/set_password/            djoser.views.UserViewSet             user-set-password
/api/v1/users/set_username/            djoser.views.UserViewSet             user-set-username
```

Rode o servidor:

```bash
python manage.py runserver
```

## Gerando um token

Agora a API exige autenticação. Um `GET` em `http://localhost:8000/api/v1/users/` sem token devolve `401 Unauthorized`:

```json
{
    "detail": "Authentication credentials were not provided."
}
```

Precisamos de um token. Há dois jeitos:

* pelo Admin: em **Auth Token > Tokens > Add token**, escolha o usuário (por exemplo, `admin`) e salve;
* pelo terminal, com o comando do Django REST framework:

```bash
python manage.py drf_create_token admin
```

```
Generated token 24ef68dcc57baa747b46ad10300090003535753f for user admin
```

O seu token será outro. Ele aparece também no Admin, em **Auth Token > Tokens**.

## Testando com o Postman

* **Listar usuários (com token).** `GET http://localhost:8000/api/v1/users/`. Na aba **Headers**, acrescente a chave `Authorization` com o valor `Token <o seu token>` (a palavra `Token`, com T maiúsculo, um espaço e o token). Agora a resposta é `200 OK`, com a lista de usuários (`email`, `id` e `username` de cada um).
* **Criar usuário (sem token).** `POST http://localhost:8000/api/v1/users/`. Para criar usuário não é preciso autenticação. Em **Body > raw > JSON**:

```json
{
    "username": "regis",
    "password": "demodemo"
}
```

A resposta é `201 Created`, com o `email` (vazio), o `username` e o `id` do novo usuário. Repare que, ao criar o usuário, o djoser **não** cria um token para ele.

* **Login.** `POST http://localhost:8000/api/v1/auth/token/login/`, com o mesmo corpo (`username` e `password`). A resposta é `200 OK` com o token, que agora aparece no Admin para o usuário `regis`:

```json
{
    "auth_token": "07a1deca4342b4af9a1943ece79d4bb03da9c95a"
}
```

* **Dados do usuário logado.** `GET http://localhost:8000/api/v1/users/me/`. Sem token, dá `401`. Com o header `Authorization: Token <token do regis>`, retorna os dados dele:

```json
{
    "email": "",
    "id": 10,
    "username": "regis"
}
```

* **Logout.** `POST http://localhost:8000/api/v1/auth/token/logout/` (tem que ser `POST`), com o header `Authorization`. O token do `regis` é apagado (some do Admin).

Quando faz o logout ele apaga o token, e só gera um novo quando você fizer login novamente.

## Testando com o Swagger

Em `http://localhost:8000/swagger/`, os endpoints do djoser aparecem no grupo `api`. Em `POST /api/v1/users/`, **Try it out**, preencha o corpo (dá para mandar o e-mail também) e **Execute**:

```json
{
  "email": "huguinho@email.com",
  "username": "huguinho",
  "password": "demodemo"
}
```

A resposta é `201`. Mas, ao tentar `GET /api/v1/users/`, o Swagger devolve `401` ("Authentication credentials were not provided."), porque ele não tem como mandar o token. Para resolver, acrescente o `BasicAuthentication` no `settings.py`:

```python
# backend/settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
```

Recarregue a página do Swagger, clique em **Authorize**, preencha usuário e senha (no vídeo, o `admin`) em **Basic authorization** e confirme. Agora o `GET /api/v1/users/` retorna `200` com a lista de usuários, e o `GET /api/v1/users/me/` retorna os dados do usuário com que você fez o login no Swagger. Todos os outros endpoints também podem ser usados por ali.

## Exemplos com curl

Com o servidor rodando, dá para fazer tudo pelo terminal.

```bash
# Cria novo usuário
curl -X POST http://127.0.0.1:8000/api/v1/users/ \
--data 'username=djoser&password=api127rg'
```

```json
{"email":"","username":"djoser","id":12}
```

```bash
# Login
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/login/ \
--data 'username=djoser&password=api127rg'
```

```json
{"auth_token":"ca635ecda0fe66998a512e9f67aa6ef08d15abf7"}
```

```bash
# Informações do usuário
curl -X GET \
http://127.0.0.1:8000/api/v1/users/me/ \
-H 'Authorization: Token ca635ecda0fe66998a512e9f67aa6ef08d15abf7'  # o seu será um novo
```

```json
{"email":"","id":12,"username":"djoser"}
```

```bash
# Logout
curl -X POST \
http://127.0.0.1:8000/api/v1/auth/token/logout/ \
-H 'Authorization: Token ca635ecda0fe66998a512e9f67aa6ef08d15abf7'  # o seu será um novo
```

O logout não devolve nada no corpo; o servidor responde `204 No Content` e o token é apagado. Se tentar o `users/me/` de novo com o mesmo token, a resposta é `{"detail":"Invalid token."}`.

Pronto: com poucas linhas de configuração, o djoser entrega cadastro, login, logout e dados do usuário, e os mesmos endpoints podem ser usados pelo Postman, pelo Swagger ou por qualquer cliente HTTP.
