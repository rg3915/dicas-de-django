# Dica 17 - Criando comandos personalizados

**Versões usadas no vídeo:** Django 2.2.13 e Python 3.8.
{: .versoes }

<a href="https://youtu.be/tqr23jPrqrw">
    <img src="../.gitbook/assets/youtube.png">
</a>


Baseado em [Criando novos comandos no django-admin](http://pythonclub.com.br/criando-novos-comandos-no-django-admin.html) e na [Live 95 do Edu Live de Python](https://youtu.be/cyxky2QJlwg?t=3482).

Quando digitamos `python manage.py`, sem nada depois, aparece a lista de subcomandos disponíveis, agrupados por app:

```bash
python manage.py
```

```
[django]
    check
    compilemessages
    ...
    makemigrations
    migrate
    ...
    runserver
    ...

[django_extensions]
    admin_generator
    ...
    shell_plus
    show_urls
    ...
```

Os do grupo `[django]` vêm com o próprio Django (`runserver`, `makemigrations`, `migrate`...), e outros vêm das bibliotecas instaladas, como o `django-extensions`, de onde eu gosto muito do `shell_plus` e do `show_urls`. Neste tutorial vamos criar os **nossos próprios** comandos:

* `hello`: imprime "Hello world." e tem uma opção `--awards`, para mostrar como funcionam os argumentos;
* `search`: busca artigos no banco pelo título e/ou pelo sub-título, direto do terminal.

## Pré-requisitos

O projeto das dicas anteriores (repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django)), com o `manage.py` na raiz, o app `core` dentro da pasta `myproject` e o modelo `Article` com os campos `title` e `subtitle`:

```python
# myproject/core/models.py
class Article(models.Model):
    ...
    title = models.CharField('título', max_length=200)
    subtitle = models.CharField('sub-título', max_length=200)
    ...
```

Os artigos cadastrados no vídeo são "Dicas de Python", "Dicas de Python 2", "Django Admin", "Django Autoslug", "Django Boilerplate" e "Django extensions" (o sub-título de cada um é igual ao título).

## Criando as pastas

Para criarmos um novo comando precisamos das seguintes pastas dentro do app:

```
core
├── management
│   ├── __init__.py
│   ├── commands
│   │   ├── __init__.py
│   │   ├── novocomando.py
```

* `management`, no singular, e `commands`, no plural, cada uma com o seu `__init__.py` (dois underlines antes e depois), para que o Python as reconheça como pacotes.
* Cada arquivo `.py` dentro de `commands` vira um comando, com o mesmo nome do arquivo: `novocomando.py` vira `python manage.py novocomando`.
* O app precisa estar no `INSTALLED_APPS`.

No nosso caso, teremos 2 novos comandos, então digite, estando na pasta myproject

```
mkdir -p core/management/commands
touch core/management/__init__.py
touch core/management/commands/{__init__.py,hello.py,search.py}
```

O `-p` do `mkdir` cria a pasta `management` e a subpasta `commands` de uma vez, e as chaves do último `touch` (sem espaço depois da vírgula) criam os três arquivos num comando só. O resultado:

```
core
├── management
│   ├── commands
│   │   ├── hello.py
│   │   ├── __init__.py
│   │   └── search.py
│   └── __init__.py
...
```

## O comando hello

O mínimo que um comando precisa é uma classe chamada `Command`, que herda de `BaseCommand`, com um método `handle`, que é o que roda quando você chama o comando:

```python
# myproject/core/management/commands/hello.py
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Print hello world.'

    def handle(self, *args, **options):
        self.stdout.write('Hello world.')
```

* `help` é o texto de ajuda do comando (aparece no `--help`).
* Para escrever na tela use `self.stdout.write()` em vez de `print()`: assim a saída respeita as opções do Django (como `--no-color`) e pode ser capturada nos testes.

Volte para a pasta do `manage.py` e rode `python manage.py` de novo: o comando já aparece na lista, num grupo com o nome do app:

```
[core]
    hello
    search
```

E já funciona:

```bash
python manage.py hello
```

```
Hello world.
```

## Acrescentando um argumento

Os argumentos são definidos no método `add_arguments`, que recebe um `parser` do `argparse` do Python:

```python
# myproject/core/management/commands/hello.py
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Print hello world.'

    def add_arguments(self, parser):
        # Argumento nomeado
        parser.add_argument(
            '--awards', '-a',
            action='store_true',
            help='Ajuda da opção awards.'
        )

    def handle(self, *args, **options):
        self.stdout.write('Hello world.')
        if options['awards']:
            self.stdout.write('Awards')
```

* `'--awards', '-a'`: o nome longo e a forma abreviada da opção. Por começar com traço, é um argumento nomeado, ou seja, opcional.
* `action='store_true'`: a opção não recebe valor; se ela for passada, `options['awards']` vale `True`, senão `False`.
* No `handle`, os argumentos chegam no dicionário `options`.

O `--help` mostra a nova opção:

```bash
python manage.py hello --help
```

