# Dica 17 - Cadastro de Usuários no Django

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, django-widget-tweaks 1.4.12, six 1.16.0 e MailHog.
{: .versoes }

<a href="https://youtu.be/JKUYdjIfugU">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`), por causa do GitBook. Aqui elas já estão escritas do jeito certo, sem a barra.

![](../.gitbook/assets/tags.png)

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django) (branch `aula17`)

Vamos criar o **cadastro de usuários** do *Projeto Dicas de Django*. O fluxo é este:

1. O visitante clica em **Criar conta** na tela de login e informa nome, sobrenome e e-mail (sem senha).
2. O Django cria o usuário e envia um **e-mail** com um link.
3. O usuário clica no link e **define a sua senha** numa tela do próprio Django (a `PasswordResetConfirmView`).
4. Pronto: ele já pode fazer login com o e-mail e a senha que definiu.

Assim confirmamos que o e-mail existe e é do usuário, e o próprio usuário escolhe a senha. Esta dica continua a [Dica 16 - Logout](076-16-logout.md) e usa o usuário com e-mail da [Dica 14](074-14-django-custom-user-email.md), a tela de login da [Dica 15](075-15-login-com-email.md) e o MailHog da [Dica 7](067-07-docker-compose.md).

Vamos criar ou editar estes arquivos, todos na app `accounts`:

* accounts/templates/registration/registration_form.html
* accounts/templates/registration/password_reset_confirm.html
* accounts/templates/registration/password_reset_complete.html
* accounts/templates/email/account_activation_email.html
* accounts/forms.py
* accounts/services.py
* accounts/tokens.py
* accounts/urls.py
* accounts/views.py

As duas views do Django que vamos estender estão na documentação:

[https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.views.PasswordResetConfirmView](https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.views.PasswordResetConfirmView)

[https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.views.PasswordResetCompleteView](https://docs.djangoproject.com/en/4.1/topics/auth/default/#django.contrib.auth.views.PasswordResetCompleteView)

```bash
git checkout -b aula17
```

## Link Criar conta no login

No `login.html` da Dica 15, o link **Criar conta** passa a apontar para a URL `signup`, que vamos criar:

```html
<!-- backend/accounts/templates/registration/login.html -->
<a href="{% url 'signup' %}" class="text-teal-500 hover:underline">Criar conta</a>
```

## O template de cadastro

```bash
touch backend/accounts/templates/registration/registration_form.html
```

É a tela de cadastro do Windster, herdando do `base_login.html` da Dica 15. Os campos têm os `name` iguais aos campos do formulário: `first_name`, `last_name` e `email`. Os campos de senha (`password1` e `password2`) estão **comentados**: a senha não é pedida aqui, o usuário vai defini-la pelo link do e-mail.

```html
<!-- backend/accounts/templates/registration/registration_form.html -->
{% extends "base_login.html" %}

{% block content %}
  <main class="bg-gray-50">
    <!-- ... -->
          <form class="mt-8 space-y-6" action="." method="POST">
            {% csrf_token %}
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
            <!-- ... (last_name e email seguem o mesmo padrão) -->
            <!-- <div>
              <label for="id_password1" class="text-sm font-medium text-gray-900 block mb-2">Senha</label>
              <input
                id="id_password1"
                type="password"
                name="password1"
                ...
            </div> -->
            <!-- ... -->
            <button type="submit" class="text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium rounded-lg text-base px-5 py-3 w-full sm:w-auto text-center">Salvar</button>
            <div class="text-sm font-medium text-gray-500">
              Você já tem uma conta? <a href="{% url 'login' %}" class="text-teal-500 hover:underline">Login</a>
            </div>
          </form>
    <!-- ... -->
  </main>

{% endblock content %}
```

Código completo: [backend/accounts/templates/registration/registration_form.html](https://github.com/rg3915/dicas-de-django/blob/8043725024b1348772b866713f880a56dc96860e/backend/accounts/templates/registration/registration_form.html)

## O formulário

Crie o `accounts/forms.py`. É um `ModelForm` do nosso `User` com três campos. Os campos foram redeclarados para ganhar rótulos em português e para que nome e sobrenome sejam **obrigatórios** (no model eles têm `blank=True`).

```python
# backend/accounts/forms.py
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

## O token

Crie o `accounts/tokens.py`. O `PasswordResetTokenGenerator` é a classe que o Django usa para gerar os tokens de redefinição de senha. Aqui criamos um gerador próprio, que calcula o token a partir do `pk` do usuário, do *timestamp* e do e-mail.

```python
# backend/accounts/tokens.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            text_type(user.pk) + text_type(timestamp) + text_type(user.email)
        )


account_activation_token = AccountActivationTokenGenerator()
```

