# Dica 22 - Validação

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, django-widget-tweaks 1.4.12 e ipdb.
{: .versoes }

<a href="https://youtu.be/l47Y4bMJj24">
    <img src="../.gitbook/assets/youtube.png">
</a>

Na [Dica 21 - Tentativas de Login](087-21-tentativas-de-login.md) usamos `ValidationError` no formulário de login sem explicar direito como funciona a validação de formulários no Django. Nesta dica vamos ver, no formulário de **Adicionar Usuário** do projeto **Dicas de Django**, as três formas mais usadas:

1. `clean_<campo>()`: validação de **um** campo;
2. `clean()`: validação que depende de **vários** campos;
3. `ValidationError` com `code` e mensagens num dicionário `error_messages`.

Documentação: [Form and field validation](https://docs.djangoproject.com/en/4.1/ref/forms/validation/)

## Pré-requisitos

* O projeto das dicas anteriores, com a lista de usuários e o formulário `user_form.html` da [Dica 20 - Templates](086-20-templates.md).
* O `CustomUserForm` em `backend/accounts/forms.py`:

```python
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
```

As views `user_create` e `user_update` instanciam o formulário com `request.POST or None` e o template acessa os erros do formulário. Ao acessar `form.errors` (ou `field.errors`), o Django roda a validação; por isso as mensagens aparecem na tela ao clicar em **Salvar**, mesmo sem salvar nada ainda.

## 1. Validando um campo: clean_<campo>

Na documentação, essa seção se chama *Cleaning a specific field attribute* (limpando um atributo de campo específico). Basta criar no formulário um método `clean_` seguido do nome do campo.

Regra: a primeira letra do nome não pode ser minúscula.

```python
# accounts/forms.py
class CustomUserForm(forms.ModelForm):
    ...

    def clean_first_name(self):
        data = self.cleaned_data['first_name']

        if data[0].islower():
            raise ValidationError(_('A primeira letra deve ser maiúscula.'))

        return data
```

* `self.cleaned_data['first_name']` já é o valor limpo do campo (o Django já verificou, por exemplo, que ele foi preenchido e que tem no máximo 150 caracteres).
* Se a regra falha, levantamos `ValidationError`. O `_()` (`gettext_lazy`) marca a mensagem para uma tradução futura.
* **Não esqueça de retornar o `data`**: o valor retornado é o que fica em `cleaned_data['first_name']`.

Digite um nome com letra minúscula e clique em **Salvar**: aparece "A primeira letra deve ser maiúscula." logo abaixo do campo. Isso porque o template já mostra os erros de cada campo:

```html
<!-- accounts/templates/accounts/user_form.html -->
{% for error in field.errors %}
  <span class="text-red-500">{{ error }}</span> <br>
{% endfor %}
```

Para validar o sobrenome ou o e-mail, você criaria `clean_last_name` e `clean_email` da mesma forma.

## 2. Validando vários campos: clean

Quando a regra depende de mais de um campo, usamos o `clean()` do formulário (*Cleaning and validating fields that depend on each other*). É o lugar certo, por exemplo, para comparar duas datas (início antes do fim).

Regra de exemplo: nome e sobrenome não podem ser iguais. A primeira versão, no vídeo, foi esta:

```python
# accounts/forms.py
    def clean(self):
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']

        if first_name == last_name:
            raise ValidationError(_('Nome e Sobrenome não podem ser iguais.'))

        return self.cleaned_data
```

Preenchendo nome e sobrenome iguais, o formulário não salva, mas **a mensagem não aparece**. O erro levantado no `clean()` não pertence a nenhum campo: ele vai para os `non_field_errors`, que o template ainda não mostra. Acrescente no `user_form.html`, logo depois do título e antes do `<form>`:

```html
<!-- accounts/templates/accounts/user_form.html -->
        <h2 class="text-2xl lg:text-3xl font-bold text-gray-900">
          {% if object.pk %}
            Editar
          {% else %}
            Adicionar
          {% endif %}
          Usuário
        </h2>

        {% if form.errors %}
          {% for error in form.non_field_errors %}
            <p class="text-red-500">{{ error }}</p>
          {% endfor %}
        {% endif %}

        <form class="mt-8 space-y-6" action="." method="POST" enctype="multipart/form-data">
```

Agora aparece "Nome e Sobrenome não podem ser iguais." no topo do formulário. O ideal seria colocar esse bloco no `base.html`, para valer em todas as páginas, mas aí seria preciso ajustar o layout; por isso ele ficou no próprio `user_form.html`.

## 3. ValidationError com code e error_messages

A documentação recomenda levantar o `ValidationError` com um `code` (e, se houver valores na mensagem, com `params`), e não só com o texto. Vamos guardar a mensagem num dicionário `error_messages`, com uma chave que funciona como código, e criar um método que monta o erro.

Regra: o primeiro caractere do nome não pode ser um número.

```python
# accounts/forms.py
class CustomUserForm(forms.ModelForm):
    ...

    error_messages = {
        'invalid_first_character': _('O primeiro caractere deve ser uma letra.'),
    }

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

É o mesmo padrão usado no `MyAuthenticationForm` da dica 21 (`get_invalid_password_error`, `get_max_attempts_error`).

### O KeyError e o ipdb

Ao testar um nome começando com número, a página quebrou com `KeyError: 'first_name'` na linha do `clean()`. O motivo: quando um `clean_<campo>()` levanta erro, o Django **remove** aquele campo de `cleaned_data`. Quando o `clean()` geral roda depois, `self.cleaned_data['first_name']` não existe mais.

No vídeo, isso foi investigado com o `ipdb` (acrescentado ao `requirements.txt`):

```bash
pip install ipdb
```

```python
    def clean(self):
        import ipdb; ipdb.set_trace()
        ...
```

No console do `ipdb`, `self.cleaned_data` mostrava só `last_name` e `email`, enquanto `self.data` (os dados brutos do POST) ainda tinha o `first_name`. A solução foi ler o nome de `self.data`, com `.get()`, para não quebrar se o valor vier vazio.

## 4. Usando super().clean()

Por último, a documentação mostra o `clean()` chamando `super().clean()` no começo. Assim mantemos as validações da classe pai (importante quando herdamos de um formulário pronto do Django, como o `AuthenticationForm`) e trabalhamos com o `cleaned_data` que ele devolve. Como o `super().clean()` já cuida do `cleaned_data`, não é preciso retornar nada no fim (o `return` ficou comentado).

A versão final do formulário:

```python
# accounts/forms.py
# ... (veja o arquivo completo no GitHub)


class CustomUserForm(forms.ModelForm):
    # ... (campos e Meta, veja o arquivo completo no GitHub)

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

    # ... (veja o arquivo completo no GitHub)
```

Código completo: [backend/accounts/forms.py](https://github.com/rg3915/dicas-de-django/blob/bc253f4b05d112f56a7973166347f354a89e24b0/backend/accounts/forms.py)

## Testando

| Nome | Sobrenome | Resultado |
|---|---|---|
| `regis` | `Santos` | "A primeira letra deve ser maiúscula." (abaixo do campo Nome) |
| `1Regis` | `Santos` | "O primeiro caractere deve ser uma letra." (abaixo do campo Nome) |
| `Regis` | `Regis` | "Nome e Sobrenome não podem ser iguais." (no topo do formulário) |
| `Regis` | `Santos` | válido |

Esses resultados foram conferidos rodando o formulário (com os mesmos campos e métodos) no Django 4.1.3.

## Boas práticas da documentação

A documentação do Django lista como escrever um bom `ValidationError`:

* passe um `code` (`code='invalid'`), que permite identificar o erro sem depender do texto;
* coloque valores variáveis em `params`, e não direto na string;
* use mapeamento (`%(value)s`) em vez de `%s`;
* envolva a mensagem em `gettext` (`_()`), para poder traduzir depois.

```python
raise ValidationError(
    _('Invalid value: %(value)s'),
    code='invalid',
    params={'value': '42'},
)
```

A documentação também mostra como levantar vários erros de uma vez e como usar `add_error()` para ligar um erro do `clean()` a um campo específico.
