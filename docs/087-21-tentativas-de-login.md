# Dica 21 - Tentativas de Login

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, Tailwind CSS e MailHog (no Docker).
{: .versoes }

<a href="https://youtu.be/WLnJskC17PQ">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`). Se copiar código de lá, remova a `\`.

![](../.gitbook/assets/tags.png)

Um ataque de **força bruta** é quando alguém tenta várias senhas seguidas até acertar. Nesta dica vamos impedir isso no login do projeto **Dicas de Django**:

* cada login, logout e senha errada fica registrado num model `AuditEntry` (ação, IP e e-mail);
* na **terceira** senha errada, o usuário não consegue mais entrar e recebe um e-mail pedindo para resetar a senha;
* quando ele finalmente acerta a senha, as tentativas erradas são apagadas.

Para isso vamos usar os signals de autenticação do Django (`user_logged_in` e `user_logged_out`), criar um signal próprio (`user_login_password_failed`), reescrever a view de login (`MyLoginView`) e o formulário de autenticação (`MyAuthenticationForm`).

## Pré-requisitos

* O projeto das dicas anteriores, com o usuário customizado que faz login por **e-mail** (dicas 14 e 15), o `TimeStampedModel` na app `core` e o `accounts/services.py` com o envio de e-mail da dica 17.
* O MailHog rodando no `docker-compose` para ver os e-mails enviados.

No vídeo, cada passo foi um commit ligado à issue 116 do repositório, por exemplo:

```bash
git add . ; git commit -m 'Login. resolve #116'
```

## 1. Mostrando os erros no login

Edite `accounts/templates/registration/login.html` e, logo abaixo do título **Login** e antes do `<form>`, mostre os erros que não pertencem a um campo específico (`non_field_errors`). É neles que o `AuthenticationForm` coloca "e-mail ou senha incorretos":

```html
<!-- accounts/templates/registration/login.html -->
          <h2 class="text-2xl lg:text-3xl font-bold text-gray-900">
            Login
          </h2>

          {% if form.errors %}
            {% for error in form.non_field_errors %}
              <p class="text-red-500">{{ error }}</p>
            {% endfor %}
          {% endif %}

          <form class="mt-8 space-y-6" action="." method="POST">
            {% csrf_token %}
            ...
```

Agora, ao errar o e-mail ou a senha, aparece em vermelho a mensagem padrão do Django, "Por favor, entre com um endereço de email e senha corretos. Note que ambos os campos diferenciam maiúsculas e minúsculas.". Ela é a mesma tanto para e-mail inexistente quanto para senha errada; vamos separar os dois casos.

## 2. O model AuditEntry e os signals de login e logout

Em `accounts/models.py`, crie o model `AuditEntry` (ideia tirada de uma resposta do Stack Overflow, cujo link fica num comentário no código) e os receivers dos signals de autenticação do Django:

```python
# accounts/models.py
from django.contrib.auth.signals import user_logged_in, user_logged_out
...

from backend.core.models import TimeStampedModel

from .managers import UserManager
from .signals import user_login_password_failed

# https://stackoverflow.com/a/37620866/802542

...


class AuditEntry(TimeStampedModel):
    action = models.CharField(max_length=64)
    ip = models.GenericIPAddressField(null=True)
    email = models.CharField(max_length=256, null=True)

    def __unicode__(self):
        return f'{self.action}-{self.email}-{self.ip}'

    def __str__(self):
        return f'{self.action}-{self.email}-{self.ip}'


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    AuditEntry.objects.create(
        action='user_logged_in',
        ip=ip,
        email=user.email
    )


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    AuditEntry.objects.create(
        action='user_logged_out',
        ip=ip,
        email=user.email
    )


@receiver(user_login_password_failed)
def user_login_password_failed(sender, **kwargs):
    user = kwargs['user']
    AuditEntry.objects.create(
        action='user_login_password_failed',
        email=user.email
    )
```

* `AuditEntry` herda de `TimeStampedModel`, então tem `created` e `modified`.
* `user_logged_in` e `user_logged_out` são signals que o próprio Django dispara no login e no logout. Os receivers gravam a ação, o IP (`request.META.get('REMOTE_ADDR')`) e o e-mail do usuário.
* `user_login_password_failed` é um signal **nosso**, que vamos disparar quando o usuário existe mas a senha está errada. Aqui não gravamos o IP, só a ação e o e-mail.
* Signals ainda serão explicados com mais calma num vídeo próprio.

No vídeo, o receiver do signal próprio e o import dele ficaram comentados até o arquivo `signals.py` existir (passo 3), porque sem ele o `migrate` dá erro de import.

Registre o model no admin:

```python
# accounts/admin.py
from .models import AuditEntry, Document, Profile, User

...


@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ('action', 'email', 'ip', 'created')
    list_filter = ('action',)
```

```bash
python manage.py makemigrations
python manage.py migrate
```

## 3. O signal próprio

Crie `accounts/signals.py`. Criar um signal é só instanciar `Signal`:

```python
# accounts/signals.py
from django.dispatch import Signal

