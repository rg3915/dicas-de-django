# 9 - Escondendo suas senhas python-decouple

<a href="https://youtu.be/eOwN7e0QBXo">
    <img src="../.gitbook/assets/youtube.png">
</a>

[Video do Henrique Bastos na Live de Python #97](https://www.youtube.com/watch?v=zYJGpLw5Wv4)

<a href="https://www.youtube.com/watch?v=zYJGpLw5Wv4">
    <img src="../.gitbook/assets/youtube.png">
</a>


https://github.com/henriquebastos/python-decouple


```
pip install python-decouple
```

Crie um arquivo `.env` com o seguinte conteúdo (de exemplo)

```
DEBUG=True
SECRET_KEY=c9^3g^bn6wgo8tabf*dl$@vx@m-!9ux%*9)88qnun&hk++sa90
ALLOWED_HOSTS=127.0.0.1,.localhost
POSTGRES_DB=mydb
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypass
DB_HOST=localhost

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=

# console ou smtp
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

repare que não deve haver espaços e nem aspas.

E em `settings.py` faça

```python
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())

EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('DB_HOST', 'localhost'),
        'PORT': '5432',
    }
}
```