O `text_type` vem da biblioteca `six` (no Python 3 ele é simplesmente o `str`), então ela precisa estar instalada; veja a seção de instalação abaixo.

## O envio do e-mail

Crie o `accounts/services.py`. A função `send_mail_to_user` monta a mensagem a partir de um template e envia com o `email_user`, o método do nosso `User` (Dica 14) que chama o `send_mail` com o e-mail do próprio usuário como destinatário.

```python
# backend/accounts/services.py
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

* `get_current_site(request)` pega o domínio atual (como o projeto não usa o `django.contrib.sites`, o Django usa o host da requisição, por exemplo `localhost:8000`).
* `request.is_secure()` diz se a requisição veio por HTTPS, para montar o link com o protocolo certo.
* `uid` é o `pk` do usuário em base64 (`urlsafe_base64_encode(force_bytes(user.pk))`), e `token` é o token gerado pelo `account_activation_token`. São exatamente os dois parâmetros que a URL `password_reset_confirm` espera.

## O template do e-mail

No vídeo, esse template ficou faltando no passo a passo e o cadastro deu erro ao enviar o e-mail:

```
django.template.exceptions.TemplateDoesNotExist: email/account_activation_email.html
```

Crie a pasta e o arquivo:

```bash
mkdir -p backend/accounts/templates/email
touch backend/accounts/templates/email/account_activation_email.html
```

```html
<!-- backend/accounts/templates/email/account_activation_email.html -->
{% autoescape off %}
  Olá {{ user.first_name }},

  Por favor clique no link abaixo para confirmar seu cadastro:

  {{ protocol }}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}
{% endautoescape %}
```

O `{% autoescape off %}` evita que o Django escape caracteres do texto, já que o e-mail é texto puro e não HTML. O link aponta para a URL `password_reset_confirm`, com o `uid` e o `token` gerados no `services.py`.

## As URLs

No `accounts/urls.py`, acrescente as três últimas rotas:

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
]
```

* `register/` é o cadastro.
* `reset/<uidb64>/<token>/` é o link que vai no e-mail, onde o usuário define a senha. O nome `password_reset_confirm` é o mesmo usado pelo Django no "esqueci a senha", e é por ele que o template do e-mail monta o link.
* `reset/done/` é a página de "senha definida". O nome `password_reset_complete` é para onde a `PasswordResetConfirmView` redireciona depois de salvar a senha.

## As views

