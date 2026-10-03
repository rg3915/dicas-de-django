# Desenvolvimento Web com Django - palestra

Publicado em 14/07/2025.

<a href="https://youtu.be/DGoSA9T-1Qc">
    <img src="../.gitbook/assets/youtube.png">
</a>

Palestra realizada em 26/06/2025 na Semana Tecnológica TADS 2025 no Instituto Federal do Pará, Campus Itajuba.

## O que é visto

Uma introdução completa ao Django: página simples, banco de dados, settings, migrate, ORM, models, admin, views, urls, templates e o padrão MTV.

## Dicas da palestra

* Nunca versione a `SECRET_KEY`. Com **python-decouple**, use `SECRET_KEY = config('SECRET_KEY')` e guarde o valor no `.env`, que fica no `.gitignore`.
* Dinheiro? Use `DecimalField` com `max_digits` e `decimal_places`, nunca `FloatField`.
* Use o mesmo banco em desenvolvimento e produção. O SQLite aceita 101 caracteres num `CharField(max_length=100)`; o PostgreSQL recusa.
* Nos templates, prefira `{% url 'produto:produto_list' %}` a escrever a URL na mão.
* Senhas ficam com hash no banco. Para trocar a senha pelo shell, use `user.set_password('nova')` e depois `user.save()`.
