# Dicas de Django

https://www.dicas-de-django.com.br/


## Qual branch usar?

Você está na `main`, que tem **só o código do projeto Django**. O [site](https://www.dicas-de-django.com.br/) é estático, não usa este Django e fica na branch `site`. O código mostrado nos vídeos antigos fica guardado em tags.

| O que você quer fazer | Onde |
|---|---|
| Rodar o projeto Django ou criar um recurso nele | branch `main` (esta) |
| Ler ou corrigir uma dica, ou mudar o site | branch [`site`](https://github.com/rg3915/dicas-de-django/tree/site) (antiga `master`) |
| Acompanhar uma aula em vídeo | tags `aula01` a `aula23` (tabela abaixo) |
| Acompanhar os vídeos das dicas 1 a 60 | tag [`main_old`](https://github.com/rg3915/dicas-de-django/tree/main_old) |
| Ver o código de importação e exportação de dados | tag [`import`](https://github.com/rg3915/dicas-de-django/tree/import) |
| Ver os exemplos de 2021 | tags [`signals`](https://github.com/rg3915/dicas-de-django/tree/signals) e [`inlineformset-htmx`](https://github.com/rg3915/dicas-de-django/tree/inlineformset-htmx) |

### O vídeo fala em uma branch que não aparece na lista

Ela virou uma tag com o mesmo nome e o mesmo código. No GitHub, procure na aba **Tags** do seletor de branches. Os links antigos continuam funcionando.

Para acompanhar uma aula no seu computador:

```
git clone https://github.com/rg3915/dicas-de-django.git
cd dicas-de-django
git switch -c minha-aula06 aula06
```

<details>
<summary>Tag de cada aula</summary>

| Tag | Assunto | Tag | Assunto |
|---|---|---|---|
| `aula01` | Criando issues com a API do GitHub | `aula13` | Dashboard com Django e Tailwind CSS |
| `aula02` | Usando http.server | `aula14` | Custom User com e-mail |
| `aula03` | Template com Bulma CSS | `aula15` | Login com e-mail |
| `aula04` | Template com Tailwind CSS | `aula16` | Logout |
| `aula05` | htmx simples | `aula17` | Cadastro de usuários |
| `aula06` | Criando o projeto Django | `aula18` | Esqueci a senha |
| `aula07` | PostgreSQL, pgAdmin e MailHog com docker-compose | `aula19` | OneToMany |
| `aula08` | isort e autopep8 | `aula20` | OneToOne |
| `aula09` | djhtml | `aula21` | ManyToMany |
| `aula10` | Makefile | `aula22` | Abstract |
| `aula11` | Landpage de produtos | `aula23` | Proxy model |
| `aula12` | Fale conosco com formulário | | |

</details>

### Como contribuir sem quebrar os vídeos

* **Código Django:** crie sua branch a partir da `main` e abra o pull request para a `main`.
* **Dicas e site:** crie sua branch a partir da `site` e abra o pull request para a `site`. Ao entrar na `site`, a mudança é publicada no site.
* **Não faça merge entre `main` e `site`:** os históricos são diferentes.
* **Não altere nem apague as tags:** vídeos e dicas apontam para elas.
* **A branch padrão continua sendo a `main`:** os vídeos que apontam para a raiz do repositório abrem nela.


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


## Leia o passo a passo

Todas as dicas estão no [site](https://www.dicas-de-django.com.br/).

