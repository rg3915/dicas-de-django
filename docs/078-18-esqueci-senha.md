# Dica 18 - Esqueci a senha

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, Tailwind CSS e MailHog.
{: .versoes }

<a href="https://youtu.be/_mYTRnPD8PQ">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`), por causa do GitBook. Aqui elas já estão escritas do jeito certo, sem a barra.

![](../.gitbook/assets/tags.png)

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django) (branch `aula18`)

Documentação:

* [https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.views.PasswordResetView](https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.views.PasswordResetView)
* [https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.views.PasswordResetDoneView](https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.views.PasswordResetDoneView)

Nesta dica vamos implementar o **Esqueci a senha** na tela de login: o usuário clica em "Esqueceu a senha?", informa o e-mail, recebe um e-mail com um link e, por esse link, cadastra uma senha nova.

O Django já traz tudo pronto em `django.contrib.auth.views`. O fluxo completo usa quatro views:

| View | O que faz | Template |
| --- | --- | --- |
| `PasswordResetView` | formulário para digitar o e-mail; envia o e-mail com o link | `password_reset_form.html`, `password_reset_email.html` |
| `PasswordResetDoneView` | página "enviamos um e-mail para você" | `password_reset_done.html` |
| `PasswordResetConfirmView` | o link do e-mail abre esta view, que pede a nova senha | `password_reset_confirm.html` |
| `PasswordResetCompleteView` | página "senha alterada" | `password_reset_complete.html` |

As duas últimas já foram feitas na [Dica 17 - Cadastro de Usuários](077-17-cadastro.md) (lá usamos o mesmo link de troca de senha para ativar a conta do usuário recém-cadastrado). Agora faltam as duas primeiras.

## Pré-requisitos

Esta dica continua o *Projeto Dicas de Django* do ponto em que a [Dica 17](077-17-cadastro.md) parou. Você precisa ter:

* o app `backend/accounts` com o usuário customizado que faz login com e-mail ([Dica 14](074-14-django-custom-user-email.md) e [Dica 15](075-15-login-com-email.md));
* as rotas `password_reset_confirm` e `password_reset_complete` da Dica 17;
* o **MailHog** rodando pelo `docker-compose` ([Dica 07](067-07-docker-compose.md)) e o envio de e-mail configurado no `settings.py` ([Dica 12](072-012-fale-co-nosco-form-email.md)).

A configuração de e-mail no `settings.py`, que já existe desde a Dica 12, é esta:

```python
# backend/settings.py (trecho)
LANGUAGE_CODE = 'pt-br'

