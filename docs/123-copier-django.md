# Copier + Django: login por e-mail em um comando

> 📅 **Vídeo agendado:** será publicado no YouTube em **10/10/2026, às 10:00**. O link abaixo passa a funcionar nessa data.

<a href="https://youtu.be/-TBGoqLYYxA">
    <img src="../.gitbook/assets/youtube.png">
</a>

Template: [https://github.com/rg3915/django-auth-template](https://github.com/rg3915/django-auth-template)

Documentação do Copier: [https://copier.readthedocs.io/](https://copier.readthedocs.io/)

Todo projeto Django começa igual: trocar o username pelo e-mail, fazer login, cadastro, "esqueci minha senha"... e copiar tudo do projeto anterior, esquecendo um pedaço.

Com o **Copier** você gera tudo isso com um comando só: um template Django com usuário que entra com e-mail, cadastro, perfil, troca e reset de senha, app `core` com modelos abstratos, health check e testes. E o projeto ainda atualiza quando o template muda (`copier update`).

## Comandos do vídeo

```
uv tool install copier
copier copy --trust gh:rg3915/django-auth-template loja
copier copy --trust --defaults -d project_name=Blog -d database=postgres gh:rg3915/django-auth-template blog
cd loja && uv run python manage.py createsuperuser
uv run python manage.py test
uv run python manage.py runserver
copier update --trust
```

## Prompt para a sua IA

> Crie um template do Copier para projetos Django 6, versionado em git com a tag v1.0.0.
>
> Dentro do arquivo copier.yml, faça três perguntas: nome do projeto, nome do pacote Python (gerado a partir do nome, com validação) e banco de dados (Postgres ou SQLite). Use a chave _subdirectory: template e depois adicione as _tasks, que vão rodar git init, uv sync, um script que gera o .env com uma SECRET_KEY nova e o migrate — esse último só quando o banco for SQLite.
>
> Crie uma app accounts com um usuário customizado: sem username, usando o e-mail único como USERNAME_FIELD, e com um manager em que o login não diferencia maiúsculas de minúsculas. Deixe a migração inicial pronta dentro do template, para o AUTH_USER_MODEL existir desde o primeiro migrate. Inclua cadastro, perfil, login, logout, troca de senha e reset de senha, usando as views do próprio Django, com templates em português.
>
> Crie também uma app core com três modelos abstratos (TimeStampedModel, UUIDModel, ActiveModel), um base.html com menu e mensagens, uma rota /health/ e um backend de e-mail de console que mostre a mensagem legível, com acentos.
>
> Configure o settings com python-decouple e dj-database-url, idioma pt-br e fuso de São Paulo. Escreva testes para o login por e-mail e para o fluxo completo de reset de senha.

## Short

* [Todo projeto Django começa igual? Conheça o Copier](https://youtube.com/shorts/6jqsywJzYG4) — agendado para 09/10/2026, às 10:00.