```python
# backend/accounts/views.py
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

* **`signup`**: valida o formulário, salva o usuário (`form.save()`), envia o e-mail com `send_mail_to_user` e redireciona para o login. Repare que o formulário não é passado para o template (`render(request, template_name)`), então, se o formulário for inválido (por exemplo, um e-mail que já está cadastrado), a página de cadastro só aparece de novo, sem mensagem de erro.
* **`MyPasswordResetConfirm`**: estende a `PasswordResetConfirmView`. Ela confere o `uidb64` e o `token` do link, mostra o formulário de nova senha (template `registration/password_reset_confirm.html`) e, ao salvar, grava a senha. No `form_valid` marcamos também `is_active = True`, ativando a conta.
* **`MyPasswordResetComplete`**: estende a `PasswordResetCompleteView` sem mudar nada; ela só mostra o template `registration/password_reset_complete.html`.

O usuário é criado **sem senha** (o campo `password` fica vazio). Uma senha vazia nunca confere no login, então ele só consegue entrar depois de definir a senha pelo link.

Uma curiosidade: a `PasswordResetConfirmView` valida o token com o gerador padrão do Django, e não com o `account_activation_token`. Funciona porque o gerador padrão calcula o token com `pk`, senha, data do último login, *timestamp* e e-mail; para um usuário recém-criado, a senha está vazia e o último login é `None`, então o resultado é igual ao do nosso gerador. Depois que a senha é definida, o token muda e o link deixa de valer (ele só pode ser usado uma vez).

## Os templates de definir senha

Crie o `password_reset_confirm.html`. Ele usa o `django-widget-tweaks` (`{% load widget_tweaks %}` e `{% render_field %}`) para renderizar os campos do formulário de nova senha com as classes do Tailwind, sem precisar escrever cada `<input>` à mão. A variável `validlink`, que vem da view, diz se o link é válido; se não for, aparece uma mensagem pedindo um novo link.

```html
<!-- backend/accounts/templates/registration/password_reset_confirm.html -->
{% extends "base_login.html" %}
{% load widget_tweaks %}

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
            Trocar senha
          </h2>
          <p class="text-sm font-medium text-gray-500">Digite sua nova senha.</p>
          {% if validlink %}
            <form class="mt-8 space-y-6" action="." method="POST">
              {% csrf_token %}
              {% for field in form.visible_fields %}
                <div>
                  <label class="text-sm font-medium text-gray-900 block mb-2">{{ field.label }}</label>
                  {% render_field field class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-cyan-600 focus:border-cyan-600 block w-full p-2.5" %}
                </div>
                <span class="text-sm font-medium text-gray-500">{{ field.help_text }}</span>
                {% for error in field.errors %}
                  <span class="text-red-500">{{ error }}</span> <br>
                {% endfor %}
              {% endfor %}
              <button type="submit" class="text-white bg-cyan-600 hover:bg-cyan-700 focus:ring-4 focus:ring-cyan-200 font-medium rounded-lg text-base px-5 py-3 w-full sm:w-auto text-center">Trocar senha</button>
              <div class="text-sm font-medium text-gray-500">
                Você já tem uma conta? <a href="{% url 'login' %}" class="text-teal-500 hover:underline">Login</a>
              </div>
            </form>
          {% else %}
            <p>O link para a recuperação de senha era inválido, possivelmente porque já foi utilizado. Por favor, solicite uma nova recuperação de senha.</p>
          {% endif %}
        </div>
      </div>
    </div>
  </main>
{% endblock content %}
```

E o `password_reset_complete.html`, a página final, com o link para o login:

```html
<!-- backend/accounts/templates/registration/password_reset_complete.html -->
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
            Deu tudo certo!
          </h2>
          <p class="text-sm font-medium text-gray-500">
            Sua senha foi definida. Você pode prosseguir e se <a class="text-sm font-medium text-cyan-600 hover:bg-gray-100 rounded-lg" href="{% url 'login' %}">autenticar</a> agora.
          </p>
        </div>
      </div>
    </div>
  </main>
{% endblock content %}
```

## Instalando as dependências

Instale o [django-widget-tweaks](https://pypi.org/project/django-widget-tweaks/) e o `six` (usado no `tokens.py`) e registre no `requirements.txt`:

```bash
pip install django-widget-tweaks six
pip freeze | grep django-widget-tweaks >> requirements.txt
pip freeze | grep six >> requirements.txt
```

No `requirements.txt` do projeto ficaram `django-widget-tweaks==1.4.12` e `six==1.16.0`.

Acrescente o `widget_tweaks` no `INSTALLED_APPS`, junto das apps de terceiros:

```python
# backend/settings.py
INSTALLED_APPS = [
    'backend.accounts',  # <<<
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # apps de terceiros
    'django_extensions',
    'widget_tweaks',
    # minhas apps
    'backend.core',
    'backend.crm',
]
```

## Testando

Suba os serviços (banco e MailHog) e rode o servidor:

```bash
docker-compose up -d
python manage.py runserver
```

1. Em [http://localhost:8000/accounts/login/](http://localhost:8000/accounts/login/), clique em **Criar conta** (ou acesse [http://localhost:8000/accounts/register/](http://localhost:8000/accounts/register/)).
2. Preencha nome, sobrenome e e-mail e clique em **Salvar**. Você volta para a tela de login.
3. Abra o MailHog em [http://localhost:8025](http://localhost:8025). Lá está o e-mail "Ative sua conta." com o link no formato `http://localhost:8000/accounts/reset/<uid>/<token>/`.
4. Clique no link, digite a nova senha duas vezes e salve. Aparece a página "Deu tudo certo!".
5. Clique em **autenticar** e faça login com o e-mail e a senha nova. Você entra no dashboard, com "Olá" e o seu nome na barra superior.

## Problemas que apareceram no vídeo

O vídeo foi regravado, e no meio do caminho o banco estava num estado inconsistente. Ao salvar o cadastro, o Django mostrou:

```
django.db.utils.ProgrammingError: relation "accounts_user" does not exist
```

A tabela do usuário não existia no banco do Docker. A solução foi recriar o banco do zero: parar e remover os contêineres do projeto (no vídeo, pelo Portainer; também dá pelo terminal com `docker-compose down`), apagar os volumes e subir tudo de novo:

```bash
docker volume prune -f
docker-compose up -d
python manage.py migrate
python manage.py createsuperuser
```

Lembre que o `docker volume prune -f` apaga **todos** os volumes que não estão em uso, inclusive de outros projetos.

Depois disso apareceu o `TemplateDoesNotExist: email/account_activation_email.html`, resolvido criando o template do e-mail, como mostrado acima. Como o usuário já tinha sido criado antes do erro (o e-mail é enviado depois do `form.save()`), foi preciso apagar esse usuário no admin e cadastrar de novo para receber o e-mail.

Na [Dica 18 - Esqueci a senha](078-18-esqueci-senha.md), aproveitamos as mesmas telas de definir senha para o fluxo de "esqueci a senha".
