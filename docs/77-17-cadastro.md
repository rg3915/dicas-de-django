# Dica 17 - Cadastro de Usuários no Django

<a href="https://youtu.be/JKUYdjIfugU">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** remova a `\` no meio das tags.

![](../.gitbook/assets/tags.png)


Vamos editar os arquivos:

* accounts/templates/registration/registration_form.html
* accounts/templates/registration/password_reset_confirm.html
* accounts/templates/registration/password_reset_complete.html
* accounts/forms.py
* accounts/services.py
* accounts/tokens.py
* accounts/urls.py
* accounts/views.py

[https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.views.PasswordResetConfirmView](https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.views.PasswordResetConfirmView)

[https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.views.PasswordResetCompleteView](https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.views.PasswordResetCompleteView)


Edite `login.html`

```html
<a href="{\% url 'signup' %}" class="text-teal-500 hover:underline">Criar conta</a>
```

```
touch backend/accounts/templates/registration/registration_form.html
```

```html
<!-- registration_form.html -->
{\% extends "base_login.html" %}

{\% block content %}
  <main class="bg-gray-50">

    <div class="mx-auto md:h-screen flex flex-col justify-center items-center px-6 pt-8 pt:mt-0">
      <a href="https://demo.themesberg.com/windster/" class="text-2xl font-semibold flex justify-center items-center mb-8 lg:mb-10">
        <img src="https://demo.themesberg.com/windster/images/logo.svg" class="h-10 mr-4" alt="Windster Logo">
        <span class="self-center text-2xl font-bold whitespace-nowrap">Dicas de Django</span>
      </a>
      <!-- Card -->
      <div class="bg-white shadow rounded-lg md:mt-0 w-full sm:max-w-screen-sm xl:p-0">
        <div class="p-6 sm:p-8 lg:p-16 space-y-8">
          <h2 class="text-2xl lg:text-3xl font-bold text-gray-900">
            Crie sua conta
          </h2>
          <form class="mt-8 space-y-6" action="." method="POST">
            {\% csrf_token %}
            <div>
              <label for="id_first_name" class="text-sm font-medium text-gray-900 block mb-2">Nome</label>
              <input
                id="id_first_name"
                type="text"
                name="first_name"
                class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5"
                placeholder="Primeiro Nome"
                required
              >
            </div>
            <div>
              <label for="id_last_name" class="text-sm font-medium text-gray-900 block mb-2">Sobrenome</label>
              <input
                id="id_last_name"
                type="text"
                name="last_name"
                class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5"
                placeholder="Sobrenome"
                required
              >
            </div>
            <div>
              <label for="id_email" class="text-sm font-medium text-gray-900 block mb-2">E-mail</label>
              <input
                id="id_email"
                type="email"
                name="email"
                class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5"
                placeholder="nome@example.com"
                required
              >
            </div>
            <!-- <div>
              <label for="id_password1" class="text-sm font-medium text-gray-900 block mb-2">Senha</label>
              <input
                id="id_password1"
                type="password"
                name="password1"
                placeholder="••••••••"
                class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5"
                required
              >
            </div>
            <div>
              <label for="id_password2" class="text-sm font-medium text-gray-900 block mb-2">Confirmação da Senha</label>
              <input
                id="id_password2"
                type="password"
                name="password2"
                placeholder="••••••••"
                class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5"
                required
              >
            </div> -->
            <div class="flex items-start">
              <div class="flex items-center h-5">
                <input
                  id="remember"
                  type="checkbox"
                  name="remember"
                  aria-describedby="remember"
                  class="bg-gray-50 border-gray-300 focus:ring-3 focus:ring-cyan-200 h-4 w-4 rounded"
                >
              </div>
              <div class="text-sm ml-3">
                <label for="remember" class="font-medium text-gray-900">Eu aceito os <a href="#" class="text-teal-500 hover:underline">Termos e Condições</a></label>
              </div>
            </div>
            <button type="submit" class="text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium rounded-lg text-base px-5 py-3 w-full sm:w-auto text-center">Salvar</button>
            <div class="text-sm font-medium text-gray-500">
              Você já tem uma conta? <a href="{\% url 'login' %}" class="text-teal-500 hover:underline">Login</a>
            </div>
          </form>
        </div>
      </div>
    </div>
  </main>

{\% endblock content %}
```

Edite `accounts/forms.py`

```python
# accounts/forms.py
from django import forms

from backend.accounts.models import User


class CustomUserForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nome',
        max_length=150,
    )
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
    )
    email = forms.EmailField(
        label='E-mail',
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )

```

Edite `accounts/services.py`

```python
# accounts/services.py
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import account_activation_token


