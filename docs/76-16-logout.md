# Dica 16 - Logout

<a href="https://youtu.be/SPnFqVRAows">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** remova a `\` no meio das tags.

![](../.gitbook/assets/tags.png)


Edite `accounts/urls.py`

```python
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # noqa E501
    path('logout/', LogoutView.as_view(), name='logout'),  # noqa E501
]
```

Edite `core/templates/includes/nav.html`

```html
<span class="text-base font-normal text-gray-500 mr-5">Olá {{ request.user.first_name }}</span>
<a href="{\% url 'logout' %}" class="text-base font-normal text-gray-500 ml-5">Sair</a>
```
