# Dica 22 - Validação

VIDEO EM BREVE.

```python
# accounts/forms.py
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
```
