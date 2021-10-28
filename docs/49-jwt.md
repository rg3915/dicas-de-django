# 49 - DRF: Autenticação via JWT com djoser - Django REST framework

<a href="https://youtu.be/dOomllYxj9E">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/drf-example](https://github.com/rg3915/drf-example)

[https://djoser.readthedocs.io/en/latest/jwt_endpoints.html](https://djoser.readthedocs.io/en/latest/jwt_endpoints.html)

JSON Web Token Authentication: [https://djoser.readthedocs.io/en/latest/authentication_backends.html#json-web-token-authentication](https://djoser.readthedocs.io/en/latest/authentication_backends.html#json-web-token-authentication)


`pip install djoser djangorestframework-simplejwt`

![jwt.png](../img/jwt.png)


```python
# settings.py
from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # <--
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}


SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),  # na doc está JWT mas pode mudar pra Bearer.
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    # "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}
```

```python
# urls.py
urlpatterns += [
    path('api/v1/', include('djoser.urls')),
    path('api/v1/auth/', include('djoser.urls.authtoken')),
    path('api/v1/auth/', include('djoser.urls.jwt')),  # <--
]
```

```python
# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from product.models import Product
from product.serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)  # <--
```

```
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/login/ --data 'username=admin&password=d'

curl -X POST http://127.0.0.1:8000/api/v1/auth/jwt/create/ --data 'username=admin&password=d'
```


Pegar access

```
# atualizar
curl -X POST \
http://127.0.0.1:8000/api/v1/auth/jwt/refresh/ \
-H 'Content-Type: application/json' \
--data '{"refresh": ""}'

curl -X GET \
http://127.0.0.1:8000/product/products/ \
-H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLC...'
```

### Consumindo a API com Python

```python
'''
Usage:

python consumer.py -u usuario -p senha
'''
from pprint import pprint
from typing import Dict

import click
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = 'http://localhost:8000/api/v1/'


def fetch_token(session, endpoint, username, password):
    '''
    Faz autenticação do usuário.
    '''
    # headers = {'Content-type': 'application/json'}  # Não precisou
    data = {
        'username': username,
        'password': password,
    }
    with session.post(
        endpoint,
        auth=HTTPBasicAuth(username, password),
        # headers=headers,  # Não precisou
        data=data
    ) as response:
        return response.json()


def get_token(username: str, password: str) -> Dict[str, str]:
    '''
    Pega o access_token do usuário logado.
    '''
    with requests.Session() as session:
        endpoint = f'{BASE_URL}auth/jwt/create/'
        response = fetch_token(session, endpoint, username, password)
        data = {
            'access_token': response['access'],
        }
        return data


def fetch(session, endpoint, access_token):
    '''
    Faz a autenticação usando JWT.
    '''
    headers = {'Authorization': f'Bearer {access_token}'}
    with session.get(endpoint, headers=headers) as response:
        return response.json()


def post_product(session, endpoint, access_token, title, price):
    '''
    Salva o produto.
    '''
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        'title': title,
        'price': price,
    }
    with session.post(endpoint, headers=headers, data=data) as response:
        print(response)
        pprint(response.json())


@click.command()
@click.option('--username', '-u', prompt='username', help='Type the username.')
@click.option('--password', '-p', prompt='password', help='Type the password.')
@click.option('--title', '-t', help='Type the title.')
@click.option('--price', '-pr', help='Type the price.')
def main(username, password, title=None, price=None):
    '''
    Consumindo a lista de produtos.
    '''
    token = get_token(username, password)
    access_token = token['access_token']
    with requests.Session() as session:
        endpoint = 'http://127.0.0.1:8000/product/products/'
        response = fetch(session, endpoint, access_token)
        pprint(response)

        if title and price:
            print(f'Salvando produto: {title}')
            post_product(session, endpoint, access_token, title, price)


if __name__ == '__main__':
    print('Produtos')
    main()

```
