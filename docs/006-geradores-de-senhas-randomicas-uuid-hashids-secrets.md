# Dica 6 - Geradores de senhas randômicas - uuid, hashids, secrets

**Versões usadas no vídeo:** Django 2.2.13, Python 3.8.2, shortuuid 1.0.1, hashids 1.2.0 e django-hashid-field 3.1.3.
{: .versoes }

<a href="https://youtu.be/-3znAePkMqY">
    <img src="../.gitbook/assets/youtube.png">
</a>

Esta dica mostra várias formas de gerar valores aleatórios: identificadores únicos, ids "embaralhados" para não expor a chave primária na URL, senhas e tokens. Ela foi gravada em duas partes:

* **Parte 1** (vídeo acima): `uuid`, `shortuuid`, `hashids` e `django-hashid-field`, aplicados num projeto Django.
* **Parte 2** (vídeo da seção "Parte 2", mais abaixo): comandos do terminal Linux, `random`, `string` e `secrets` do Python, e o `get_random_string` do Django para gerar a `SECRET_KEY`.

## Pré-requisitos

O vídeo usa o projeto das dicas anteriores (repositório [rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)), com um app `core` dentro de `myproject`, o `django-extensions` (para o `shell_plus`, veja a [Dica 2](002-django-extensions.md)) e o `django-autoslug` (veja a [Dica 3](003-django-bulk_create-e-django-autoslug.md)). Na época, o `requirements.txt` do projeto era este:

```
# requirements.txt
dj-database-url==0.5.0
django-autoslug==1.9.7
django-daterange-filter==1.3.0
django-extensions==2.2.9
django-hashid-field==3.1.3
django-widget-tweaks==1.4.8
Django==2.2.13
hashids==1.2.0
python-decouple==3.3
shortuuid==1.0.1
```

O ponto de partida são estes dois models:

```python
# myproject/core/models.py
from django.db import models
from autoslug import AutoSlugField


class Article(models.Model):
    title = models.CharField('título', max_length=200)
    subtitle = models.CharField('sub-título', max_length=200)
    slug = AutoSlugField(populate_from='title')
    category = models.ForeignKey(
        'Category',
        related_name='categories',
        verbose_name='categoria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    published_date = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'artigo'
        verbose_name_plural = 'artigos'

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField('título', max_length=50, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.title
```

## uuid

