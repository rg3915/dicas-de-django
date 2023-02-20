# Dicas de Django

https://www.dicas-de-django.com.br/


## Este projeto foi feito com:

* [Python 3.10.6](https://www.python.org/)
* [Django 4.1.6](https://www.djangoproject.com/)
* [TailwindCSS](https://tailwindcss.com/)
* [htmx](https://htmx.org)

## Como rodar o projeto?

* Clone esse repositório.
* Crie um virtualenv com Python 3.
* Ative o virtualenv.
* Instale as dependências.
* Rode as migrações.

```
git clone https://github.com/rg3915/dicas-de-django.git
cd dicas-de-django
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python contrib/env_gen.py

# crie .env.docker

cat << EOF > .env.docker
POSTGRES_DB=dicas_de_django_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
EOF

# Django docker
docker-compose up --build -d

docker container exec -it dicas_de_django_app python manage.py migrate
docker container exec -it dicas_de_django_app python manage.py createsuperuser --email="admin@email.com"

# Django local
python manage.py migrate
python manage.py createsuperuser --email="admin@email.com"
python manage.py test
python manage.py runserver
```

### Makefile

Para verifcar os comando disponiveis no Makefile no terminal, basta informar `make help`

**Obs:** Deve ter o `rich` instalado (`pip install rich`). Ele já está contido no `requirements.txt` instalado na venv, basta ativa-la `source .venv/bin/activate`


## branch antiga

branch: `main_old`

[Dicas 1 a 60](https://github.com/rg3915/dicas-de-django/tree/main_old)


## Leia o passo a passo

[Dicas de Django antigas](https://github.com/rg3915/dicas-de-django/tree/master/docs)

[Dicas de Django novas](doc/)