user_login_password_failed = Signal()
```

Agora descomente o import e o receiver no `models.py` e rode o `migrate` de novo; o erro some.

## 4. A view de login: MyLoginView

Até aqui a url de login usava a `LoginView` padrão. Vamos trocar por uma view nossa, `MyLoginView`, que herda de `LoginView` e reescreve `form_invalid` e `form_valid`:

```python
# accounts/views.py
# ... (veja o arquivo completo no GitHub)


class MyLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = MyAuthenticationForm

    def form_invalid(self, form):
        email = form.data.get('username')

        if email:
            try:
                user = User.objects.get(email=email)

                for error in form.errors.as_data()['__all__']:
                    if error.code == 'max_attempt':
                        # Envia email para o usuário resetar a senha.
                        send_mail_to_user_reset_password(self.request, user)

            except User.DoesNotExist:
                pass
            else:
                # Dispara o signal quando o usuário existe, mas a senha está errada.
                user_login_password_failed.send(
                    sender=__name__,
                    request=self.request,
                    user=user
                )

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        user = form.get_user()

        # Autentica usuário
        auth_login(self.request, user)

        # Zera o AuditEntry
        AuditEntry.objects.filter(
            email=user.email,
            action='user_login_password_failed'
        ).delete()

        return HttpResponseRedirect(self.get_success_url())
```

Código completo: [backend/accounts/views.py](https://github.com/rg3915/dicas-de-django/blob/646e636535c21b7ba51fd08cda31d6462d4142fa/backend/accounts/views.py)

**form_invalid** (o formulário não validou):

* O campo do formulário se chama `username`, mas no nosso projeto ele contém o **e-mail**. Por isso procuramos o usuário com `User.objects.get(email=email)`.
* Se o usuário não existe, não há o que registrar (`pass`).
* Se existe, percorremos os erros gerais do formulário (`form.errors.as_data()['__all__']`). Se um deles tem o código `max_attempt`, enviamos o e-mail para resetar a senha. O envio é feito aqui na view, e não no formulário, porque precisa do `request`.
* Depois disparamos o nosso signal com `user_login_password_failed.send(...)`, que grava um `AuditEntry` com a ação `user_login_password_failed`.
* No fim, renderiza o template de novo com o formulário e os erros, como a `LoginView` faria.

**form_valid** (login correto): autentica o usuário com `auth_login` (importado com outro nome para não conflitar com o `login` do Django) e **apaga** as tentativas erradas desse e-mail, zerando a contagem.

Na url, troque a `LoginView` pela nova view:

```python
# accounts/urls.py
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from backend.accounts import views as v

urlpatterns = [
    path('login/', v.MyLoginView.as_view(), name='login'),  # noqa E501
    path('logout/', LogoutView.as_view(), name='logout'),  # noqa E501
    ...
]
```

## 5. O formulário: MyAuthenticationForm

O formulário herda do `AuthenticationForm` do Django e reescreve as mensagens de erro e o `clean()`:

```python
# accounts/forms.py
# ... (veja o arquivo completo no GitHub)


class MyAuthenticationForm(AuthenticationForm):

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
        'invalid_password': _("Senha inválida."),
        'max_attempt': _(
            "Você atingiu o número máximo de tentativas. "
            "Estamos te enviando um e-mail."
        ),
    }

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            if self.user_cache is None:
                self.check_authentication_error(username)
            else:
                self.confirm_login_allowed(self.user_cache)
            return self.cleaned_data
        else:
            self.validation_field()

    def validation_field(self):
        raise ValidationError(
            'Os campos e-mail e senha devem ser preenchidos.',
            code='invalid_fields',
            params={'username': self.username_field.verbose_name},
        )

    def check_authentication_error(self, username):
        '''
        Verifica se foi erro de autenticação.
        '''
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            raise self.get_invalid_login_error()
        else:
            self.check_max_attempts(user)
            raise self.get_invalid_password_error()

    def check_max_attempts(self, user):
        '''
        Verifica o número de tentativas de login.
        '''
        max_attempts = AuditEntry.objects.filter(
            email=user.email,
            action='user_login_password_failed'
        ).count()
        if max_attempts >= 2:
            # Envia email para o usuário resetar a senha.
            # Envia pela views.
            raise self.get_max_attempts_error()
    # ... (veja o arquivo completo no GitHub)
