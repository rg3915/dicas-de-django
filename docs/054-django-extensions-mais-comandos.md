# Dica 54 - django-extensions - mais comandos

**Versões usadas no vídeo:** Django 3.2, django-extensions 3.1, Python 3.9 e IPython 7.27.
{: .versoes }

<a href="https://youtu.be/pguupq-s70M">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

Doc: [https://django-extensions.readthedocs.io/en/latest/](https://django-extensions.readthedocs.io/en/latest/)

O django-extensions é um pacote que acrescenta dezenas de comandos ao `manage.py`. Nesta dica veremos mais comandos do django-extensions, todos listados na seção [Command Extensions](https://django-extensions.readthedocs.io/en/latest/command_extensions.html) da documentação: `shell_plus`, `admin_generator`, `clean_pyc`, `create_command`, `create_template_tags`, `show_template_tags`, `generate_password`, `generate_secret_key`, `graph_models`, `list_model_info`, `list_signals`, `print_settings` e `show_urls`.

## Pré-requisitos

O vídeo usa o projeto do repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django): o pacote `myproject` com as apps `core`, `product`, `ecommerce`, `event`, `travel` etc. Para acompanhar, basta qualquer projeto Django com pelo menos uma app e um modelo. Nos exemplos usamos a app `product` com o modelo `Product`:

```python
# myproject/product/models.py
from django.db import models


class Product(models.Model):
    title = models.CharField('título', max_length=100, unique=True)
    price = models.DecimalField('preço', max_digits=7, decimal_places=2)
    manufacturing_date = models.DateField('data de fabricação', null=True, blank=True)  # noqa E501
    due_date = models.DateField('data de vencimento', null=True, blank=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        return self.title
```

## Instalação

O django-extensions já estava instalado no projeto; no vídeo ele foi atualizado com `-U`:

```bash
pip install -U django-extensions
```

No `requirements.txt` do projeto, as versões ficaram assim:

```
Django==3.2.*
django-extensions==3.1.*
```

Depois acrescente `django_extensions` ao `INSTALLED_APPS`:

```python
# myproject/settings.py
INSTALLED_APPS = [
    'myproject.core',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    ...
    'django_extensions',
    ...
]
```

Para ver todos os comandos disponíveis, digite apenas:

```bash
python manage.py
```

Na lista aparece a seção `[django_extensions]` com os comandos novos:

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
    list_model_info
    list_signals
    mail_debug
    merge_model_instances
    notes
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
    ...
```

## shell_plus

Roda o shell do Django importando todos os pacotes essenciais. É o comando que eu mais uso.

```bash
python manage.py shell_plus
```

Ele importa automaticamente todos os modelos do projeto (inclusive os do Django, como `User`, `Group` e `Permission`) e os utilitários mais usados, como `settings`, `transaction`, `timezone`, `reverse` e as funções de agregação de `django.db.models`. No vídeo a saída foi esta (com o IPython instalado, o shell_plus usa o IPython):

```
# Shell Plus Model Imports
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from myproject.core.models import Article, Category, Person
from myproject.ecommerce.models import Order, OrderItems
from myproject.event.models import Room
from myproject.product.models import Product
from myproject.travel.models import Travel
# Shell Plus Django Imports
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When
from django.utils import timezone
from django.urls import reverse
from django.db.models import Exists, OuterRef, Subquery
Python 3.9.6 (default, Jul  5 2021, 08:48:45)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.27.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]:
```

Como `Product` já foi importado, dá para usá-lo direto:

```python
In [1]: Product.objects.all()
Out[1]: <QuerySet [<Product: After lot hold discover stuff just manager.>, ...]>
```

Para sair, `Ctrl+D`.

## admin_generator

Gera uma classe no Admin para a app selecionada, lendo os campos dos modelos dela.

```bash
python manage.py admin_generator product
```

Saída:

```python
# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'manufacturing_date', 'due_date')
    list_filter = ('manufacturing_date', 'due_date')