```
usage: manage.py hello [-h] [--awards] [--version] [-v {0,1,2,3}]
                       [--settings SETTINGS] [--pythonpath PYTHONPATH]
                       [--traceback] [--no-color] [--force-color]

Print hello world.

optional arguments:
  -h, --help            show this help message and exit
  --awards, -a          Ajuda da opção awards.
  --version             show program's version number and exit
  -v {0,1,2,3}, --verbosity {0,1,2,3}
  ...
```

Repare que, além da nossa, todo comando ganha de graça as opções padrão do Django, como `--verbosity`, `--settings` e `--traceback`.

```bash
python manage.py hello -a
```

```
Hello world.
Awards
```

## O comando search

Agora um comando que faz algo útil: localiza artigos pelo título ou pelo sub-título.

```python
# myproject/core/management/commands/search.py
from django.core.management.base import BaseCommand
from myproject.core.models import Article


class Command(BaseCommand):
    help = 'Localiza um artigo pelo título ou sub-título.'

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
                self.stdout.write(f"{article.title} {article.subtitle}")
            self.stdout.write(f'\n{queryset.count()} artigos localizados.')
```

Vamos por partes:

* **Argumentos**: `--title` (ou `-t`) e `--subtitle` (ou `-sub`). Agora eles recebem um valor (não têm `action='store_true'`). O `dest` é o nome com que o valor chega no `handle`, e `default=None` indica que a opção não foi passada.
* **`handle(self, title=None, subtitle=None, **options)`**: como os argumentos chegam como parâmetros nomeados, dá para recebê-los direto na assinatura do método. O resto (como `verbosity`) continua em `options`.
* **`self.verbosity`**: o nível de verbosidade da opção padrão `-v` (0, 1, 2 ou 3; o padrão é 1). Com `-v 0` o comando não imprime nada.
* **`filters`**: um dicionário em que a chave é o lookup do ORM (`title__icontains`, contém, sem diferenciar maiúsculas e minúsculas) e o valor é o que foi digitado.
* **`filter_by`**: um *dict comprehension* que fica só com os filtros que foram de fato informados (`value is not None`). Se você passar só `-t`, o filtro de sub-título é descartado.
* **`Article.objects.filter(**filter_by)`**: o `**` desempacota o dicionário em argumentos nomeados. `filter(**{'title__icontains': 'django'})` é o mesmo que `filter(title__icontains='django')`. Isso permite montar o filtro dinamicamente. Se nenhum filtro for passado, o dicionário fica vazio e o comando lista todos os artigos.
* No fim, imprimimos título e sub-título de cada artigo e o total encontrado.

O f-string (`f"..."`) exige Python 3.6 ou superior; no vídeo foi usado o Python 3.8.

## Testando o search

O `--help` mostra a descrição e as opções:

```bash
python manage.py search --help
```

```
usage: manage.py search [-h] [--title TITLE] [--subtitle SUBTITLE] [--version]
                        [-v {0,1,2,3}] [--settings SETTINGS]
                        [--pythonpath PYTHONPATH] [--traceback] [--no-color]
                        [--force-color]

Localiza um artigo pelo título ou sub-título.

optional arguments:
  -h, --help            show this help message and exit
  --title TITLE, -t TITLE
                        Localiza um artigo pelo título.
  --subtitle SUBTITLE, -sub SUBTITLE
                        Localiza um artigo pelo sub-título.
  ...
```

Buscando pelo título:

```bash
python manage.py search -t django
```

```
Django Admin Django Admin
Django Autoslug Django Autoslug
Django Boilerplate Django Boilerplate
Django extensions Django extensions

4 artigos localizados.
```

Pelo sub-título (no vídeo, a primeira tentativa foi com `pyton`, escrito errado, e não encontrou nada):

```bash
python manage.py search -sub pyton
```

```

0 artigos localizados.
```

```bash
python manage.py search -sub python
```

```
Dicas de Python Dicas de Python
Dicas de Python 2 Dicas de Python 2

2 artigos localizados.
```

E os dois juntos, que são combinados com "e":

```bash
python manage.py search -t python -sub 2
```

```
Dicas de Python 2 Dicas de Python 2

1 artigos localizados.
```

(No vídeo aparece também um aviso `core.Article.id: (HashidField.W001) 'salt' is not set` antes da saída. Ele vem do `django-hashid-field` usado no modelo de uma dica anterior e não tem relação com o comando.)

Essas saídas foram conferidas rodando os comandos com Django 2.2 e Python 3.8.

## Na Live 95

Na [Live 95 do Edu Live de Python](https://youtu.be/cyxky2QJlwg?t=3482), sobre o ORM do Django, a mesma estrutura (`management/commands` com os `__init__.py`) foi usada para um comando `import_lives`, que lê um arquivo CSV com `csv.DictReader` e grava os registros no banco com o ORM. É um uso muito comum de comandos personalizados: importar dados, popular o banco para testes, rodar rotinas agendadas no `cron` etc.