```

Código completo: [backend/accounts/forms.py](https://github.com/rg3915/dicas-de-django/blob/646e636535c21b7ba51fd08cda31d6462d4142fa/backend/accounts/forms.py)

**As mensagens de erro.** `invalid_login` e `inactive` são as do `AuthenticationForm` original (em inglês, mas como estão dentro de `_()`, aparecem traduzidas para o português). Acrescentamos `invalid_password` ("Senha inválida.") e `max_attempt`.

**O `clean()`** segue o do `AuthenticationForm`:

* se e-mail e senha foram preenchidos, tenta autenticar com `authenticate()`;
* se não autenticou (`user_cache is None`), chama `check_authentication_error`;
* se autenticou, `confirm_login_allowed` verifica se o usuário está ativo;
* se faltou algum campo, `validation_field` levanta o erro "Os campos e-mail e senha devem ser preenchidos.".

**`check_authentication_error`** separa os dois casos que antes tinham a mesma mensagem:

* o e-mail não existe: erro `invalid_login` ("Por favor, entre com um endereço de email e senha corretos...");
* o e-mail existe, então a senha está errada: primeiro verifica o número de tentativas (`check_max_attempts`) e, se não passou do limite, levanta `invalid_password` ("Senha inválida.").

**`check_max_attempts`** conta quantos `AuditEntry` com a ação `user_login_password_failed` existem para aquele e-mail. Não há um contador: cada tentativa errada cria um registro novo, e contamos os registros. Com `>= 2`, a **terceira** tentativa errada já dá o erro `max_attempt` ("Você atingiu o número máximo de tentativas. Estamos te enviando um e-mail.").

Fluxo com senha errada:

| Tentativa | Registros antes | Erro mostrado | Registros depois |
|---|---|---|---|
| 1ª | 0 | Senha inválida. | 1 |
| 2ª | 1 | Senha inválida. | 2 |
| 3ª | 2 | Você atingiu o número máximo de tentativas... (e o e-mail é enviado) | 3 |

## 6. O e-mail de aviso

Em `accounts/services.py`, ao lado do `send_mail_to_user` que já existia (dica 17), crie uma função parecida, mudando o assunto e o template:

```python
# accounts/services.py
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import account_activation_token


def send_mail_to_user(request, user):
    ...


def send_mail_to_user_reset_password(request, user):
    current_site = get_current_site(request)
    use_https = request.is_secure()
    subject = 'Aviso: Erro em tentativas de login.'
    message = render_to_string('email/account_reset_password.html', {
        'user': user,
        'protocol': 'https' if use_https else 'http',
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    user.email_user(subject, message)
```

E o template do e-mail, feito a partir do `account_activation_email.html` ("salvar como"), com o link para a tela de redefinição de senha:

```html
<!-- accounts/templates/email/account_reset_password.html -->
{% autoescape off %}
  Olá {{ user.first_name }},

  Você excedeu o número de tentativas de login.
  Por favor clique no link abaixo para resetar sua senha:

  {{ protocol }}://{{ domain }}{% url 'password_reset_confirm' uidb64=uid token=token %}

  Atenciosamente,
  Equipe Dev.
{% endautoescape %}
```

## 7. Testando

```bash
python manage.py runserver
```

* Com um e-mail que não existe: aparece "Por favor, entre com um endereço de email e senha corretos...".
* Com um e-mail que existe e a senha errada: "Senha inválida." na primeira e na segunda vez; na terceira, "Você atingiu o número máximo de tentativas. Estamos te enviando um e-mail.".
* No admin, em **Audit entrys**, aparecem três registros `user_login_password_failed` para esse e-mail.
* No MailHog chega o e-mail "Aviso: Erro em tentativas de login.".
* Ao acertar a senha, o login é feito e os registros de falha desse e-mail são apagados; fica só o `user_logged_in`.

No vídeo, dois erros de digitação impediram o funcionamento na primeira tentativa, e vale conferir no seu código: a chave e o código do erro precisam ser **iguais** (`max_attempt`, no singular, tanto em `error_messages` quanto em `get_max_attempts_error` e na view), e a ação gravada pelo receiver precisa ser exatamente `user_login_password_failed`, que é a que o formulário conta e a view apaga.

## O problema do link de reset

Ao clicar no link do e-mail, a tela **Trocar senha** diz que o link é inválido ("O link para a recuperação de senha era inválido, possivelmente porque já foi utilizado..."). Isso não foi resolvido no vídeo. O contorno foi acrescentar, nessa mensagem, um link para a tela **Redefinição de senha**, onde o usuário pede um novo e-mail de recuperação e aí o fluxo funciona:

```html
<!-- accounts/templates/registration/password_reset_confirm.html -->
          {% else %}
            <p>O link para a recuperação de senha era inválido, possivelmente porque já foi utilizado. Por favor, solicite uma nova recuperação de senha.</p>
            <a href="{% url 'password_reset' %}" class="text-sm text-teal-500 hover:underline ml-auto">Resetar senha</a>
          {% endif %}
```

Observação: o motivo provável é o token. O e-mail usa o `account_activation_token` (o gerador da ativação de conta, que monta o hash com pk, timestamp e e-mail), mas a `PasswordResetConfirmView` valida o token com o `default_token_generator` do Django, que monta o hash de outro jeito; por isso o token nunca confere. Gerar o token com `from django.contrib.auth.tokens import default_token_generator` no `send_mail_to_user_reset_password` deve resolver.

## Resumo

* `AuditEntry` guarda ação, IP e e-mail de cada login, logout e senha errada.
* Os signals `user_logged_in` e `user_logged_out` do Django e o nosso `user_login_password_failed` criam esses registros.
* `MyAuthenticationForm` separa e-mail inexistente de senha errada e bloqueia na terceira tentativa.
* `MyLoginView` envia o e-mail de aviso, dispara o signal de senha errada e zera as tentativas quando o login dá certo.
