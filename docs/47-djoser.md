# 47 - DRF: djoser - Django REST framework

<a href="https://youtu.be/HUtG2Eg47Gw">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/drf-example](https://github.com/rg3915/drf-example)

https://djoser.readthedocs.io/en/latest/

```
pip install -U djoser
pip freeze | grep djoser >> requirements.txt
```



Configure `INSTALLED_APPS`

```python
INSTALLED_APPS = (
    'django.contrib.auth',
    (...),
    'rest_framework',
    'rest_framework.authtoken',  # <-- rode ./manage.py migrate
    'djoser',  # <--
    (...),
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

```

Configure `urls.py`

```python
# djoser
urlpatterns += [
    path('api/v1/', include('djoser.urls')),
    path('api/v1/auth/', include('djoser.urls.authtoken')),
]
```


```
python manage.py migrate
python manage.py drf_create_token admin

token d7643a4710c7e19915df7d5e3d82f70cb07998ba  # o seu será um novo
```

Veja no video como rodar no **Postman** e no **Swagger**.

Exemplos com curl

```
# Cria novo usuário
curl -X POST http://127.0.0.1:8000/api/v1/users/ --data 'username=djoser&password=api127rg'

# Login
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/login/ --data 'username=djoser&password=api127rg'

# Informações do usuário
curl -X GET http://127.0.0.1:8000/api/v1/users/me/ -H 'Authorization: Token d7643a4710c7e19915df7d5e3d82f70cb07998ba'  # o seu será um novo

# Logout
curl -X GET http://127.0.0.1:8000/api/v1/auth/token/logout/ -H 'Authorization: Token d7643a4710c7e19915df7d5e3d82f70cb07998ba'  # o seu será um novo
```

Quando faz o logout ele apaga o token, e só gera um novo quando você fizer login novamente.
