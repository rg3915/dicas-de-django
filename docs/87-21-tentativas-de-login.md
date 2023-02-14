# Dica 21 - Tentativas de Login

VIDEO EM BREVE.

Edite `registration/login.html`

```html
{% if form.errors %}
  {% for error in form.non_field_errors %}
    <p class="text-red-500">{{ error }}</p>
  {% endfor %}
{% endif %}
```

## accounts/models.py

```python
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

## admin.py

```python
@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ('action', 'email', 'ip', 'created')
    list_filter = ('action',)
```

## signals.py

```python
from django.dispatch import Signal

user_login_password_failed = Signal()
```

## urls.py

```python
path('login/', v.MyLoginView.as_view(), name='login'),  # noqa E501
```

## views.py

```python
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

## forms.py


```python
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from backend.accounts.models import User

from .models import AuditEntry


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

    def get_invalid_password_error(self):
        '''
        Verifica se foi erro de senha inválida.
        '''
        return ValidationError(
            self.error_messages['invalid_password'],
            code='invalid_password',
            params={'username': self.username_field.verbose_name},
        )

    def get_invalid_login_error(self):
        '''
        Verifica se foi erro de login.
        '''
        return ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
            params={'username': self.username_field.verbose_name},
        )

    def get_max_attempts_error(self):
        '''
        Verifica se excedeu o número de tentativas de login.
        '''
        return ValidationError(
            self.error_messages['max_attempt'],
            code='max_attempt',
            params={'username': self.username_field.verbose_name},
        )
```


## views.py

```python
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
```

## services.py

```python
# accounts/services.py
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import account_activation_token


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
