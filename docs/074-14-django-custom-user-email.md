# Dica 14 - Django Custom User com e-mail

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10 e PostgreSQL 14 (no Docker).
{: .versoes }

<a href="https://youtu.be/8Hg9ALsxz4c">
    <img src="../.gitbook/assets/youtube.png">
</a>

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django) (branch `aula14`)

Por padrão, o Django autentica com **username** e senha. Neste tutorial vamos trocar o model de usuário por um **usuário customizado** que usa o **e-mail** no lugar do username: no `createsuperuser`, no admin e, na próxima dica, no login. Faremos isso estendendo `AbstractBaseUser`, com um manager próprio, um admin próprio e testes.

Esta dica continua o *Projeto Dicas de Django* da [Dica 13 - Dashboard com Django e Tailwind CSS](073-13-dashboard.md). O mesmo assunto já tinha aparecido num vídeo anterior do canal, citado abaixo.

## User, AbstractUser ou AbstractBaseUser?

Vale olhar o código-fonte do Django para entender de onde vem cada campo (links para o código do Django usado como referência no vídeo):

User

[https://github.com/django/django/blob/70c945d6b31b41b320e57088702077864428fdc0/django/contrib/auth/models.py#L405](https://github.com/django/django/blob/70c945d6b31b41b320e57088702077864428fdc0/django/contrib/auth/models.py#L405)

AbstractUser

[https://github.com/django/django/blob/70c945d6b31b41b320e57088702077864428fdc0/django/contrib/auth/models.py#L334](https://github.com/django/django/blob/70c945d6b31b41b320e57088702077864428fdc0/django/contrib/auth/models.py#L334)

AbstractBaseUser

[https://github.com/django/django/blob/70c945d6b31b41b320e57088702077864428fdc0/django/contrib/auth/base_user.py#L56](https://github.com/django/django/blob/70c945d6b31b41b320e57088702077864428fdc0/django/contrib/auth/base_user.py#L56)

* `User` é só uma subclasse de `AbstractUser`, sem nada a mais.
* `AbstractUser` (que herda de `AbstractBaseUser` e `PermissionsMixin`) define `username` (obrigatório e único), `first_name`, `last_name`, `email`, `is_staff`, `is_active` e `date_joined`.
* `AbstractBaseUser` tem só o essencial da autenticação: `password`, `last_login` e os métodos de senha.

Como **não queremos** o campo `username`, e sim o e-mail no lugar dele, não dá para herdar de `AbstractUser`. Vamos herdar de `AbstractBaseUser` (e de `PermissionsMixin`, que traz `is_superuser`, grupos e permissões) e declarar nós mesmos os campos que queremos.

O código foi baseado neste artigo do Simple is Better Than Complex:

Extending User Model Using a Custom Model Extending AbstractBaseUser

[https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractbaseuser](https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractbaseuser)

E no vídeo anterior do canal sobre o mesmo assunto:

Django autenticação e login com email - Django login email

[https://youtu.be/dXdMD3LBUvA](https://youtu.be/dXdMD3LBUvA)

## Criando a app accounts

```bash
git checkout -b aula14

cd backend
python ../manage.py startapp accounts
cd ..

touch backend/accounts/managers.py
```

Como a app fica dentro da pasta `backend`, ajuste o `name` no `apps.py` (o `startapp` gera só `'accounts'`):

```python
# backend/accounts/apps.py
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.accounts'
```

## Configurando o settings

Duas mudanças no `settings.py`:

* `AUTH_USER_MODEL = 'accounts.User'` diz ao Django que o model de usuário do projeto é o `User` da app `accounts` (o formato é `rótulo_da_app.Model`, e o rótulo da app é `accounts`, não `backend.accounts`).
* a app `backend.accounts` entra no `INSTALLED_APPS` **antes** do `django.contrib.admin`.

```python
# backend/settings.py
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())

AUTH_USER_MODEL = 'accounts.User'

# Application definition

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
    # minhas apps
    'backend.core',
    'backend.crm',
]
```

## O model User

```python
# backend/accounts/models.py
from __future__ import unicode_literals

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_admin = models.BooleanField(
        _('admin status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
```

O que importa aqui:

* `email` é `unique=True`, porque vai ser o identificador do usuário.
* `USERNAME_FIELD = 'email'` diz ao Django que o campo usado como "nome de usuário" (no login, no `createsuperuser`, no `authenticate`) é o e-mail.
* `REQUIRED_FIELDS = []`: campos extras que o `createsuperuser` pede além do `USERNAME_FIELD` e da senha. Nenhum.
* `is_admin` faz o papel do `is_staff` do Django: em vez de um campo `is_staff`, existe a *property* `is_staff`, que devolve `is_admin`. É ela que o admin consulta para deixar o usuário entrar.
* `has_perm` e `has_module_perms` devolvem sempre `True`, a resposta mais simples possível, como no artigo de referência. Na prática, quem decide se o usuário entra no admin é o `is_staff` (ou seja, o `is_admin`). Repare que esses dois métodos substituem os do `PermissionsMixin`, então as permissões por grupo não são verificadas.
* `get_full_name`, `get_short_name` e `email_user` são os mesmos métodos que o `User` padrão tem.
* `objects = UserManager()` é o manager que vamos escrever a seguir.

## O manager

O `BaseUserManager` padrão não sabe criar usuário sem username, então escrevemos o nosso, com `create_user` e `create_superuser` recebendo o e-mail:

```python
# backend/accounts/managers.py
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
```

* `_create_user` normaliza o e-mail (deixa o domínio em minúsculas), grava a senha com `set_password` (que guarda o hash, nunca a senha pura) e salva.
* `create_superuser` liga `is_admin` e `is_superuser` e confere se os dois ficaram `True`.
* `use_in_migrations = True` faz o manager entrar nas migrations (por isso a migration gerada importa `backend.accounts.managers`).

## O admin

O `UserAdmin` do Django faz referência a campos do `auth.User` (como `username` e `is_staff`), então criamos o nosso, herdando dele e redefinindo os campos:

```python
# backend/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'first_name', 'last_name', 'is_admin', 'is_active')  # noqa E501
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_admin',
                # 'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(User, UserAdmin)
```

* `fieldsets` são os grupos de campos da tela de edição.
* `add_fieldsets` é usado só na tela de **criação** de usuário: e-mail, senha e confirmação da senha.
* `ordering` e `search_fields` usam o e-mail no lugar do username (o `UserAdmin` padrão ordena por `username`, que não existe mais).

## Os testes

```python
# backend/accounts/tests.py
from django.test import TestCase

from backend.accounts.models import User


class TestUser(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@email.com',
            password='demodemo',
            first_name='Admin',
            last_name='Admin',
        )
        self.superuser = User.objects.create_superuser(
            email='superadmin@email.com',
            password='demodemo'
        )

    def test_user_exists(self):
        self.assertTrue(self.user)

    def test_str(self):
        self.assertEqual(self.user.email, 'admin@email.com')

    def test_return_attributes(self):
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'password',
            'is_active',
            'is_admin',
            'is_superuser',
            'date_joined',
            'last_login',
        )

        for field in fields:
            with self.subTest():
                self.assertTrue(hasattr(User, field))

    def test_user_is_authenticated(self):
        self.assertTrue(self.user.is_authenticated)

    def test_user_is_active(self):
        self.assertTrue(self.user.is_active)

    def test_user_is_staff(self):
        self.assertFalse(self.user.is_staff)

    def test_user_is_superuser(self):
        self.assertFalse(self.user.is_superuser)

    def test_superuser_is_superuser(self):
        self.assertTrue(self.superuser.is_superuser)

    def test_user_has_perm(self):
        self.assertTrue(self.user.has_perm)

    def test_user_has_module_perms(self):
        self.assertTrue(self.user.has_module_perms)

    def test_user_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), 'Admin Admin')

    def test_user_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), 'Admin')
```

## Migrations: o erro InconsistentMigrationHistory

Gere a migration e aplique:

```bash
python manage.py makemigrations
```

```
Migrations for 'accounts':
  backend/accounts/migrations/0001_initial.py
    - Create model User
```

```bash
python manage.py migrate
```

Como o banco **já tinha** as migrations do projeto aplicadas com o `auth.User` padrão (o `migrate` foi rodado nas dicas anteriores), o Django reclama:

```
django.db.migrations.exceptions.InconsistentMigrationHistory: Migration admin.0001_initial is applied before its dependency accounts.0001_initial on database 'default'.
```

A migration do admin depende do model de usuário (`AUTH_USER_MODEL`), e agora esse model está na `accounts.0001_initial`, que nunca foi aplicada. Trocar o model de usuário com o banco já criado não é simples, e é por isso que a recomendação é definir o usuário customizado **no início** do projeto. Como aqui ainda não temos dados que importam, a solução é apagar o banco e criar de novo.

No projeto, o PostgreSQL roda no Docker (veja a [Dica 7](067-07-docker-compose.md)). Remova o contêiner do banco e o volume:

```bash
docker container rm dicas_de_django_db -f
docker volume prune -f
```

```
Deleted Volumes:
dicas-de-django_pgdata

Total reclaimed space: 52.89MB
```

Atenção: o `docker volume prune -f` remove **todos** os volumes que não estão em uso por nenhum contêiner, não só o deste projeto.

Suba o banco de novo (no projeto existe o comando `make up`, que roda `docker-compose up -d`, criado na [Dica 10](070-10-makefile.md)) e rode as migrations:

```bash
make up
python manage.py migrate
```

```
Operations to perform:
  Apply all migrations: accounts, admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0001_initial... OK
  ...
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying accounts.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying sessions.0001_initial... OK
```

## Criando o superusuário

Agora o `createsuperuser` pede o **e-mail** direto, sem username:

```bash
python manage.py createsuperuser --email="admin@email.com"
```

Sem o `--email`, ele pergunta `Endereço de email:`. No vídeo foi usada uma senha bem simples, então o Django avisou que ela é curta e comum, e perguntou se queria criar assim mesmo (`Bypass password validation and create user anyway? [y/N]: y`).

## Rodando os testes

```bash
python manage.py test
```

```
Found 12 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
............
----------------------------------------------------------------------
Ran 12 tests in 3.282s

OK
Destroying test database for alias 'default'...
```

## Conferindo no admin

Rode o servidor, entre em [http://localhost:8000/admin/](http://localhost:8000/admin/) com o e-mail e a senha do superusuário e abra **Usuários > Adicionar**: o formulário pede apenas **Endereço de email**, **Senha** e **Confirmação de senha**.

Pronto: o projeto agora usa e-mail e senha no lugar de username e senha. Na próxima dica, [Dica 15 - Login com e-mail no Django](075-15-login-com-email.md), fazemos a tela de login.
