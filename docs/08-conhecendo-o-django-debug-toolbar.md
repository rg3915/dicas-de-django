# 8 - Conhecendo o Django Debug Toolbar

<a href="https://youtu.be/T23bEwMhD6A">
    <img src="../.gitbook/assets/youtube.png">
</a>


https://django-debug-toolbar.readthedocs.io/en/latest/

```
pip install django-debug-toolbar
```

#### Configurando o `settings.py`

```python
INSTALLED_APPS = [
    # ...
    'django.contrib.staticfiles',
    # ...
    'debug_toolbar',
]

MIDDLEWARE = [
    # ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Deve estar por último.
]

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

STATIC_URL = '/static/'
```

#### Configurando o `urls.py`

```python
from django.conf import settings
from django.urls import include, path

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```
