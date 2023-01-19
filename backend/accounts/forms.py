# accounts/forms.py
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from backend.accounts.models import User

from .models import AuditEntry


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

    error_messages = {
        'invalid_first_character': _('O primeiro caractere deve ser uma letra.'),
    }

    def clean(self):
        cleaned_data = super().clean()
        first_name = self.data.get('first_name')
        last_name = cleaned_data['last_name']

        if first_name == last_name:
            raise ValidationError(_('Nome e Sobrenome não podem ser iguais.'))

        # return self.cleaned_data

    def clean_first_name(self):
        data = self.cleaned_data['first_name']

        if data[0].islower():
            raise ValidationError(_('A primeira letra deve ser maiúscula.'))

        if data[0].isdigit():
            raise self.get_invalid_first_character_error()

        return data

    def get_invalid_first_character_error(self):
        '''
        O primeiro caractere deve ser uma letra.
        '''
        return ValidationError(
            self.error_messages['invalid_first_character'],
            code='invalid_first_character'
        )


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
