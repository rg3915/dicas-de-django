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
| 04/10/2026 | [02. Django 6.1 com uv, dentro do Docker](https://youtube.com/shorts/RYgtFEu_mpo) |
| 06/10/2026 | [03. settings.py: PostgreSQL 18 e MAILERS](https://youtube.com/shorts/m7VSO2c2XTs) |
| 08/10/2026 | [04. App core: models abstratos, view e urls](https://youtube.com/shorts/DK0wBCVK3uU) |
| 10/10/2026 | [05. base.html com Emmet](https://youtube.com/shorts/rmH2ryVtvJw) |
| 12/10/2026 | [06. index.html, 403.html e urls do projeto](https://youtube.com/shorts/-Yam3-cLrLw) |
| 14/10/2026 | [07. accounts: usuário com login por e-mail](https://youtube.com/shorts/63jfz3rk-wA) |
| 16/10/2026 | [08. accounts: forms, admin e urls](https://youtube.com/shorts/7dF5xftjqpE) |
| 18/10/2026 | [09. Templates de login e reset de senha](https://youtube.com/shorts/n9WEV05jwjE) |
| 20/10/2026 | [10. Reset de senha: confirmar a nova senha](https://youtube.com/shorts/GfeXJXgsfh8) |
| 22/10/2026 | [11. person: model Employee e form](https://youtube.com/shorts/36IzuFs9NoY) |
| 24/10/2026 | [12. person: views com permissões](https://youtube.com/shorts/t6xov5ucwAc) |
| 26/10/2026 | [13. person: urls e admin](https://youtube.com/shorts/PQPoX2Pj14I) |
| 28/10/2026 | [14. Lista de funcionários com Emmet](https://youtube.com/shorts/7E86xgWd31I) |
| 30/10/2026 | [15. Form e confirmação de exclusão](https://youtube.com/shorts/Lwnzy3fhyuM) |
| 01/11/2026 | [16. Comando create_groups: Vendedor e Gerente](https://youtube.com/shorts/XcGmd8gh5v4) |
| 03/11/2026 | [17. Subindo tudo: migrate, grupos e usuários](https://youtube.com/shorts/ydEBp9u2urE) |
| 05/11/2026 | [18. Navegando: o vendedor cadastra, mas não exclui](https://youtube.com/shorts/W_8__T2Lxg4) |
| 07/11/2026 | [19. Navegando: o gerente edita e exclui](https://youtube.com/shorts/d5As5VHoWlg) |
| 09/11/2026 | [20. Navegando: reset de senha pelo Mailpit](https://youtube.com/shorts/56byLG5r9Zw) |
| 11/11/2026 | [21. Navegando: grupos e permissões no admin](https://youtube.com/shorts/FF5NhPLtWSw) |
