# 12 - Fale conosco com formulário para enviar mensagem

Criar app `crm`

```
cd backend
python ../manage.py startapp crm
cd ..

touch backend/crm/forms.py
touch backend/crm/urls.py
```

Edite `crm/apps.py`

```python
# crm/apps.py
from django.apps import AppConfig


class CrmConfig(AppConfig):
    ...
    name = 'backend.crm'
```

Edite `settings.py`

```python
# settings.py
INSTALLED_APPS = [
    ...
    # minhas apps
    'backend.core',
    'backend.crm',
]
```

Edite `backend/urls.py`

```python
# backend/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    ...
    path('crm/', include('backend.crm.urls', namespace='crm')),  # noqa E501
    ...
]
```

Edite `crm/urls.py`

```python
# crm/urls.py
from django.urls import path

from backend.crm import views as v

app_name = 'crm'


urlpatterns = [
    path('contact/', v.send_contact, name='send_contact'),  # noqa E501
]
```

Edite `crm/forms.py`

```python
# crm/forms.py
from django import forms


class ContactForm(forms.Form):
    name = forms.CharField('nome', max_length=255)
    email = forms.EmailField('email',)  # sender
    title = forms.CharField('título', max_length=100)  # subject
    body = forms.CharField(widget=forms.Textarea)  # message
```

Edite `crm/views.py`


# crm/views.py`
```python
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from .forms import ContactForm


@require_http_methods(['POST'])
def send_contact(request):
    form = ContactForm(request.POST or None)

    if form.is_valid():
        subject = form.cleaned_data.get('title')
        message = form.cleaned_data.get('body')
        sender = form.cleaned_data.get('email')
        send_mail(
            subject,
            message,
            sender,
            ['localhost'],
            fail_silently=False,
        )
        return redirect('core:index')
```

Edite `index.html`

```html
<form action="{\% url 'crm:send_contact' %}" method="POST">
```