```

Repare que ele coloca todos os campos em `list_display` e os campos de data em `list_filter`. Para gravar o resultado direto no arquivo, redirecione a saída com `>>` (acrescenta no fim do arquivo):

```bash
python manage.py admin_generator product >> myproject/product/admin.py
```

Como o `admin.py` do vídeo já tinha um `ProductAdmin`, o código gerado ficou embaixo do existente, e o trecho repetido foi apagado. Num `admin.py` vazio, o resultado já fica pronto para usar.

## clean_pyc

Remove todos os arquivos `*.pyc` do projeto (os bytecodes que o Python grava em `__pycache__`).

```bash
python manage.py clean_pyc
```

No vídeo, o `tree` antes do comando mostrava vários `*.cpython-39.pyc`; depois do `clean_pyc` não sobrou nenhum.

## create_command

Cria um novo comando do Django (um *management command*) dentro de uma app.

```bash
python manage.py create_command core -n novocomando
```

O `-n` (ou `--name`) define o nome do comando. Ele cria as pastas `management/commands` com os `__init__.py`, se ainda não existirem, e o arquivo do comando com um esqueleto básico para você implementar:

```python
# myproject/core/management/commands/novocomando.py
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('sample', nargs='+')

    def handle(self, *args, **options):
        raise NotImplementedError()
```

Depois de implementar o `handle`, o comando roda com `python manage.py novocomando`.

## create_template_tags

Cria um novo arquivo de template tags em uma app.

```bash
python manage.py create_template_tags core
```

Sem o nome, ele cria a pasta `templatetags` (se não existir) e um arquivo com o nome da app seguido de `_tags`, no caso `core_tags.py`:

```python
# myproject/core/templatetags/core_tags.py
from django import template

register = template.Library()
```

Com `-n` você escolhe o nome do arquivo:

```bash
python manage.py create_template_tags core -n lorem_tags
```

Isso cria `myproject/core/templatetags/lorem_tags.py`, com o mesmo conteúdo. Para escrever as suas tags, veja a [Dica 34 - Django custom template tags](034-django-custom-template-tags.md).

## show_template_tags

Lista todos os template tags e filtros do projeto, app por app, com a docstring de cada um.

```bash
python manage.py show_template_tags
```

Ele mostra as bibliotecas que você carrega com `{% load ... %}` e, para cada tag ou filtro, a docstring. No vídeo, a app `core` aparece assim (trecho):

```
App: myproject.core
    load: model_name_tags
        Tag: model_name
            Django template filter which returns the verbose name of a model.
        Tag: model_name_plural
            Django template filter which returns the plural verbose name of a model.
    load: url_replace
        Tag: url_replace
    load: core_tags
    load: usergroup_tags
        Filter: name_group
            Retorna o nome do grupo do usuário.

            Usage:

            {% load usergroup_tags %}

            {{ user|name_group }}

        Filter: has_group
            Verifica se este usuário pertence a um grupo.

            Usage:

            {% load usergroup_tags %}
            ...
```

Repare que `url_replace` não tem docstring, então só o nome aparece; e `core_tags`, recém-criado, não tem nenhuma tag. As docstrings vêm do próprio código, por exemplo:

```python
# myproject/core/templatetags/usergroup_tags.py
from django import template

register = template.Library()


@register.filter('name_group')
def name_group(user):
    '''
    Retorna o nome do grupo do usuário.

    Usage:

    {% load usergroup_tags %}

    {{ user|name_group }}
    '''
    _groups = user.groups.first()
    if _groups:
        return _groups.name
    return ''


@register.filter('has_group')
def has_group(user, group_name):
    '''
    Verifica se este usuário pertence a um grupo.

    Usage:

    {% load usergroup_tags %}

    {% if user|has_group:"Nome do grupo" %}
        {{ user|name_group }}
    {% endif %}
    '''
    if user:
        groups = user.groups.all().values_list('name', flat=True)
        return True if group_name in groups else False
    return False
