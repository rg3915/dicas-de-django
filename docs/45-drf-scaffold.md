# 45 - DRF: Scaffold django apis - Django REST framework

<a href="https://youtu.be/UOW0CaFayFo">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: https://github.com/rg3915/drf-example

https://github.com/Abdenasser/dr_scaffold

https://www.abdenasser.com/scaffold-django-apis


dr-scaffold é uma lib para criar models e uma API simples em Django REST framework.


### Experimentando e criando um projeto do zero

```
python -m venv .venv
source .venv/bin/activate
pip install dr-scaffold djangorestframework django-extensions python-decouple
```

Crie um arquivo `.env`

```
cat << EOF > .env
SECRET_KEY=my-super-secret-key-dev-only
EOF
```


Crie um novo projeto.

```
django-admin startproject backend .
```

Edite `settings.py`

```python
# settings.py

from decouple import config

SECRET_KEY = config('SECRET_KEY')

INSTALLED_APPS = [
    ...
    'rest_framework',
    'dr_scaffold',
]
```


#### Exemplo 1

Rodando o comando `dr_scaffold`

```
python manage.py dr_scaffold blog Author name:charfield

python manage.py dr_scaffold blog Post body:textfield author:foreignkey:Author
```

Edite `settings.py`

```python
# settings.py
INSTALLED_APPS = [
    ...
    'rest_framework',
    'dr_scaffold',
    'blog',  # <--
]
```

Edite `urls.py`

```python
# urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('blog/', include('blog.urls')),
    path('admin/', admin.site.urls),
]
```

```
python manage.py makemigrations
python manage.py migrate
```


#### Exemplo 2


```
python manage.py dr_scaffold product Product title:charfield price:decimalfield

python manage.py dr_scaffold ecommerce Order nf:charfield

python manage.py dr_scaffold ecommerce OrderItems \
order:foreignkey:Order \
product:foreignkey:Product \
quantity:integerfield \
price:decimalfield
```

Edite `settings.py`

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'dr_scaffold',
    'blog',  # <--
    'product',  # <--
    'ecommerce',  # <--
]

```

Edite `urls.py`

```python
...
path('product/', include('product.urls')),
path('ecommerce/', include('ecommerce.urls')),
...
```

Não se esqueça de editar `ecommerce/models.py`

```python
from product.models import Product
```

```
python manage.py makemigrations
python manage.py migrate
```