# Email config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
EMAIL_HOST = config('EMAIL_HOST', 'localhost')
EMAIL_PORT = config('EMAIL_PORT', 1025, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
```

A porta `1025` é a do SMTP do MailHog, e a caixa de entrada dele fica em `http://localhost:8025`.

## O link "Esqueceu a senha?" no login

Em `backend/accounts/templates/registration/login.html` já existia o link "Esqueceu a senha?", mas com o `href` vazio. Aponte-o para a rota `password_reset`, que vamos criar a seguir:

```html
<!-- backend/accounts/templates/registration/login.html (trecho) -->
<a href="{% url 'password_reset' %}" class="text-sm text-teal-500 hover:underline ml-auto">Esqueceu a senha?</a>
```

## As rotas

Acrescente as duas rotas no fim de `backend/accounts/urls.py`. O arquivo completo fica assim:

```python
# backend/accounts/urls.py
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from backend.accounts import views as v

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # noqa E501
    path('logout/', LogoutView.as_view(), name='logout'),  # noqa E501
    path('register/', v.signup, name='signup'),  # noqa E501
    path('reset/<uidb64>/<token>/', v.MyPasswordResetConfirm.as_view(), name='password_reset_confirm'),  # noqa E501
    path('reset/done/', v.MyPasswordResetComplete.as_view(), name='password_reset_complete'),  # noqa E501
    path('password_reset/', v.MyPasswordReset.as_view(), name='password_reset'),  # noqa E501
    path('password_reset/done/', v.MyPasswordResetDone.as_view(), name='password_reset_done'),  # noqa E501
]
```

Os nomes `password_reset` e `password_reset_done` são importantes: a `PasswordResetView`, depois de enviar o e-mail, redireciona para `reverse_lazy('password_reset_done')`, e o template do e-mail usa a rota `password_reset_confirm`. Como o app é incluído em `backend/urls.py` com `path('accounts/', include('backend.accounts.urls'))`, sem namespace, a página fica em `http://localhost:8000/accounts/password_reset/`.

## As views

Em `backend/accounts/views.py`, importe `PasswordResetDoneView` e `PasswordResetView` junto com as views que já estavam lá e crie as duas classes. Elas só herdam das views do Django; a docstring lembra quais templates cada uma precisa. O arquivo completo:

```python
# backend/accounts/views.py
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView
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

Os templates padrão dessas views ficam em `registration/`, com os nomes da docstring. Basta criar arquivos com esses nomes em `backend/accounts/templates/registration/` para que os nossos, com o visual do projeto, sejam usados no lugar dos templates do admin do Django. O `password_reset_subject.txt` é opcional: sem ele, o Django usa o assunto padrão traduzido, "Redefinição de senha em localhost:8000".

## O formulário de e-mail: password_reset_form.html

A `PasswordResetView` usa o `PasswordResetForm`, que tem um único campo, `email`. Por isso o `input` tem `name="email"`. O layout é o mesmo da tela de login (Tailwind CSS, estendendo `base_login.html`):

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

O arquivo fica em `backend/accounts/templates/registration/password_reset_form.html`.

## O corpo do e-mail: password_reset_email.html

Este é o texto do e-mail. A view passa para o template o `user`, o `protocol` (`http` ou `https`), o `domain` (aqui, `localhost:8000`), o `uid` (o id do usuário em base64) e o `token`. Com `uid` e `token` montamos o link para a rota `password_reset_confirm`. O `{% autoescape off %}` evita que o Django escape caracteres do texto, já que o e-mail é texto puro.

```html
{% autoescape off %}
  Para iniciar o processo de redefinição de senha para sua conta {{ user.get_username }}, clique no link abaixo:

  {{ protocol }}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}

  Se clicar no link acima não funcionar, por favor copie e cole a URL no navegador.

  Atenciosamente,
  Equipe Dev.
{% endautoescape %}
```

O arquivo fica em `backend/accounts/templates/registration/password_reset_email.html`. Repare que ele não tem a linha de comentário `<!-- ... -->` no topo, como os outros templates: ela apareceria no corpo do e-mail.

## A confirmação de envio: password_reset_done.html

Depois de enviar o formulário, o usuário é redirecionado para esta página:

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

A mensagem é propositalmente vaga ("se uma conta existe com o e-mail fornecido"): a `PasswordResetView` mostra a mesma página mesmo quando o e-mail não está cadastrado, para não revelar quais e-mails existem no sistema.

A pasta de templates do app fica assim:

```
backend/accounts/templates/registration/
├── login.html
├── password_reset_complete.html   # Dica 17
├── password_reset_confirm.html    # Dica 17
├── password_reset_done.html       # novo
├── password_reset_email.html      # novo
├── password_reset_form.html       # novo
└── registration_form.html         # Dica 17
```

## Testando

Com os contêineres no ar (`make up`, que roda `docker-compose up -d`) e o servidor rodando:

1. Saia do sistema e, na tela de login, clique em **Esqueceu a senha?**.
2. Informe o e-mail de um usuário cadastrado (no vídeo, `regis@email.com`) e clique em **Enviar**. Aparece a página "Redefinição de senha enviada".
3. Abra o MailHog em `http://localhost:8025`. Chegou um e-mail de `webmaster@localhost` com o assunto **Redefinição de senha em localhost:8000**:

    ```
    Para iniciar o processo de redefinição de senha para sua conta regis@email.com, clique no link abaixo:

    http://localhost:8000/accounts/reset/Mw/bg42lm-984f6c848c7b6aea3247183735028c72/

    Se clicar no link acima não funcionar, por favor copie e cole a URL no navegador.

    Atenciosamente,
    Equipe Dev.
    ```

    O `Mw` é o id do usuário (3) em base64, e o resto é o token, que só pode ser usado uma vez.

4. Clique no link. A `PasswordResetConfirmView` valida o token, guarda-o na sessão e redireciona para `/accounts/reset/Mw/set-password/` (assim o token não fica na barra de endereço), onde abre a tela **Trocar senha** da Dica 17. Digite a nova senha duas vezes e clique em **Trocar senha**; você é levado para `/accounts/reset/done/`.
5. Volte ao login e entre com o e-mail e a senha nova.

Lembrando que o MailHog só simula o recebimento: nenhum e-mail sai de verdade. Em produção, troque as variáveis `EMAIL_*` do `.env` pelas do seu servidor SMTP.

Com isso o ciclo de autenticação do projeto fica completo: cadastro, login, logout e redefinição de senha, todos com as views prontas do Django e templates próprios.
