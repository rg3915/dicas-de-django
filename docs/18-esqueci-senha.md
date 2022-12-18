# 18 - Esqueci a senha

https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.views.PasswordResetView

https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.views.PasswordResetDoneView


Edite `login.html`

```html
<a href="{% url 'password_reset' %}" class="text-sm text-teal-500 hover:underline ml-auto">Esqueceu a senha?</a>
```

Edite `accounts/urls.py`

```python
# accounts/urls.py
urlpatterns = [
    ...
    path('password_reset/', v.MyPasswordReset.as_view(), name='password_reset'),  # noqa E501
    path('password_reset/done/', v.MyPasswordResetDone.as_view(), name='password_reset_done'),  # noqa E501
]
```

Edite `accounts/views.py`

```python
# accounts/views.py
class MyPasswordReset(PasswordResetView):
    '''
    Requer
    registration/password_reset_form.html
    registration/password_reset_email.html
    registration/password_reset_subject.txt  Opcional
    '''
    ...


class MyPasswordResetDone(PasswordResetDoneView):
    '''
    Requer
    registration/password_reset_done.html
    '''
    ...
```

Edite `registration/password_reset_form.html`

```html
<!-- password_reset_form.html -->
{% extends "base_login.html" %}

{% block content %}
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
            Redefinição de senha
          </h2>
          <p class="text-sm font-medium text-gray-500">
            Esqueceu sua senha? Informe seu e-mail abaixo, e nós te enviaremos um e-mail com instruções para configurar uma nova.
          </p>
          <form class="mt-8 space-y-6" action="." method="POST">
            {% csrf_token %}
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
            <button type="submit" class="text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium rounded-lg text-base px-5 py-3 w-full sm:w-auto text-center">Enviar</button>
            <div class="text-sm font-medium text-gray-500">
              Não cadastrado? <a href="{% url 'signup' %}" class="text-teal-500 hover:underline">Criar conta</a>
            </div>
          </form>
        </div>
      </div>
    </div>
  </main>

{% endblock content %}
```

Edite `registration/password_reset_email.html`

```html
{% autoescape off %}
  Para iniciar o processo de redefinição de senha para sua conta {{ user.get_username }}, clique no link abaixo:

  {{ protocol }}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}

  Se clicar no link acima não funcionar, por favor copie e cole a URL no navegador.

  Atenciosamente,
  Equipe Dev.
{% endautoescape %}
```

Edite `registration/password_reset_done.html`

```html
<!-- password_reset_done.html -->
{% extends "base_login.html" %}

{% block content %}
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
            Redefinição de senha enviada
          </h2>
          <p class="text-sm font-medium text-gray-500">
            Nós te enviamos um e-mail com instruções para configurar sua senha, se uma conta existe com o e-mail fornecido. Você receberá a mensagem em breve.
          </p>
          <p class="text-sm font-medium text-gray-500">
            Se você não recebeu um e-mail, por favor certifique-se que você forneceu o endereço que você está cadastrado, e verifique sua pasta de spam.
          </p>
        </div>
      </div>
    </div>
  </main>
{% endblock content %}
```
