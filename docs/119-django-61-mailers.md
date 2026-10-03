# Django 6.1: conheça o MAILERS, o novo jeito de enviar e-mails

Publicado em 29/09/2026.

<a href="https://youtu.be/YI3qazL4xZM">
    <img src="../.gitbook/assets/youtube.png">
</a>

Guia oficial de migração: [https://docs.djangoproject.com/en/6.1/howto/mailers-migration/](https://docs.djangoproject.com/en/6.1/howto/mailers-migration/)

Por anos o envio de e-mail no Django foi um backend só, espalhado por onze settings `EMAIL_*`. No Django 6.1 isso vira um dicionário, igual ao `CACHES` e ao `DATABASES`: o **MAILERS**.

## O que muda

* Os 11 settings `EMAIL_*` entram em depreciação no Django 6.1.
* O `MAILERS` tem o alias `"default"` e quantos provedores você quiser (por exemplo `"marketing"`), cada um com `BACKEND` e `OPTIONS`.
* `send_mail(..., using="marketing")` no lugar de `connection=get_connection(...)`.

## De-para

| Antes | Django 6.1 |
|---|---|
| `EMAIL_BACKEND` | `MAILERS["default"]["BACKEND"]` |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS` | `MAILERS["default"]["OPTIONS"]` |
| `mail.get_connection()` | `mail.mailers.default` |

`fail_silently` não tem substituto direto: trate a exceção de envio no seu código. Rode com os avisos de depreciação ligados para achar o resto.
