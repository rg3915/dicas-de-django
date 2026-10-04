# Dica 2 - Django extensions

**Versões usadas no vídeo:** Django 2.2.13, django-extensions 2.2.9 e Python 3.8.2.
{: .versoes }

<a href="https://youtu.be/qUKzDSSuh2w">
    <img src="../.gitbook/assets/youtube.png">
</a>

Documentação: [https://django-extensions.readthedocs.io/en/latest/index.html](https://django-extensions.readthedocs.io/en/latest/index.html)

O [django-extensions](https://django-extensions.readthedocs.io/en/latest/index.html) é uma coleção de extensões para o Django: dezenas de comandos novos para o `manage.py`, campos extras para os models, extensões para o admin e mais. É daquelas bibliotecas que entram em praticamente todo projeto, porque aumentam a produtividade no dia a dia.

Nesta dica vamos instalar o django-extensions e usar os dois comandos que o autor mais usa: `show_urls` e `shell_plus`.

## Pré-requisitos

Um projeto Django qualquer. No vídeo, o projeto foi criado com o `boilerplatesimple.sh` da [Dica 1](000-django-boilerplate-e-cookiecutter-django.md):

```bash
mkdir /tmp/c
cd /tmp/c

curl https://gist.githubusercontent.com/rg3915/b363f5c4a998f42901705b23ccf4b8e8/raw/b759d5a4c1dd471a1c1851c2a9e7cbc705f11ac1/boilerplatesimple.sh -o boilerplatesimple.sh
source boilerplatesimple.sh
```

O script cria a virtualenv, instala o Django 2.2.13 e cria o projeto `myproject` com o app `core` e o superusuário `admin`.

## Instalação

```bash
pip install django-extensions
```

O boilerplate já instala o django-extensions, por isso no vídeo o `pip` responde que ele já está instalado:

```
Requirement already satisfied: django-extensions in ./.venv/lib/python3.8/site-packages (2.2.9)
Requirement already satisfied: six>=1.2 in ./.venv/lib/python3.8/site-packages (from django-extensions) (1.15.0)
```

Depois, acrescente `django_extensions` (com *underline*) ao `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = (
    ...
    'django_extensions',
)
```

No projeto do boilerplate ele já está lá:

```python
# myproject/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'myproject.core'
]
```

## Os novos comandos

Rode o `manage.py` sem argumentos (ou `python manage.py help`) para ver todos os comandos disponíveis:

```bash
python manage.py
```

Além dos comandos que o Django já tem (`[auth]`, `[django]`, `[sessions]`, `[staticfiles]` etc.), aparece uma seção nova, `[django_extensions]`:

```
[django_extensions]
    admin_generator
    clean_pyc
    clear_cache
    compile_pyc
    create_command
    create_jobs
    create_template_tags
    delete_squashed_migrations
    describe_form
    drop_test_database
    dumpscript
    export_emails
    find_template
    generate_password
    generate_secret_key
    graph_models
    mail_debug
    merge_model_instances
    notes
    passwd
    pipchecker
    print_settings
    print_user_for_session
    reset_db
    reset_schema
    runjob
    runjobs
    runprofileserver
    runscript
    runserver_plus
    set_default_site
    set_fake_emails
    set_fake_passwords
    shell_plus
    show_template_tags
    show_templatetags
    show_urls
    sqlcreate
    sqldiff
    sqldsn
    sync_s3
    syncdata
    unreferenced_files
    update_permissions
    validate_templates
```

Cada um está explicado na [documentação dos comandos](https://django-extensions.readthedocs.io/en/latest/command_extensions.html).

## show_urls

O `show_urls` lista todas as URLs do projeto, com a view que atende cada uma e o nome da rota. É ótimo para mapear as URLs de um projeto que você não conhece:

```bash
python manage.py show_urls
```

Neste projeto ainda só existem as URLs do admin:

```
/admin/	django.contrib.admin.sites.index	admin:index
/admin/<app_label>/	django.contrib.admin.sites.app_index	admin:app_list
/admin/auth/group/	django.contrib.admin.options.changelist_view	admin:auth_group_changelist
/admin/auth/group/<path:object_id>/	django.views.generic.base.RedirectView
/admin/auth/group/<path:object_id>/change/	django.contrib.admin.options.change_view	admin:auth_group_change
/admin/auth/group/<path:object_id>/delete/	django.contrib.admin.options.delete_view	admin:auth_group_delete
/admin/auth/group/<path:object_id>/history/	django.contrib.admin.options.history_view	admin:auth_group_history
/admin/auth/group/add/	django.contrib.admin.options.add_view	admin:auth_group_add
/admin/auth/group/autocomplete/	django.contrib.admin.options.autocomplete_view	admin:auth_group_autocomplete
/admin/auth/user/	django.contrib.admin.options.changelist_view	admin:auth_user_changelist
/admin/auth/user/<id>/password/	django.contrib.auth.admin.user_change_password	admin:auth_user_password_change
/admin/auth/user/<path:object_id>/	django.views.generic.base.RedirectView
/admin/auth/user/<path:object_id>/change/	django.contrib.admin.options.change_view	admin:auth_user_change
/admin/auth/user/<path:object_id>/delete/	django.contrib.admin.options.delete_view	admin:auth_user_delete
/admin/auth/user/<path:object_id>/history/	django.contrib.admin.options.history_view	admin:auth_user_history
/admin/auth/user/add/	django.contrib.auth.admin.add_view	admin:auth_user_add
/admin/auth/user/autocomplete/	django.contrib.admin.options.autocomplete_view	admin:auth_user_autocomplete
/admin/jsi18n/	django.contrib.admin.sites.i18n_javascript	admin:jsi18n
/admin/login/	django.contrib.admin.sites.login	admin:login
/admin/logout/	django.contrib.admin.sites.logout	admin:logout
/admin/password_change/	django.contrib.admin.sites.password_change	admin:password_change
/admin/password_change/done/	django.contrib.admin.sites.password_change_done	admin:password_change_done
/admin/r/<int:content_type_id>/<path:object_id>/	django.contrib.contenttypes.views.shortcut	admin:view_on_site
```

São três colunas: a URL, a view e o nome (`namespace:nome`), o mesmo que você usa no `{% url %}` e no `reverse()`.

## shell_plus

O `shell_plus` é o `shell` do Django com uma vantagem: ele já importa automaticamente todos os models de todos os apps instalados e os módulos mais usados do Django. Não é preciso digitar nenhum `import`:

```bash
python manage.py shell_plus
```

```
# Shell Plus Model Imports
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
# Shell Plus Django Imports
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When, Exists, OuterRef, Subquery
from django.utils import timezone
from django.urls import reverse
Python 3.8.2 (default, Apr 29 2020, 23:19:54)
[GCC 9.2.1 20191008] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>>
```

Repare que o `User` já foi importado (`from django.contrib.auth.models import Group, Permission, User`). Então dá para consultar direto:

```python
>>> User.objects.all()
<QuerySet [<User: admin>]>
```

Quando você criar models nos seus apps, eles também aparecem na seção `# Shell Plus Model Imports`.

## Conclusão

Com duas linhas (o `pip install` e o `INSTALLED_APPS`) você ganha dezenas de comandos. Os dois que mais ajudam no dia a dia:

```
python manage.py show_urls
```

```
python manage.py shell_plus
```