```

Por isso vale a pena documentar as suas template tags: o `show_template_tags` vira uma documentação de graça.

## generate_password

Gera uma senha aleatória.

```bash
python manage.py generate_password
```

```
R2ZcV7wdQW
```

Com `--length` você define o tamanho:

```bash
python manage.py generate_password --length 32
```

```
dA8C5Qyja3YUTSunpmfA335c8Zr48XTU
```

## generate_secret_key

Gera uma nova chave secreta, para usar no `SECRET_KEY` do `settings.py` (ou no `.env`).

```bash
python manage.py generate_secret_key
```

```
_p07+-^01u1s%sfxo#+l@yqod-^ze*i2+g-$x)ug)%i9p-n6(f
```

A cada execução sai uma senha e uma chave diferentes.

## graph_models

O `graph_models` gera o diagrama dos modelos do projeto. Ele tem um vídeo só para ele (link da descrição do vídeo):

[https://youtu.be/99dOVsDBUxg](https://youtu.be/99dOVsDBUxg)

O passo a passo está na [Dica 36 - Visualizando seus modelos com graph_models](036-django-visualizando-seus-modelos-com-graph-models.md).

## list_model_info

Lista as informações de um modelo: os campos e os métodos públicos.

```bash
python manage.py list_model_info --model product.Product
```

```
product.Product
    Fields:
        product_items -
        id -
        title -
        price -
        manufacturing_date -
        due_date -
    Methods (non-private/internal):

Total Models Listed: 1
```

O `product_items` aparece porque, no projeto do vídeo, o modelo `OrderItems` da app `ecommerce` tem uma chave estrangeira para `Product` com `related_name='product_items'`. Com `--field-class` ele mostra também o tipo de cada campo:

```bash
python manage.py list_model_info --model product.Product --field-class
```

```
product.Product
    Fields:
        id - BigAutoField
        title - CharField
        price - DecimalField
        manufacturing_date - DateField
        due_date - DateField
    Methods (non-private/internal):

Total Models Listed: 1
```

O `id` é `BigAutoField` porque o projeto tem `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'` no `settings.py`.

## list_signals

Lista os sinais (*signals*) registrados no projeto.

```bash
python manage.py list_signals
```

O projeto do vídeo não tinha nenhum sinal, por isso o comando não retornou nada.

## print_settings

Mostra todas as configurações do projeto, incluindo os valores padrão do Django que você não alterou no `settings.py`.

```bash
python manage.py print_settings
```

```
ABSOLUTE_URL_OVERRIDES                   = {}
ADMINS                                   = []
ALLOWED_HOSTS                            = []
APPEND_SLASH                             = True
AUTHENTICATION_BACKENDS                  = ['django.contrib.auth.backends.ModelBackend']
AUTH_USER_MODEL                          = 'auth.User'
...
```

## show_urls

Lista todas as URLs do projeto: o caminho, a view que atende e o nome da rota.

```bash
python manage.py show_urls
```

Trecho da saída no vídeo:

```
/admin/travel/travel/                           django.contrib.admin.options.changelist_view  admin:travel_travel_changelist
/admin/travel/travel/<path:object_id>/          django.views.generic.base.RedirectView
/admin/travel/travel/<path:object_id>/change/   django.contrib.admin.options.change_view      admin:travel_travel_change
/admin/travel/travel/<path:object_id>/delete/   django.contrib.admin.options.delete_view      admin:travel_travel_delete
/admin/travel/travel/<path:object_id>/history/  django.contrib.admin.options.history_view     admin:travel_travel_history
/admin/travel/travel/add/                       django.contrib.admin.options.add_view         admin:travel_travel_add
/articles/                                      myproject.core.views.article_list             core:article_list
/articles/filter/                               myproject.core.views.article_filter_list      core:article_filter_list
/articles/json/                                 myproject.core.views.article_json             core:article_json
/persons/                                       myproject.core.views.PersonListView           core:person_list
/persons/create/                                myproject.core.views.person_create            core:person_create
/travel/                                        myproject.travel.views.TravelListView         travel:travel_list
/travel/create/                                 myproject.travel.views.TravelCreateView       travel:travel_create
```

É muito útil para descobrir o nome de uma rota para usar no `{% url %}` ou no `reverse()`.

## Conclusão

Com o django-extensions instalado, o `manage.py` ganha atalhos para tarefas do dia a dia: um shell com tudo importado, geração de admin, de comandos e de template tags, senhas e chaves secretas, e várias formas de inspecionar o projeto (modelos, sinais, settings e URLs). Na próxima dica veremos o [runserver_plus](055-runserver_plus.md), também do django-extensions.
