# 14 - Django Custom User com e-mail

User

https://github.com/django/django/blob/70c945d6b31b41b320e57088702077864428fdc0/django/contrib/auth/models.py#L405

AbstractUser

https://github.com/django/django/blob/70c945d6b31b41b320e57088702077864428fdc0/django/contrib/auth/models.py#L334

AbstractBaseUser

https://github.com/django/django/blob/70c945d6b31b41b320e57088702077864428fdc0/django/contrib/auth/base_user.py#L56

Extending User Model Using a Custom Model Extending AbstractBaseUser

https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractbaseuser

Django autenticação e login com email - Django login email

https://youtu.be/dXdMD3LBUvA

Crie a app `accounts`

```
cd backend
python ../manage.py startapp accounts
cd ..
```

Edite `settings.py`

```python
# settings.py

AUTH_USER_MODEL = 'accounts.User'

INSTALLED_APPS = [
    'backend.accounts',  # <<<
    'django.contrib.admin',
    ...
]
```

Edite `accounts/apps.py`

```python
# accounts/apps.py
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.accounts'
```

Edite `accounts/models.py`

```python
# accounts/models.py
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

Edite `accounts/admin.py`

```python
# accounts/admin.py
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

Edite `accounts/managers.py`

```python
# accounts/managers.py
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

Edite `accounts/tests.py`

```python
# accounts/tests.py
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

```
python manage.py makemigrations
python manage.py migrate
python manage.py test
```

Erro

```
django.db.migrations.exceptions.InconsistentMigrationHistory: Migration admin.0001_initial is applied before its dependency accounts.0001_initial on database 'default'.
```

Delete o banco de dados e recrie novamente.

```
docker container rm dicas_de_django_db -f
docker volume prune -f

python manage.py migrate
python manage.py createsuperuser --email="admin@email.com"

python manage.py test
```
