# Postgres em vez de SQLite, até no dev

<!--agendado-->

> 📅 **Vídeo agendado:** será publicado no YouTube em **14/10/2026, às 10:00**.

<!--/agendado-->

<!--yt-block ikCqYsBHr6k short-->

O SQLite ignora o `max_length`: um `CharField(max_length=10)` aceita 18 letras, calado. O PostgreSQL dá `DataError` na hora, e é esse erro que você quer ver na sua máquina, não no seu cliente.

* O banco da sua máquina tem que ser igual ao da produção.
* De brinde: `django.contrib.postgres` (unaccent, SearchVector, ArrayField).
* E subir é um comando: `docker compose up -d`.
