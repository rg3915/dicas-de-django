# Dica 9 - Escondendo suas senhas python-decouple

**Versões usadas no vídeo:** Django 3.0.7, Python 3.8 e python-decouple 3.3.
{: .versoes }

<a href="https://youtu.be/eOwN7e0QBXo">
    <img src="../.gitbook/assets/youtube.png">
</a>

[Video do Henrique Bastos na Live de Python #97](https://www.youtube.com/watch?v=zYJGpLw5Wv4)

<a href="https://www.youtube.com/watch?v=zYJGpLw5Wv4">
    <img src="../.gitbook/assets/youtube.png">
</a>

Repositório: [https://github.com/henriquebastos/python-decouple](https://github.com/henriquebastos/python-decouple)

Quando você cria um projeto Django, o `settings.py` já vem com a `SECRET_KEY` escrita no código, o `DEBUG = True` fixo e o `ALLOWED_HOSTS` vazio. Se depois você colocar ali a senha do banco ou do e-mail, tudo isso vai parar no repositório. O `python-decouple`, criado pelo Henrique Bastos, resolve isso: os valores sensíveis e os que mudam de um ambiente para outro ficam num arquivo `.env` (ou em variáveis de ambiente), fora do código, e o `settings.py` só os lê.

Ele funciona em qualquer projeto Python (Django, Flask ou um script qualquer). Neste tutorial vamos criar um projeto Django do zero e configurar `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, e-mail e banco de dados com o decouple.

## A ideia por trás do decouple

Na [Live de Python #97](https://www.youtube.com/watch?v=zYJGpLw5Wv4) (vídeo acima), o Henrique Bastos explica o conceito com calma. Em resumo:

* O **código** do projeto é o mesmo na sua máquina, no servidor de homologação e no de produção. O que muda é a **configuração da instância**: qual banco usar, como enviar e-mail, se o debug está ligado. Por isso, em vez de vários `settings` (um para cada ambiente), você tem um `settings.py` só, que lê esses parâmetros de fora.
* Variáveis de ambiente são sempre **strings**. Por isso o `config` tem o parâmetro `cast`, que converte o valor para o tipo certo (`bool`, `int`, lista etc.).
* Se uma configuração obrigatória não existe, o decouple **levanta um erro** em vez de seguir com um valor qualquer. Assim você descobre o problema na hora de subir o projeto, e não depois.

## Criando o projeto

Neste vídeo o projeto é criado à mão, sem boilerplate, para mostrar todos os detalhes:

```bash
mkdir dica09
cd dica09
python -m venv .venv
source .venv/bin/activate
pip install django    # no vídeo, instalou o Django 3.0.7

django-admin.py startproject myproject .
cd myproject
python ../manage.py startapp core
cd ..
```

O `settings.py` gerado tem os valores fixos no código:

```python
# myproject/settings.py
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'v81jh&n^asq$con^i763ilo+&r*%@&+d%0fcj8p8z(p4g2b$_r'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
```

## Instalando o python-decouple

```bash
pip install python-decouple
pip freeze > requirements.txt
```

```
# requirements.txt
asgiref==3.2.10
Django==3.0.7
python-decouple==3.3
pytz==2020.1
sqlparse==0.3.1
```

## O arquivo .env

Na raiz do projeto (na mesma pasta do `manage.py`), crie o arquivo `.env`. Recorte a `SECRET_KEY` do `settings.py` e cole aqui:

```
# .env
DEBUG=True
SECRET_KEY=v81jh&n^asq$con^i763ilo+&r*%@&+d%0fcj8p8z(p4g2b$_r
ALLOWED_HOSTS=127.0.0.1,.localhost
```

Repare que o formato é `NOME=valor`: escreva **sem espaços** em volta do `=` e **sem aspas** no valor. O `.localhost` (com ponto na frente) aceita `localhost` e qualquer subdomínio dele.

**Importante:** o `.env` não pode ir para o repositório. Coloque-o no `.gitignore`:

```
# .gitignore
.env
```

## Lendo as configurações no settings.py

```python
# myproject/settings.py
import os
from decouple import config, Csv

# ...

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())
```

* `config('SECRET_KEY')`: lê o valor do `.env`. O nome no `config` é o mesmo da variável no `.env`. Como não tem `default`, se a variável não existir o decouple levanta `UndefinedValueError: SECRET_KEY not found. Declare it as envvar or define a default value.`
* `config('DEBUG', default=False, cast=bool)`: o `cast=bool` converte o texto `True` (ou `False`, `1`, `0`, `on`, `off`...) em booleano. Se não houver `DEBUG` definido, o padrão é `False`, o que é o mais seguro para produção.
* `config('ALLOWED_HOSTS', default=[], cast=Csv())`: o `Csv` (com **C maiúsculo**, importado do `decouple`, e não o módulo `csv` do Python) separa o texto pelas vírgulas e devolve uma lista: `['127.0.0.1', '.localhost']`.

Teste: o projeto deve rodar normalmente.

```bash
python manage.py migrate
python manage.py runserver
```

Se você definir a mesma variável no ambiente, ela tem prioridade sobre o `.env`. Por exemplo, `DEBUG=False python manage.py runserver` roda com o debug desligado, sem mexer no arquivo.

## Configuração de e-mail

Qualquer outra configuração pode ir para o `.env`. Por exemplo, o envio de e-mail:

```
# .env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=rg3915@email.com
EMAIL_HOST_PASSWORD=oiuoytrb
```

No `.env`, como antes, sem espaços e sem aspas (no vídeo, essas linhas foram coladas primeiro com o `config(...)` do lado direito, e o Regis corrige no fim: no `.env` vai só o valor). O usuário e a senha acima são de exemplo.

* `EMAIL_HOST`: o servidor SMTP do seu provedor (para o SendGrid, `smtp.sendgrid.net`).
* `EMAIL_BACKEND`: com `django.core.mail.backends.smtp.EmailBackend` o Django envia e-mails de verdade; com `django.core.mail.backends.console.EmailBackend` ele só mostra o e-mail no terminal, o que é ótimo para testar.

E no `settings.py`:

```python
# myproject/settings.py
EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```

Use o `cast` também aqui: sem `cast=bool`, o `EMAIL_USE_TLS` seria a string `'False'`, que em Python é verdadeira.

## Configuração do banco de dados

No `settings.py`, em vez da configuração padrão do SQLite, dá para detalhar o banco e ler cada parte do `.env`. Por exemplo, para o PostgreSQL:

```python
# myproject/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('DB_HOST', 'localhost'),
        'PORT': '5432',
    }
}
```

O segundo argumento de `config('DB_HOST', 'localhost')` é o valor padrão, usado se `DB_HOST` não estiver no `.env`. A porta também poderia vir do `.env`, do mesmo jeito.

```
# .env
POSTGRES_DB=mydb
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypass
DB_HOST=localhost
```

* `POSTGRES_DB`: o nome do banco.
* `POSTGRES_USER` e `POSTGRES_PASSWORD`: o usuário e a senha.
* `DB_HOST`: `localhost` na sua máquina, ou o endereço do servidor de banco (como um RDS da AWS) em produção.

Para usar o PostgreSQL você precisa de um servidor Postgres rodando e do driver (`pip install psycopg2-binary`). No vídeo essa parte é só mostrada, sem rodar.

## O .env completo

Juntando tudo, um `.env` de exemplo (o mesmo modelo serve para outras dicas, por isso ele já traz as variáveis da AWS, vazias):

```
# .env
DEBUG=True
SECRET_KEY=c9^3g^bn6wgo8tabf*dl$@vx@m-!9ux%*9)88qnun&hk++sa90
ALLOWED_HOSTS=127.0.0.1,.localhost
POSTGRES_DB=mydb
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypass
DB_HOST=localhost

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=

# console ou smtp
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

E o trecho correspondente do `settings.py`:

```python
# myproject/settings.py
import os
from decouple import config, Csv

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())

EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('DB_HOST', 'localhost'),
        'PORT': '5432',
    }
}
```

Para gerar um `.env` com uma `SECRET_KEY` nova automaticamente, veja o script `contrib/env_gen.py` da [Dica 6](006-geradores-de-senhas-randomicas-uuid-hashids-secrets.md).

## Conclusão

Com o `python-decouple`, o `settings.py` pode ir para o repositório sem nenhuma senha: cada ambiente tem o seu `.env` (ou as suas variáveis de ambiente), e o `cast` garante que cada valor chega com o tipo certo.
