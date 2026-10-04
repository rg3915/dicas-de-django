# Dica 55 - Rodando Django em https localmente com runserver_plus

**Versões usadas no vídeo:** Django 3.2.6, django-extensions 3.1, Werkzeug 2.0.2, pyOpenSSL 21.0.0 e Python 3.9.
{: .versoes }

<a href="https://youtu.be/4nI3lcUAeC4">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

O `runserver_plus` é um comando do django-extensions que substitui o `runserver` do Django pelo servidor de desenvolvimento do [Werkzeug](https://werkzeug.palletsprojects.com/). Ele traz duas coisas que o `runserver` não tem: a opção `--print-sql`, que mostra no terminal cada consulta SQL que as páginas executam, e a possibilidade de rodar o projeto em **https** localmente, com um certificado gerado na hora.

Documentação: [https://django-extensions.readthedocs.io/en/latest/runserver_plus.html](https://django-extensions.readthedocs.io/en/latest/runserver_plus.html)

## Pré-requisitos

Um projeto Django com o django-extensions instalado e configurado, como vimos na dica anterior, [Dica 54 - django-extensions - mais comandos](054-django-extensions-mais-comandos.md):

```bash
pip install django-extensions
```

```python
# myproject/settings.py
INSTALLED_APPS = [
    ...
    'django_extensions',
    ...
]
```

## Instalando o Werkzeug

O `runserver_plus` depende do Werkzeug:

```bash
pip install Werkzeug
```

```
Collecting Werkzeug
  Using cached Werkzeug-2.0.2-py3-none-any.whl (288 kB)
Installing collected packages: Werkzeug
Successfully installed Werkzeug-2.0.2
```

## Mostrando as consultas SQL com --print-sql

Rode o servidor com a opção `--print-sql`:

```bash
python manage.py runserver_plus --print-sql
```

Logo na inicialização ele já mostra as consultas que o Django faz para verificar as migrations, e depois a mensagem do servidor:

```
SELECT name,
       type
  FROM sqlite_master
 WHERE type in ('table', 'view')
   AND NOT name='sqlite_sequence'
 ORDER BY name

Execution time: 0.001281s [Database: default]
SELECT "django_migrations"."id",
       "django_migrations"."app",
       "django_migrations"."name",
       "django_migrations"."applied"
  FROM "django_migrations"

Execution time: 0.001817s [Database: default]

Django version 3.2.6, using settings 'myproject.settings'
Development server is running at http://[127.0.0.1]:8000/
Using the Werkzeug debugger (http://werkzeug.pocoo.org/)
Quit the server with CONTROL-C.
 * Debugger is active!
 * Debugger PIN: 660-232-784
```

Agora abra [http://localhost:8000](http://localhost:8000) e navegue. Tudo o que a página consultar no banco aparece no terminal, formatado e com o tempo de execução. No vídeo, ao entrar em **Viagens** (`/travel/`) e em **Pessoas** (`/persons/`), apareceram as contagens usadas pela paginação e pelo contador de viagens do menu:

```
SELECT COUNT(*) AS "__count"
  FROM "travel_travel"

Execution time: 0.001044s [Database: default]
127.0.0.1 - - [05/Dec/2021 01:08:18] "GET /travel/ HTTP/1.1" 200 -
SELECT COUNT(*) AS "__count"
  FROM "core_person"

Execution time: 0.002651s [Database: default]
SELECT COUNT(*) AS "__count"
  FROM "travel_travel"

Execution time: 0.000287s [Database: default]
127.0.0.1 - - [05/Dec/2021 01:08:28] "GET /persons/ HTTP/1.1" 200 -
```

É uma forma simples de ver quantas consultas cada página faz, sem abrir o Django Debug Toolbar.

## Rodando em https

Pare o servidor com `Ctrl+C`. Para usar https, o Werkzeug precisa do pyOpenSSL:

```bash
pip install pyOpenSSL
```

```
Collecting pyOpenSSL
  Using cached pyOpenSSL-21.0.0-py2.py3-none-any.whl (55 kB)
Collecting cryptography>=3.3
  Using cached cryptography-36.0.0-cp36-abi3-manylinux_2_24_x86_64.whl (3.6 MB)
...
Installing collected packages: pycparser, cffi, cryptography, pyOpenSSL
```

Agora rode o `runserver_plus` com `--cert-file`, indicando onde fica o certificado. No vídeo ele foi colocado na pasta `/tmp`:

```bash
python manage.py runserver_plus --cert-file /tmp/cert.crt
```

```
 * Running on https://127.0.0.1:8000/ (Press CTRL+C to quit)
 * Restarting with stat
Performing system checks...

System check identified no issues (0 silenced).

Django version 3.2.6, using settings 'myproject.settings'
Development server is running at https://[127.0.0.1]:8000/
Using the Werkzeug debugger (http://werkzeug.pocoo.org/)
Quit the server with CONTROL-C.
 * Debugger is active!
 * Debugger PIN: 660-232-784
```

Se o arquivo ainda não existir, o `runserver_plus` gera um certificado autoassinado na hora, criando `/tmp/cert.crt` e a chave `/tmp/cert.key`. Nas próximas vezes ele reaproveita os mesmos arquivos.

Entre em [https://localhost:8000](https://localhost:8000) (ou https://127.0.0.1:8000).

## O aviso do navegador

Como o certificado foi gerado localmente e não foi assinado por nenhuma autoridade certificadora, o navegador mostra o aviso "Sua conexão não é particular" (`NET::ERR_CERT_AUTHORITY_INVALID`). Isso é esperado em desenvolvimento: clique em **Avançado** e depois em prosseguir para 127.0.0.1. A partir daí você navega normalmente pelo projeto em https, com o cadeado marcado como "Não seguro" por causa do certificado local.

Isso é útil para testar localmente recursos que só funcionam em https, como cookies com `Secure`, algumas APIs do navegador e integrações de terceiros que exigem uma URL https.

## Conclusão

Com o Werkzeug instalado, `python manage.py runserver_plus --print-sql` mostra todas as consultas SQL das páginas; com o pyOpenSSL, `python manage.py runserver_plus --cert-file /tmp/cert.crt` roda o Django em https localmente, sem configurar nenhum servidor web.
