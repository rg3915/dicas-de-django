# Django 6.1 + Docker ASMR Programming - No Talking

Publicado em 01/10/2026.

<a href="https://youtu.be/QA7Zpk8T4S4">
    <img src="../.gitbook/assets/youtube.png">
</a>

Django 6.1 do zero, sem narração: só o teclado. Um projeto completo, tudo no Docker: PostgreSQL 18, Mailpit e o Django 6.1 instalado com o **uv** dentro do container. Código em inglês, docstrings em português e templates HTML escritos com **Emmet**.

## O que é construído

* **core**: models abstratos (`TimeStampedModel` e `ActiveModel`) e o `base.html`.
* **accounts**: usuário com e-mail no login, logout e todo o fluxo de reset de senha (e-mail no Mailpit).
* **person**: cadastro de funcionários (`Employee`), grupos Vendedor e Gerente, e permissões (o vendedor não vê salário nem exclui; o gerente pode tudo).
* Novidade do Django 6.1: o e-mail se configura no `MAILERS`.

### Capítulos

* 00:00 Abertura
* 00:08 Docker: Dockerfile, compose.yaml e .env
* 01:26 Django 6.1 com uv, dentro do Docker
* 02:21 settings.py: apps, PostgreSQL 18, MAILERS (Mailpit)
* 03:53 App core: models abstratos e base.html
* 07:47 App accounts: login com e-mail e reset de senha
* 13:52 App person: funcionários, grupos e permissões
* 21:42 Subindo tudo: migrations, grupos e usuários
* 23:33 Navegando: vendedor, gerente, reset de senha e admin

## Série de shorts "Django do zero ASMR"

O vídeo também foi dividido em 21 shorts, publicados um a cada dois dias. Os que ainda não saíram já estão agendados para a data indicada.

| Data | Short |
|---|---|
| 02/10/2026 | [01. Docker: Dockerfile, compose.yaml e .env](https://youtube.com/shorts/pfdNbMxj9XY) |
| 04/10/2026 | <!--yt-pending RYgtFEu_mpo short-->02. Django 6.1 com uv, dentro do Docker<!--/yt-pending--> |
| 06/10/2026 | <!--yt-pending m7VSO2c2XTs short-->03. settings.py: PostgreSQL 18 e MAILERS<!--/yt-pending--> |
| 08/10/2026 | <!--yt-pending DK0wBCVK3uU short-->04. App core: models abstratos, view e urls<!--/yt-pending--> |
| 10/10/2026 | <!--yt-pending rmH2ryVtvJw short-->05. base.html com Emmet<!--/yt-pending--> |
| 12/10/2026 | <!--yt-pending -Yam3-cLrLw short-->06. index.html, 403.html e urls do projeto<!--/yt-pending--> |
| 14/10/2026 | <!--yt-pending 63jfz3rk-wA short-->07. accounts: usuário com login por e-mail<!--/yt-pending--> |
| 16/10/2026 | <!--yt-pending 7dF5xftjqpE short-->08. accounts: forms, admin e urls<!--/yt-pending--> |
| 18/10/2026 | <!--yt-pending n9WEV05jwjE short-->09. Templates de login e reset de senha<!--/yt-pending--> |
| 20/10/2026 | <!--yt-pending GfeXJXgsfh8 short-->10. Reset de senha: confirmar a nova senha<!--/yt-pending--> |
| 22/10/2026 | <!--yt-pending 36IzuFs9NoY short-->11. person: model Employee e form<!--/yt-pending--> |
| 24/10/2026 | <!--yt-pending t6xov5ucwAc short-->12. person: views com permissões<!--/yt-pending--> |
| 26/10/2026 | <!--yt-pending PQPoX2Pj14I short-->13. person: urls e admin<!--/yt-pending--> |
| 28/10/2026 | <!--yt-pending 7E86xgWd31I short-->14. Lista de funcionários com Emmet<!--/yt-pending--> |
| 30/10/2026 | <!--yt-pending Lwnzy3fhyuM short-->15. Form e confirmação de exclusão<!--/yt-pending--> |
| 01/11/2026 | <!--yt-pending XcGmd8gh5v4 short-->16. Comando create_groups: Vendedor e Gerente<!--/yt-pending--> |
| 03/11/2026 | <!--yt-pending ydEBp9u2urE short-->17. Subindo tudo: migrate, grupos e usuários<!--/yt-pending--> |
| 05/11/2026 | <!--yt-pending W_8__T2Lxg4 short-->18. Navegando: o vendedor cadastra, mas não exclui<!--/yt-pending--> |
| 07/11/2026 | <!--yt-pending d5As5VHoWlg short-->19. Navegando: o gerente edita e exclui<!--/yt-pending--> |
| 09/11/2026 | <!--yt-pending 56byLG5r9Zw short-->20. Navegando: reset de senha pelo Mailpit<!--/yt-pending--> |
| 11/11/2026 | <!--yt-pending FF5NhPLtWSw short-->21. Navegando: grupos e permissões no admin<!--/yt-pending--> |
