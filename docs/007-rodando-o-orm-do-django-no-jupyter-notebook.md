# Dica 7 - Rodando o ORM do Django no Jupyter Notebook

**Versões usadas no vídeo:** Django 2.2.13 e depois 3.0.7, Python 3.8.2, django-extensions 2.2.9, IPython 7.16.1 e Notebook 6.0.3.
{: .versoes }

<a href="https://youtu.be/bXtmvu_O_sk">
    <img src="../.gitbook/assets/youtube.png">
</a>

O Jupyter Notebook é ótimo para explorar dados: você roda o código em células, vê o resultado logo abaixo e pode refazer só o trecho que quiser. Nesta dica vamos abrir um notebook que já vem com o Django carregado, para usar o ORM (`User.objects.all()`, por exemplo) direto nas células. Também vamos ver o erro `SynchronousOnlyOperation` que aparece a partir do Django 3.0 e como resolvê-lo.

## Pré-requisitos

* Python 3 e um projeto Django com o `django-extensions` instalado e no `INSTALLED_APPS` (veja a [Dica 2](002-django-extensions.md)). É ele que fornece o comando `shell_plus`.

## Criando o projeto com o boilerplate

No vídeo, o projeto é criado com o boilerplate simples da [Dica 1](001-django-boilerplate.md), um script que cria a virtualenv, instala o Django 2.2.13, o `django-extensions`, o `python-decouple` e outras libs, e cria o projeto `myproject` com o app `core`.

Gist do boilerplate: [https://gist.github.com/rg3915/b363f5c4a998f42901705b23ccf4b8e8](https://gist.github.com/rg3915/b363f5c4a998f42901705b23ccf4b8e8)

```bash
cd /tmp
mkdir dica07
cd dica07

curl https://gist.githubusercontent.com/rg3915/b363f5c4a998f42901705b23ccf4b8e8/raw/5d0d1cc46d3a52bef6cd73d9d476140ad445be9e/boilerplatesimple.sh -o boilerplatesimple.sh

source boilerplatesimple.sh
```

O script mostra o andamento:

```
>>> The name of the project is 'myproject'.
>>> Creating README.md
>>> Creating virtualenv
>>> .venv is created
>>> activate the .venv
>>> Installing the Django
...
Create superuser? (y/N)
```

Ele roda as migrações e pergunta se você quer criar um superusuário. Responda `y` e escolha a senha do usuário `admin` (vamos listar esse usuário no notebook). No fim, a virtualenv `.venv` já está ativa.

O `requirements.txt` gerado ficou assim:

```
# requirements.txt
dj-database-url==0.5.0
Django==2.2.13
django-extensions==2.2.9
django-widget-tweaks==1.4.8
python-decouple==3.3
pytz==2020.1
six==1.15.0
sqlparse==0.3.1
```

E o `django_extensions` já está no `INSTALLED_APPS`:

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
    'myproject.core',
]
```

## Instalando o Jupyter

Instale o IPython com o extra `notebook`, que traz o Jupyter Notebook junto:

```bash
pip install ipython[notebook]
```

> Se o seu shell for o zsh, coloque entre aspas: `pip install "ipython[notebook]"`.

No vídeo foram instalados, entre outros, `ipython-7.16.1`, `notebook-6.0.3`, `ipykernel-5.3.0` e `jupyter-client-6.1.3`.

## Rodando o shell_plus no notebook

```bash
python manage.py shell_plus --notebook
```

O Jupyter abre no navegador, em `http://localhost:8888`, mostrando os arquivos do projeto. Para criar um notebook com o Django carregado, clique em **New** e escolha o kernel **Django Shell-Plus**. Esse kernel já faz o `django.setup()` e importa os models e utilitários, como o `shell_plus` faz no terminal.

Agora é só usar o ORM nas células:

```python
users = User.objects.all()
```

```python
for user in users:
    print(user)
```

```
admin
```

Para parar o servidor do Jupyter, volte ao terminal, aperte `Ctrl+C` e responda `y`:

```
Shutdown this notebook server (y/[n])? y
```

## O erro SynchronousOnlyOperation no Django 3.0

Agora vamos atualizar o Django no mesmo projeto, para a versão mais recente na época (3.0.7):

```bash
pip install -U django
```

```
Collecting django
  Using cached Django-3.0.7-py3-none-any.whl (7.5 MB)
```

Rode de novo o notebook, crie um notebook novo com o kernel **Django Shell-Plus** e execute as mesmas células:

```bash
python manage.py shell_plus --notebook
```

```python
users = User.objects.all()
```

```python
for user in users:
    print(user)
```

Desta vez dá erro:

```
SynchronousOnlyOperation                  Traceback (most recent call last)
<ipython-input-2-0a995b17fe71> in <module>
----> 1 for user in users:
      2     print(user)

/tmp/dica07/.venv/lib/python3.8/site-packages/django/db/models/query.py in __iter__(self)
...
SynchronousOnlyOperation: You cannot call this from an async context - use a thread or sync_to_async.
```

O motivo: a partir do Django 3.0, partes do Django que não podem rodar num contexto assíncrono, como o ORM, ficam protegidas. Se houver um *event loop* rodando na thread, o Django levanta `SynchronousOnlyOperation`. E o Jupyter (o IPython) roda o código das células dentro de um event loop.

A documentação ([Async safety](https://docs.djangoproject.com/en/3.0/topics/async/#async-safety)) cita exatamente o caso do Jupyter: quando você tem certeza de que não há código concorrente acessando o ORM, pode desligar essa proteção com a variável de ambiente `DJANGO_ALLOW_ASYNC_UNSAFE`. Dentro do Python:

```python
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
```

No vídeo, essa linha foi colocada no `settings.py`, logo depois do `ALLOWED_HOSTS` (o `os` já está importado no `settings.py` do Django 2.2 e 3.0):

```python
# myproject/settings.py
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
```

Depois, no notebook, use **Kernel > Restart & Run All** para reiniciar o kernel e rodar todas as células de novo. Agora o `for` funciona e imprime `admin`.

**Atenção:** a própria documentação avisa que essa opção pode causar perda ou corrupção de dados se houver acesso concorrente, e que ela não deve ser usada em produção. Como o Jupyter é só para desenvolvimento, tudo bem usar localmente, mas não deixe isso ativo no servidor. Uma forma de garantir é definir a variável só na hora de abrir o notebook, em vez de colocá-la no `settings.py`:

```bash
DJANGO_ALLOW_ASYNC_UNSAFE=true python manage.py shell_plus --notebook
```

## Para saber mais

Na [Live de Python #95](https://www.youtube.com/watch?v=cyxky2QJlwg), no canal do Eduardo Mendes, o Regis falou mais sobre o ORM do Django usando o Jupyter Notebook.
