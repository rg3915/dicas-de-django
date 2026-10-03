# Django 6.1: conheça o MAILERS, o novo jeito de enviar e-mails

Publicado em 29/09/2026.

**Testado com:** Django 6.1.1 e Python 3.12.
{: .versoes }

<a href="https://youtu.be/YI3qazL4xZM">
    <img src="../.gitbook/assets/youtube.png">
</a>

Guia oficial de migração: [https://docs.djangoproject.com/en/6.1/howto/mailers-migration/](https://docs.djangoproject.com/en/6.1/howto/mailers-migration/)

Por anos o envio de e-mail no Django foi um backend só, espalhado por onze settings `EMAIL_*`. No Django 6.1 isso vira um dicionário, igual ao `CACHES` e ao `DATABASES`: o **MAILERS**. Neste tutorial vamos ver como era, como fica, configurar mais de um provedor, enviar escolhendo o provedor com `using=`, migrar um projeto existente (incluindo o caso chato do `fail_silently`) e testar.

## Pré-requisitos

* Python 3.12, 3.13 ou 3.14.
* Django 6.1 (`pip install "django>=6.1"`). Os exemplos foram rodados com o Django 6.1.1.

## Como era antes

Um backend só, configurado em vários settings soltos:

```python
# config/settings.py (antes do Django 6.1)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.exemplo.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'no-reply@exemplo.com'
EMAIL_HOST_PASSWORD = '...'
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10
```

O projeto inteiro tinha uma configuração de envio, e só uma. Para mandar e-mail transacional pelo SMTP próprio e marketing por outro provedor, você abria a segunda conexão na mão, com as credenciais no meio do código:

```python
# loja/emails.py (antes do Django 6.1)
from django.core import mail

connection = mail.get_connection(
    'path.to.custom.EmailBackend',
    host='smtp.marketing.com',
    username='...',
    password='...',
)
mail.send_mail('Novidades', 'Corpo', 'de@exemplo.com', ['para@exemplo.com'], connection=connection)
```

E parte da configuração vazava para os argumentos do envio: `auth_user`, `auth_password`, `fail_silently` e `connection`.

## Como fica: o setting MAILERS

```python
# config/settings.py
from decouple import config

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'OPTIONS': {
            'host': config('EMAIL_HOST', 'smtp.exemplo.com'),
            'use_tls': True,
            'username': config('EMAIL_USERNAME', ''),
            'password': config('EMAIL_PASSWORD', ''),
            'timeout': 10,
        },
    },
    'marketing': {
        'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'OPTIONS': {
            'host': config('MARKETING_EMAIL_HOST', 'smtp.marketing.com'),
            'use_tls': True,
            'username': config('MARKETING_EMAIL_USERNAME', ''),
            'password': config('MARKETING_EMAIL_PASSWORD', ''),
        },
    },
}

DEFAULT_FROM_EMAIL = 'no-reply@exemplo.com'
```

* Cada chave do dicionário é um **alias** (um "mailer"). O `'default'` é o usado quando você não diz nada.
* **`BACKEND`**: a classe do backend. Se for omitido, o padrão é o SMTP.
* **`OPTIONS`**: tudo o que antes era `EMAIL_*` vira uma chave aqui dentro, em minúsculas. As opções são repassadas como argumentos nomeados para o `__init__` do backend.
* O `port` pode ser omitido quando é o padrão do tipo de conexão: 587 com `use_tls`, 465 com `use_ssl`, 25 sem nenhum.
* Um backend de terceiros (de um provedor com API própria) entra do mesmo jeito, com as opções que ele documentar, por exemplo `'BACKEND': 'example.third.party.EmailBackend'` e `'OPTIONS': {'region': 'africa-1'}`.

O `python-decouple` foi usado só para tirar as credenciais do código; use o que preferir.

Projetos novos criados com `startproject` no 6.1 já vêm com um `MAILERS` que usa o backend de console (o e-mail é impresso no terminal). Projetos existentes não ganham o `MAILERS` sozinhos: os `EMAIL_*` continuam funcionando, com avisos de depreciação.

## Enviando: escolha o mailer pelo alias

```python
# loja/emails.py
import logging

from django.core import mail
from django.core.mail import EmailMessage, send_mail

logger = logging.getLogger(__name__)


def enviar_recibo(pedido):
    # vai pelo mailer 'default'
    send_mail(
        'Recibo do seu pedido',
        f'Obrigado! Seu pedido {pedido.pk} foi confirmado.',
        None,  # usa o DEFAULT_FROM_EMAIL
        [pedido.cliente.email],
    )


def enviar_novidades(emails):
    # vai pelo mailer 'marketing'
    send_mail(
        'Novidades da semana',
        'Confira os lançamentos.',
        None,
        emails,
        using='marketing',
    )


def enviar_com_anexo(destinatario, caminho_pdf):
    msg = EmailMessage('Seu boleto', 'Segue o boleto em anexo.', to=[destinatario])
    msg.attach_file(caminho_pdf)
    msg.send(using='marketing')


def enviar_lote(mensagens):
    # a instância do backend, se você precisar dela
    backend = mail.mailers['marketing']
    return backend.send_messages(mensagens)
```

* `send_mail(..., using='marketing')` substitui o `connection=get_connection(...)`. Host, porta, usuário e senha não aparecem mais no ponto de envio: o código diz qual mailer quer, os settings dizem o que aquele mailer é.
* `EmailMessage.send(using=...)` funciona do mesmo jeito.
* `mail.mailers['marketing']` devolve a instância do backend configurado, e `mail.mailers.default` devolve o default.
* Um alias que não existe levanta `django.core.mail.MailerDoesNotExist` ("The mailer 'xyz' is not configured.").

## De-para completo

| Antes | Django 6.1 |
|---|---|
| `EMAIL_BACKEND` | `MAILERS['default']['BACKEND']` |
| `EMAIL_HOST` | `'host'` em `OPTIONS` (obrigatório no SMTP; antes o padrão era `'localhost'`) |
| `EMAIL_PORT` | `'port'` em `OPTIONS` |
| `EMAIL_HOST_USER` | `'username'` em `OPTIONS` (repare: não é `host_user`) |
| `EMAIL_HOST_PASSWORD` | `'password'` em `OPTIONS` |
| `EMAIL_USE_TLS` | `'use_tls'` em `OPTIONS` |
| `EMAIL_USE_SSL` | `'use_ssl'` em `OPTIONS` |
| `EMAIL_SSL_CERTFILE` | `'ssl_certfile'` em `OPTIONS` |
| `EMAIL_SSL_KEYFILE` | `'ssl_keyfile'` em `OPTIONS` |
| `EMAIL_TIMEOUT` | `'timeout'` em `OPTIONS` |
| `EMAIL_FILE_PATH` | `'file_path'` em `OPTIONS` (com o backend `filebased`) |
| `mail.get_connection()` | `mail.mailers.default` |
| `mail.get_connection('backend', ...)` | um alias novo em `MAILERS` + `mail.mailers['alias']` |
| `send_mail(..., connection=conn)` | `send_mail(..., using='alias')` |
| `send_mail(..., auth_user=..., auth_password=...)` | um alias com `'username'` e `'password'` em `OPTIONS` + `using=` |

Exemplo real de migração, lado a lado:

```python
# config/settings.py - antes
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.example.net'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'user@example.net'
EMAIL_HOST_PASSWORD = 'password'
```

```python
# config/settings.py - depois
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'OPTIONS': {
            'host': 'mail.example.net',
            'use_tls': True,
            # port não é necessário: com use_tls o padrão já é 587
            'username': 'user@example.net',
            'password': 'password',
        },
    },
}
```

Atenção: não dá para ter os dois ao mesmo tempo. Se `MAILERS` estiver definido junto com algum `EMAIL_*` depreciado, o Django nem sobe:

```
django.core.exceptions.ImproperlyConfigured: Deprecated email settings are not allowed when MAILERS is defined: EMAIL_BACKEND, EMAIL_HOST.
```

Na transição, `mail.mailers['default']` funciona com qualquer um dos dois jeitos de configurar. Dá para migrar os settings primeiro e o código depois.

## O caso chato: fail_silently

O `fail_silently` está depreciado em `send_mail()`, `send_mass_mail()`, `mail_admins()`, `mail_managers()` e `EmailMessage.send()`, e não combina com `using`:

```python
send_mail('a', 'b', None, ['c@d.com'], using='default', fail_silently=True)
# TypeError: 'fail_silently' is not compatible with 'using'.
```

Não existe um argumento substituto: decida o que você quer ignorar e trate no seu código.

```python
# loja/emails.py (continuação)
def enviar_novidades_sem_quebrar(emails):
    try:
        send_mail('Novidades', 'Corpo', None, emails, using='marketing')
    except mail.MailerDoesNotExist:
        # o projeto não configurou o mailer 'marketing': segue a vida
        pass
    except OSError:
        # falhas de rede e de SMTP
        logger.exception('falha ao enviar e-mail de marketing')
```

* `except mail.MailerDoesNotExist`: enviar se o e-mail estiver configurado, sem erro se não estiver (útil em apps reutilizáveis).
* `except OSError`: ignorar só problemas de SMTP e rede (o mesmo que o `fail_silently` do backend SMTP fazia).
* `except Exception`: ignorar tudo, por exemplo dentro de um handler de erro, para não gerar falha em cascata.
* Se você usava `fail_silently` para "ignorar e-mail digitado errado", pode simplesmente removê-lo: erros de destinatário quase nunca são detectados no momento do envio.

Se quiser reaproveitar o comportamento em vários pontos, crie um alias com a opção no próprio backend:

```python
# config/settings.py (trecho)
MAILERS = {
    'default': {...},
    'admin-logging': {
        'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'OPTIONS': {
            'host': 'smtp.exemplo.com',
            'fail_silently': True,
        },
    },
}
```

E aponte o `AdminEmailHandler` para ele, com a nova opção `using` (o antigo `email_backend` do handler também foi depreciado):

```python
# config/settings.py (trecho)
LOGGING = {
    'version': 1,
    'handlers': {
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'using': 'admin-logging',
        },
    },
}
```

## O Django passa a avisar quando a config está errada

* **`mail.E001`**: impede usar no mailer `'default'` um backend que não é de produção (console, locmem, file). Só roda no check de deploy.
* **`mail.W001`**: avisa quando você definiu `MAILERS`, mas esqueceu a entrada `'default'`.
* **`sendtestemail --using`**: o comando de teste ganhou a opção para escolher o alias.

```bash
python manage.py check --deploy
# ?: (mail.E001) Your MAILERS setting uses a development-only email backend in the 'default' entry (django.core.mail.backends.console.EmailBackend).

python manage.py sendtestemail voce@exemplo.com --using marketing
```

## Ambiente de desenvolvimento

Em desenvolvimento, aponte os mailers para backends que não enviam nada:

```python
# config/settings.py (desenvolvimento)
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
    'marketing': {
        'BACKEND': 'django.core.mail.backends.filebased.EmailBackend',
        'OPTIONS': {'file_path': BASE_DIR / 'emails-marketing'},
    },
}
```

O `default` imprime no terminal, e o `marketing` grava um arquivo `.log` por envio na pasta `emails-marketing`.

## Testes

O test runner do Django substitui **todos** os mailers pelo backend em memória: nada é enviado de verdade e as mensagens ficam em `mail.outbox`, inclusive as enviadas com `using=`.

```python
# loja/tests.py
from django.core import mail
from django.test import TestCase


class EmailTest(TestCase):
    def test_marketing(self):
        mail.send_mail('Novidades', 'corpo', None, ['cliente@exemplo.com'], using='marketing')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Novidades')
```

```bash
python manage.py test loja
```

Por isso mesmo, a suíte de testes pode não mostrar os avisos de depreciação da sua configuração de produção.

## Encontrando o que falta migrar

Rode o projeto com os avisos de depreciação ligados:

```bash
python -W always manage.py runserver
python -W always manage.py test
```

Com `EMAIL_*` nos settings, você verá algo assim:

```
RemovedInDjango70Warning: The EMAIL_BACKEND setting is deprecated. Migrate to MAILERS before Django 7.0.
RemovedInDjango70Warning: The EMAIL_HOST setting is deprecated. Migrate to MAILERS before Django 7.0.
```

(Essa é a mensagem do Django 6.1.1. A documentação já chama a próxima versão maior de **Django 2028**: com a adoção do versionamento por calendário, a antiga 7.0 virou 2028.)

Antes de migrar, confira se as bibliotecas de terceiros que mandam e-mail no seu projeto já suportam `MAILERS`. Se alguma delas ler `settings.EMAIL_HOST` ou chamar `get_connection('caminho.do.Backend')`, você verá `AttributeError: The EMAIL_... setting is not available when MAILERS is defined` ou `RuntimeError: get_connection(backend, ...) is not supported with MAILERS`. Nesse caso, atualize a biblioteca ou mantenha os `EMAIL_*` até ela ser atualizada.

## O prazo

* **Django 6.1 (agora)**: `MAILERS` existe e funciona. Os `EMAIL_*`, `get_connection()`, `connection=`, `fail_silently`, `auth_user` e `auth_password` continuam valendo, com aviso de depreciação.
* **Django 2028**: os `EMAIL_*` e esses argumentos são removidos, e enviar e-mail sem `MAILERS` passa a levantar `MailerDoesNotExist`.

## Resumo

1. Traduza os `EMAIL_*` para `MAILERS['default']`. Na maioria dos projetos, é só isso.
2. Troque `get_connection()` por `mail.mailers` e `connection=` por `using=`.
3. Substitua `fail_silently` por `try`/`except` ou por um alias com `'fail_silently': True`.
4. Rode com os avisos de depreciação ligados para achar o resto.

Documentação:

* [Migrating email to mailers](https://docs.djangoproject.com/en/6.1/howto/mailers-migration/)
* [Sending email](https://docs.djangoproject.com/en/6.1/topics/email/)
* [Notas de lançamento do Django 6.1](https://docs.djangoproject.com/en/6.1/releases/6.1/)
