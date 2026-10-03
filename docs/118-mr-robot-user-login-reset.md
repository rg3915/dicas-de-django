# Se o Elliot usasse Django: User, login e reset de senha

Publicado em 24/09/2026.

<a href="https://youtu.be/nq1uZju7IW8">
    <img src="../.gitbook/assets/youtube.png">
</a>

As telas do Mr. Robot, mas com o código que a gente escreve de verdade: um app de contas em Django rodando em Docker com Postgres.

## O que é visto

* Dockerfile com Python 3.13 e gunicorn, e o compose com Postgres e **health check**: o contêiner web só sobe quando o banco está pronto.
* `AUTH_USER_MODEL` apontando para o nosso próprio model, `migrate` e `createsuperuser`.
* `accounts/models.py`: `User` estendendo `AbstractUser`, e-mail único como campo de login (`USERNAME_FIELD`), avatar e flag de e-mail verificado.
* `LoginView` e `PasswordResetView` direto do `django.contrib.auth`: só trocamos o template, o formulário e para onde ir depois.
* O shell criando o usuário, conferindo a senha e gerando o token de reset.

## Dica

Comece todo projeto Django com um User customizado, antes do primeiro `migrate`.

## Shorts da série Mr. Robot

* [O Elliot subiu o Django no Docker em 1 comando](https://youtube.com/shorts/gLL3iWZAD5Y) (21/09/2026)
* [Reset de senha estilo Mr. Robot, em Django](https://youtube.com/shorts/sMTdIeFqntA) (22/09/2026)