Documentação: [https://docs.python.org/3/library/uuid.html](https://docs.python.org/3/library/uuid.html)

O módulo `uuid` faz parte da biblioteca padrão do Python. A função mais usada é a `uuid4()`, que gera um UUID aleatório:

```python
>>> import uuid
>>> uuid.uuid4()
UUID('e92a8cad-4aa0-4062-af9b-448e804422eb')
>>> uuid.uuid4().hex
'cb90933c7ada49399663422b796775f3'
>>> uuid.uuid4().hex
'65d536f10bb44e42bcadc4c640ad0242'
```

O `.hex` devolve o valor em hexadecimal, sem os tracinhos. Cada chamada gera um valor diferente.

### Um slug com UUID no model

No Django, um uso comum é ter um campo `slug` com um UUID, para identificar o registro na URL sem expor o `id`. Para reaproveitar o campo em vários models, criamos um model **abstrato**, que não vira tabela e funciona como um "molde" para os outros:

```python
# myproject/core/models.py
import uuid
from django.db import models
from autoslug import AutoSlugField


class UuidModel(models.Model):
    slug = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True
```

A `Category` passa a herdar de `UuidModel` em vez de `models.Model`, e com isso ganha o campo `slug`:

```python
# myproject/core/models.py
class Category(UuidModel):
    title = models.CharField('título', max_length=50, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.title
```

* `unique=True`: não pode haver dois slugs iguais.
* `editable=False`: o campo não aparece nos formulários (nem no Admin).
* `default=uuid.uuid4`: repare que é a **função**, sem parênteses. O Django chama a função a cada registro novo.

Crie a migração:

```bash
python manage.py makemigrations
```

```
Migrations for 'core':
  myproject/core/migrations/0002_category_slug.py
    - Add field slug to category
```

### O erro do `uuid.uuid4()` com parênteses

No vídeo, o model foi escrito primeiro com `default=uuid.uuid4()`, **com** parênteses. Assim o UUID é gerado uma vez só, quando o Python carrega o `models.py`, e esse valor fixo vai parar na migração:

```python
# myproject/core/migrations/0002_category_slug.py
field=models.UUIDField(default=uuid.UUID('4194db20-ff52-4852-a426-516080e18490'), editable=False, unique=True),
```

Depois do `python manage.py migrate`, ao criar várias categorias de uma vez no `python manage.py shell_plus`:

```python
>>> categories = [
...     'dicas',
...     'django',
...     'python',
... ]
>>>
>>> aux = []
>>>
>>> for category in categories:
...     obj = Category(title=category)
...     aux.append(obj)
...
>>> Category.objects.bulk_create(aux)
```

todas recebem o mesmo slug, e o banco recusa:

```
django.db.utils.IntegrityError: UNIQUE constraint failed: core_category.slug
```

A correção é tirar os parênteses (`default=uuid.uuid4`), gerar uma nova migração e aplicá-la:

```bash
python manage.py makemigrations
python manage.py migrate
```

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, core, sessions
Running migrations:
  Applying core.0003_auto_20200614_0855... OK
```

A migração nova troca o valor fixo pela função:

```python
# myproject/core/migrations/0003_auto_20200614_0855.py
field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
```

Rodando de novo o mesmo código no `shell_plus`, o `bulk_create` funciona e cada categoria ganha o seu UUID.

### Vendo o slug no Admin

Para enxergar o slug na lista de categorias, acrescente o `list_display` no Admin:

```python
# myproject/core/admin.py
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    actions = None

    def has_add_permission(self, request, obj=None):
        return False

    if not settings.DEBUG:
        def has_delete_permission(self, request, obj=None):
            return False
```

Rode `python manage.py runserver`, abra `http://localhost:8000/admin/core/category/` e veja que cada categoria (dicas, django, python) tem um UUID diferente na coluna **slug**.

## shortuuid

Documentação: [https://pypi.org/project/shortuuid/](https://pypi.org/project/shortuuid/)

O `shortuuid` gera identificadores mais curtos, de 22 caracteres, com letras e números, sem os caracteres que se confundem (como `l`, `1`, `I`, `O` e `0`).

```bash
pip install shortuuid
```

```python
>>> import shortuuid
>>> shortuuid.uuid()
'cZJLMgZUzAjyY8tvB2eGHm'
>>> shortuuid.uuid(name='example.com')
'exu3DTbj2ncsn9tLdLWspw'
>>> shortuuid.ShortUUID().random(length=22)
'CxCQgoCAUBFjqrx6y2EV9F'
>>> shortuuid.ShortUUID().random(length=10)
'75WPgnGvbg'
```

* `shortuuid.uuid()`: um id aleatório a cada chamada.
* `shortuuid.uuid(name='example.com')`: um id gerado a partir de um nome. O mesmo nome gera sempre o mesmo id.
* `shortuuid.ShortUUID().random(length=...)`: uma string aleatória do tamanho que você quiser.

Também dá para trocar o alfabeto. No vídeo, usando só as letras do nome "regis":

```python
>>> shortuuid.set_alphabet('regis')
>>> shortuuid.uuid()
'egggsrsiiiiissgigsisiigsreieirsisrsegeerggigsgigsrgsgee'
>>> shortuuid.uuid()
'gesgiirrsgrieesesgirreigegsegiigriegegggrisiigsrisgsieeg'
```

Com um alfabeto de só 5 letras, o id fica bem mais longo.

## hashids

Gist: [https://gist.github.com/rg3915/4684721a603cf6d0dd3b9495744482fe](https://gist.github.com/rg3915/4684721a603cf6d0dd3b9495744482fe)

Documentação: [https://pypi.org/project/hashids/](https://pypi.org/project/hashids/)

O [hashids](https://hashids.org/) transforma números inteiros em strings curtas, como os ids dos vídeos do YouTube, e faz o caminho de volta. Ele existe para várias linguagens. É útil quando você não quer mostrar o id do banco (1, 2, 3...) para o usuário.

```bash
pip install hashids
```

```python
>>> from hashids import Hashids
>>> hashids = Hashids()
>>> hashids.encode(42)
'9x'
>>> hashids.decode('9x')
(42,)
>>> hashids.encode(665190)
'k7qWJ'
>>> hashids.decode('k7qWJ')
(665190,)
>>> hashids.encode(1122, 4200, 32665)
'ELmhW0mFD7o'
>>> hashids.decode('ELmhW0mFD7o')
(1122, 4200, 32665)
```

O `encode` aceita um ou vários números, e o `decode` sempre devolve uma tupla.

Dá para definir o alfabeto e o tamanho mínimo da string gerada:

```python
>>> hashids = Hashids(alphabet='abcdefghijklmnopqrstuvwxyz1234567890', min_length=22)
>>> for i in range(10): hashids.encode(i)
...
'9xkwnvoj3ejwgp6481y5mq'
'ml6kz731jdkoe524rxn0yq'
'kwp7yx456gl9g91lm23v8n'
'0qr6jxo9memje214w8zlvp'
'9poy2jq1xdn0e037nwv4zl'
'nz97pw01jgo5el24yrxv6m'
'q4pkmy631epjenrxv70w5l'
'n97kyw8q0dq9eo143z2x6v'
'x7n4zl0pkgr4d6o3vq92wy'
'6y27mjnzkev3d3549vq0xl'
```

Sem um `salt` (`Hashids(salt='...')`), o resultado é sempre o mesmo para os mesmos números, por isso você vai obter exatamente essa saída.

### django-hashid-field

Documentação: [https://pypi.org/project/django-hashid-field/](https://pypi.org/project/django-hashid-field/)

O `django-hashid-field` leva o hashids para os models: o banco continua guardando um inteiro, mas o Django mostra o id como hashid.

```bash
pip install django-hashid-field==3.1.3
```

No model `Article`, declare o `id` como `HashidAutoField` (antes ele era o `id` automático do Django):

```python
# myproject/core/models.py
import uuid
from django.db import models
from autoslug import AutoSlugField
from hashid_field import HashidAutoField


class UuidModel(models.Model):
    slug = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


class Article(models.Model):
    id = HashidAutoField(primary_key=True)
    title = models.CharField('título', max_length=200)
    subtitle = models.CharField('sub-título', max_length=200)
    slug = AutoSlugField(populate_from='title')
    category = models.ForeignKey(
        'Category',
        related_name='categories',
        verbose_name='categoria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    published_date = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'artigo'
        verbose_name_plural = 'artigos'

    def __str__(self):
        return self.title


class Category(UuidModel):
    title = models.CharField('título', max_length=50, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.title
```

```bash
python manage.py makemigrations
python manage.py migrate
```

A migração gerada mostra o alfabeto e o tamanho mínimo padrão do campo:

```python
# myproject/core/migrations/0004_auto_20200614_0901.py
from django.db import migrations
import hashid_field.field


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20200614_0855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='id',
            field=hashid_field.field.HashidAutoField(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', min_length=7, primary_key=True, serialize=False),
        ),
    ]
```

Para ter artigos para testar, o vídeo usa o mesmo `bulk_create` da [Dica 3](003-django-bulk_create-e-django-autoslug.md), no `python manage.py shell_plus`:

```python
titles = [
    {
        'title': 'Django Boilerplate',
        'subtitle': 'Django Boilerplate',
        'category': 'dicas'
    },
    {
        'title': 'Django extensions',
        'subtitle': 'Django extensions',
        'category': 'dicas'
    },
    {
        'title': 'Django Admin',
        'subtitle': 'Django Admin',
        'category': 'admin'
    },
    {
        'title': 'Django Autoslug',
        'subtitle': 'Django Autoslug',
        'category': 'dicas'
    },
]

aux = []

for title in titles:
    category = Category.objects.filter(title=title['category']).first()
    article = dict(
        title=title['title'],
        subtitle=title['subtitle']
    )
    if category:
        obj = Article(category=category, **article)
    else:
        obj = Article(**article)
    aux.append(obj)

Article.objects.bulk_create(aux)
```

Agora o `article.id` já aparece "encriptado". Para obter o inteiro que está no banco, use a classe `Hashid` e o atributo `.id`:

```python
>>> from hashid_field import Hashid
>>> articles = Article.objects.all()
>>> for article in articles:
...     print(article.id)
...
pnel5aK
MvbmOeY
olejRej
pmbk5ez
>>> for article in articles:
...     hashid = Hashid(article.id)
...     print(article.id, hashid.id)
...
pnel5aK 3
MvbmOeY 4
olejRej 1
pmbk5ez 2
```

A ordem segue o `ordering = ('title',)` do model. Assim você tem o id tanto encriptado (para usar na URL, por exemplo) quanto o valor real.

No repositório, o `ArticleAdmin` também passou a mostrar o id na listagem: `list_display = ('id', 'title', 'slug', 'get_published_date')`.

## Parte 2: senhas no terminal, com Python e com Django

<a href="https://youtu.be/qsRefchlXlo">
    <img src="../.gitbook/assets/youtube.png">
</a>

A segunda parte mostra outras ferramentas para gerar senhas e valores aleatórios.

### Gerando senhas no terminal Linux

```bash
# sha256 da data atual (em segundos), em base64, cortado em 32 caracteres
date +%s | sha256sum | base64 | head -c 32 ; echo

# 32 bytes aleatórios em base64 (troque 32 por 10 para uma senha menor)
openssl rand -base64 32

# 30 caracteres alfanuméricos tirados do /dev/urandom
strings /dev/urandom | grep -o '[[:alnum:]]' | head -n 30 | tr -d '\n'; echo

# md5 da data atual
date | md5sum
```

Exemplos de saída do vídeo:

```
$ date +%s | sha256sum | base64 | head -c 32; echo
NWI1MzQ2YmYyMjQyMmYwNjc4ZTUyY2Zk
$ openssl rand -base64 32
5eBWxC1joYo4kUGUD5Wumn8pFV/RrHIL37TMn0HyA8A=
$ openssl rand -base64 10
PrRggukSPT9ybw==
$ date | md5sum
f05037a9b2fb7b04398051f6b0804c7b  -
```

Os comandos baseados em `date` só mudam quando muda o segundo: rodando duas vezes no mesmo segundo, a saída se repete. Por isso o `openssl rand` e o `/dev/urandom` são opções melhores.

O `gpw` gera senhas **pronunciáveis**, mais fáceis de memorizar. Ele precisa ser instalado:

```bash
sudo apt install -y gpw

gpw          # 10 senhas
gpw 3 32     # 3 senhas de 32 caracteres
gpw 1 12     # 1 senha de 12 caracteres
gpw 1 6      # 1 senha de 6 caracteres
```

```
$ gpw 1 12
zipusterskeu
$ gpw 1 6
prowpu
```

### Gerando senhas com Python

#### com random

```python
import random

chars = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
size = 8
secret_key = "".join(random.sample(chars, size))
print(secret_key)
```

O `random.sample` sorteia `size` caracteres de `chars`, e o `join` junta tudo numa string. Cada execução gera uma senha nova (no vídeo saíram, por exemplo, `w#lI3vr8` e `vC3F5Tdc`).

#### com random e string

Referência: [https://pynative.com/python-generate-random-string/](https://pynative.com/python-generate-random-string/)

Para gerar uma string só com as letras que você escolher:

```python
# Generate a random string of specific letters only

import random
import string


def rand_string(length=5):
    # put your letters in the following string
    your_letters = 'abcdefghi'
    return ''.join((random.choice(your_letters) for i in range(length)))


print("Random String with specific letters ", rand_string())
print("Random String with specific letters ", rand_string(8))
```

```python
>>> rand_string()
'cagdh'
```

Aqui o `random.choice` sorteia uma letra por vez, e as letras podem se repetir.

#### com secrets

Documentação: [https://docs.python.org/3/library/secrets.html](https://docs.python.org/3/library/secrets.html)

*Novo no Python 3.6*

O módulo `secrets` é o indicado para senhas e tokens, porque usa a fonte de aleatoriedade mais segura do sistema operacional (o `random` não é feito para criptografia).

```python
>>> import secrets
>>> secrets.token_hex(16)
'67b98befdd801e657950ea276ea1aa65'
>>> secrets.token_hex(10)
'21f63cfc299c63121738'
>>> secrets.token_urlsafe(16)
'2z5rOtsq53rQInmLyG-_cg'
>>> url = 'https://mydomain.com/reset=' + secrets.token_urlsafe()
>>> print(url)
https://mydomain.com/reset=TYYcc4XXKQlwvdQcSUNHfiWTbed_QhUu6qigBza8os
```

* `token_hex(n)`: `n` bytes aleatórios em hexadecimal (a string tem o dobro de caracteres).
* `token_urlsafe(n)`: um token que pode ir numa URL sem problema, ótimo para um link de redefinição de senha.

### Django: gerando a SECRET_KEY e o .env

O Django tem a função `get_random_string`, a mesma que o `startproject` usa para gerar a `SECRET_KEY`. No projeto, ela é usada num script que cria o arquivo `.env` (lido pelo `python-decouple`, assunto da [Dica 9](009-escondendo-suas-senhas-python-decouple.md)):

```bash
vim contrib/env_gen.py
```

```python
# contrib/env_gen.py
"""
Django SECRET_KEY generator.
"""
from django.utils.crypto import get_random_string

chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

CONFIG_STRING = """
DEBUG=True
SECRET_KEY=%s
ALLOWED_HOSTS=127.0.0.1, .localhost
""".strip() % get_random_string(50, chars)

print(CONFIG_STRING)

# Writing our configuration file to '.env'
with open('.env', 'w') as configfile:
    configfile.write(CONFIG_STRING)
```

* `get_random_string(50, chars)` gera 50 caracteres sorteados de `chars`.
* O `%s` dentro do texto é trocado por esse valor.
* O `.strip()` tira a quebra de linha do começo e do fim.
* O `with open('.env', 'w')` grava (e sobrescreve) o arquivo `.env` na raiz do projeto.

Rode o script e confira o arquivo:

```bash
python contrib/env_gen.py
cat .env
```

```
DEBUG=True
SECRET_KEY=+c9^3g^bn6wgo8tabf*dl$@vx@m-!9ux%*9)88qnun&hk++sa9
ALLOWED_HOSTS=127.0.0.1, .localhost
```

Cada vez que você roda o script, uma `SECRET_KEY` diferente é gerada.

## Resumo

* Identificador único: `uuid.uuid4()` (no model, `default=uuid.uuid4`, sem parênteses), ou `shortuuid` para algo mais curto.
* Esconder o id do banco: `hashids`, e no Django o `HashidAutoField` do `django-hashid-field`.
* Senhas e tokens: `secrets` no Python; `openssl rand` ou `gpw` no terminal.
* `SECRET_KEY` do Django: `get_random_string` num script como o `contrib/env_gen.py`.

Observação: a partir do Django 4.0 o argumento `length` do `get_random_string` passou a ser obrigatório (o script acima já passa `50`). Para reproduzir o vídeo tal como foi gravado, use as versões indicadas no início.
