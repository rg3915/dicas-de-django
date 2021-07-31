# 17 - Criando comandos personalizados

<a href="https://youtu.be/tqr23jPrqrw">
    <img src="../.gitbook/assets/youtube.png">
</a>


Baseado em [Criando novos comandos no django-admin](http://pythonclub.com.br/criando-novos-comandos-no-django-admin.html) e na [Live 95 do Edu Live de Python](https://youtu.be/cyxky2QJlwg?t=3482).

### Criando as pastas

Para criarmos um novo comando precisamos das seguintes pastas:

```
core
├── management
│   ├── __init__.py
│   ├── commands
│   │   ├── __init__.py
│   │   ├── novocomando.py
```

No nosso caso, teremos 2 novos comandos, então digite, estando na pasta myproject

```
mkdir -p core/management/commands
touch core/management/__init__.py
touch core/management/commands/{__init__.py,hello.py,search.py}
```


```python
# hello.py
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Print hello world.'

    def add_arguments(self, parser):
        # Argumento nomeado (opcional)
        parser.add_argument(
            '--awards', '-a',
            action='store_true',
            help='Ajuda da opção aqui.'
        )

    def handle(self, *args, **options):
        self.stdout.write('Hello world.')
        if options['awards']:
            self.stdout.write('Awards')
```


```python
# search.py
from django.core.management.base import BaseCommand

from myproject.core.models import Article


class Command(BaseCommand):
    help = """Localiza um artigo pelo título ou sub-título."""

    def add_arguments(self, parser):
        parser.add_argument(
            '--title', '-t',
            dest='title',
            default=None,
            help='Localiza um artigo pelo título.'
        )
        parser.add_argument(
            '--subtitle', '-sub',
            dest='subtitle',
            default=None,
            help='Localiza um artigo pelo sub-título.'
        )

    def handle(self, title=None, subtitle=None, **options):
        """ dicionário de filtros """
        self.verbosity = int(options.get('verbosity'))

        filters = {
            'title__icontains': title,
            'subtitle__icontains': subtitle,
        }

        filter_by = {
            key: value for key,
            value in filters.items() if value is not None
        }
        queryset = Article.objects.filter(**filter_by)

        if self.verbosity > 0:
            for article in queryset:
                self.stdout.write("{0} {1}".format(
                    article.title, article.subtitle))
            self.stdout.write(f'\n{queryset.count()} artigos localizados.')
```