def send_mail_to_user(request, user):
    current_site = get_current_site(request)
    use_https = request.is_secure()
    subject = 'Ative sua conta.'
    message = render_to_string('email/account_activation_email.html', {
        'user': user,
        'protocol': 'https' if use_https else 'http',
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    user.email_user(subject, message)
```

Edite `accounts/tokens.py`

```python
# accounts/tokens.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            text_type(user.pk) + text_type(timestamp) + text_type(user.email)
        )


account_activation_token = AccountActivationTokenGenerator()
```

Edite `accounts/urls.py`

```python
# accounts/urls.py
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from backend.accounts import views as v

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # noqa E501
    path('logout/', LogoutView.as_view(), name='logout'),  # noqa E501
    path('register/', v.signup, name='signup'),  # noqa E501
    path('reset/<uidb64>/<token>/', v.MyPasswordResetConfirm.as_view(), name='password_reset_confirm'),  # noqa E501
    path('reset/done/', v.MyPasswordResetComplete.as_view(), name='password_reset_complete'),  # noqa E501
]
```


Instale [django-widget-tweaks](https://pypi.org/project/django-widget-tweaks/).

```
pip install django-widget-tweaks
pip freeze | grep django-widget-tweaks >> requirements.txt
```

Em `settings.py`

```python
INSTALLED_APPS = [
    ...
    # apps de terceiros
    'widget_tweaks',
]
```

Edite `accounts/templates/registration/password_reset_confirm.html`

```html
<!-- password_reset_confirm.html -->
{\% extends "base_login.html" %}
{\% load widget_tweaks %}

{\% block content %}
  <main class="bg-gray-50">
    <div class="mx-auto md:h-screen flex flex-col justify-center items-center px-6 pt-8 pt:mt-0">
      <a href="https://demo.themesberg.com/windster/" class="text-2xl font-semibold flex justify-center items-center mb-8 lg:mb-10">
        <img src="https://demo.themesberg.com/windster/images/logo.svg" class="h-10 mr-4" alt="Windster Logo">
        <span class="self-center text-2xl font-bold whitespace-nowrap">Dicas de Django</span>
      </a>
      <!-- Card -->
      <div class="bg-white shadow rounded-lg md:mt-0 w-full sm:max-w-screen-sm xl:p-0">
        <div class="p-6 sm:p-8 lg:p-16 space-y-8">
          <h2 class="text-2xl lg:text-3xl font-bold text-gray-900">
            Trocar senha
          </h2>
          <p class="text-sm font-medium text-gray-500">Digite sua nova senha.</p>
          {\% if validlink %}
            <form class="mt-8 space-y-6" action="." method="POST">
              {\% csrf_token %}
              {\% for field in form.visible_fields %}
                <div>
                  <label class="text-sm font-medium text-gray-900 block mb-2">{{ field.label }}</label>
                  {\% render_field field class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5" %}
                </div>
                <span class="text-sm font-medium text-gray-500">{{ field.help_text }}</span>
                {\% for error in field.errors %}
                  <span class="text-red-500">{{ error }}</span> <br>
                {\% endfor %}
              {\% endfor %}
              <button type="submit" class="text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium rounded-lg text-base px-5 py-3 w-full sm:w-auto text-center">Trocar senha</button>
              <div class="text-sm font-medium text-gray-500">
                Você já tem uma conta? <a href="{\% url 'login' %}" class="text-teal-500 hover:underline">Login</a>
              </div>
            </form>
          {\% else %}
            <p>O link para a recuperação de senha era inválido, possivelmente porque já foi utilizado. Por favor, solicite uma nova recuperação de senha.</p>
          {\% endif %}
        </div>
      </div>
    </div>
  </main>
{\% endblock content %}

```

Edite `accounts/templates/registration/password_reset_complete.html`

```html
<!-- password_reset_complete.html -->
{\% extends "base_login.html" %}

{\% block content %}
  <main class="bg-gray-50">
    <div class="mx-auto md:h-screen flex flex-col justify-center items-center px-6 pt-8 pt:mt-0">
      <a href="https://demo.themesberg.com/windster/" class="text-2xl font-semibold flex justify-center items-center mb-8 lg:mb-10">
        <img src="https://demo.themesberg.com/windster/images/logo.svg" class="h-10 mr-4" alt="Windster Logo">
        <span class="self-center text-2xl font-bold whitespace-nowrap">Dicas de Django</span>
      </a>
      <!-- Card -->
      <div class="bg-white shadow rounded-lg md:mt-0 w-full sm:max-w-screen-sm xl:p-0">
        <div class="p-6 sm:p-8 lg:p-16 space-y-8">
          <h2 class="text-2xl lg:text-3xl font-bold text-gray-900">
            Deu tudo certo!
          </h2>
          <p class="text-sm font-medium text-gray-500">
            Sua senha foi definida. Você pode prosseguir e se <a class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg" href="{\% url 'login' %}">autenticar</a> agora.
          </p>
        </div>
      </div>
    </div>
  </main>
{\% endblock content %}

```

Edite `accounts/views.py`

```python
# accounts/views.py
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView
)
from django.shortcuts import redirect, render

from backend.accounts.services import send_mail_to_user

from .forms import CustomUserForm


def signup(request):
    '''
    Cadastra Usuário.
    '''
    template_name = 'registration/registration_form.html'
    form = CustomUserForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            send_mail_to_user(request=request, user=user)
            return redirect('login')

    return render(request, template_name)


class MyPasswordResetConfirm(PasswordResetConfirmView):
    '''
    Requer password_reset_confirm.html
    '''

    def form_valid(self, form):
        self.user.is_active = True
        self.user.save()
        return super(MyPasswordResetConfirm, self).form_valid(form)


class MyPasswordResetComplete(PasswordResetCompleteView):
    '''
    Requer password_reset_complete.html
    '''
    ...

```
