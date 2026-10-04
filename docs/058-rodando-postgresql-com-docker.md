# Dica 58 - Rodando PostgreSQL com Docker + Portainer + pgAdmin + Django local para desenvolvimento

**Versões usadas no vídeo:** Django 4.0, Python 3.8, PostgreSQL 13.4 (imagem `postgres:13.4-alpine`), pgAdmin 4, psycopg2-binary 2.9.2 e docker-compose com arquivo na versão 3.8.
{: .versoes }

<a href="https://youtu.be/aWZDFKJz7X8">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/django-postgresql-docker](https://github.com/rg3915/django-postgresql-docker)

Suponha que você queira usar o PostgreSQL no seu projeto Django, mas não quer instalar o PostgreSQL na sua máquina. A solução: rodar o PostgreSQL dentro de um container Docker e continuar rodando o Django na sua máquina local, fora do container. Nesta dica vamos montar esse ambiente de desenvolvimento:

* o **PostgreSQL** num container, na porta 5432 dentro do container e 5433 do lado de fora;
* o **pgAdmin** em outro container, na porta 80 dentro do container e 5050 do lado de fora, para administrar o banco pelo navegador;
* os dois juntos num `docker-compose.yml`, na mesma rede;
* o **Portainer**, num container separado, fora do docker-compose, na porta 9000, para monitorar os containers;
* o **Django** rodando localmente na porta 8000, conectado ao PostgreSQL do container pela porta 5433.

```
             docker-compose
  ┌───────────────────────────────────────┐
  │  db (PostgreSQL)      pgadmin         │
  │  5433:5432  <───────  5050:80         │       Portainer
  └───────────────────────────────────────┘  <──  9000
        ^
        │
     Django (local)
     8000
```

Este vídeo supõe que você já tem uma noção de Docker e docker-compose. Se quiser se aprofundar, veja os vídeos que passaram pelo canal (links da descrição do vídeo):

* PostgreSQL com Juliano Atanázio: [https://youtu.be/ABGbZYY4e3o](https://youtu.be/ABGbZYY4e3o)
* Docker com Gomex: [https://youtu.be/lEPTR2AbRto](https://youtu.be/lEPTR2AbRto)
* Docker-compose com Gomex: [https://youtu.be/CByr4db4shQ](https://youtu.be/CByr4db4shQ)

## Pré-requisitos

Instale o [docker](https://docs.docker.com/get-docker/) e o [docker-compose](https://docs.docker.com/compose/install/) na sua máquina e confira:

```bash
docker --version
docker-compose --version
```

## Portainer

Vamos usar o [Portainer](https://www.portainer.io/) para monitorar os nossos containers. Ele roda fora do docker-compose, com este comando:

```bash
# Portainer
docker run -d \
--name myportainer \
-p 9000:9000 \
--restart always \
-v /var/run/docker.sock:/var/run/docker.sock \
-v /opt/portainer:/data \
portainer/portainer
```

Como ele tem `--restart always`, basta rodar uma vez: ele sobe sozinho junto com o Docker. Acesse [http://localhost:9000](http://localhost:9000), crie o usuário administrador e, em **Containers**, você vê todos os containers da máquina, com status, logs, estatísticas e console de cada um. No vídeo ele já estava rodando, com o container `myportainer`.

## Escrevendo o docker-compose.yml

Crie a pasta do projeto e, dentro dela, o arquivo `docker-compose.yml`:

```bash
mkdir django-postgresql-docker
cd django-postgresql-docker
touch docker-compose.yml
```

```yaml
# docker-compose.yml
version: "3.8"

services:
  database:
    container_name: db
    image: postgres:13.4-alpine
    restart: always
    user: postgres  # importante definir o usuário
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - LC_ALL=C.UTF-8
      - POSTGRES_PASSWORD=postgres  # senha padrão
      - POSTGRES_USER=postgres  # usuário padrão
      - POSTGRES_DB=db  # necessário porque foi configurado assim no settings
    ports:
      - 5433:5432  # repare na porta externa 5433
    networks:
      - postgres

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4
    restart: unless-stopped
    volumes:
       - pgadmin:/var/lib/pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: admin
      PGADMIN_CONFIG_SERVER_MODE: 'False'
    ports:
      - 5050:80
    networks:
      - postgres

volumes:
  pgdata:  # mesmo nome do volume externo definido na linha 10
  pgadmin:

networks:
  postgres:
```

Explicando:

* `version: "3.8"` é a versão do formato do arquivo do docker-compose.
* Temos dois serviços, `database` e `pgadmin`, dois volumes nomeados, `pgdata` e `pgadmin`, e uma rede, `postgres`. Os dois serviços estão na mesma rede para o pgAdmin enxergar o banco.
* `container_name: db` dá um nome fixo ao container, que vamos usar nos comandos `docker container exec` e também como endereço do banco dentro da rede do Docker.
* `user: postgres` é importante: sem definir o usuário, não conseguimos conectar.
* O volume `pgdata:/var/lib/postgresql/data` guarda os dados do banco fora do container; assim eles não se perdem quando o container é recriado. O nome usado no serviço (linha 10) tem que ser o mesmo declarado em `volumes:` no fim do arquivo.
* Em `environment`, `POSTGRES_USER` e `POSTGRES_PASSWORD` definem o usuário e a senha padrão, e `POSTGRES_DB=db` cria o banco `db`, que é o nome que vamos configurar no `settings.py`.
* Em `ports`, `5433:5432` significa porta 5433 na sua máquina e 5432 dentro do container. Não usamos 5432 do lado de fora porque, se você já tiver um PostgreSQL instalado na sua máquina, a porta estaria ocupada e daria conflito.
* O pgAdmin usa a imagem `dpage/pgadmin4`, com o e-mail `admin@admin.com` e a senha `admin` para entrar, e fica acessível em `5050`.

## Criando o projeto Django

Crie o virtualenv, instale o Django, o python-decouple e o django-extensions e grave as versões no `requirements.txt`:

```bash
python -m venv .venv
source .venv/bin/activate

pip install django python-decouple django-extensions
pip freeze | grep Django >> requirements.txt
pip freeze | grep python-decouple >> requirements.txt
pip freeze | grep django-extensions >> requirements.txt
cat requirements.txt
```

```
Django==4.0
python-decouple==3.5
django-extensions==3.1.5
```

Crie o projeto na pasta atual:

```bash
django-admin startproject backend .
```

## Variáveis de ambiente

Crie o `.env` com as variáveis do projeto. Repare que os dados do banco são os mesmos do `docker-compose.yml`: banco `db`, usuário `postgres` e senha `postgres`. O `DB_HOST` é `localhost`, porque o Django roda na sua máquina e acessa o banco pela porta publicada.

```bash
cat << EOF > .env
SECRET_KEY=my-super-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,.localhost,0.0.0.0
POSTGRES_DB=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=localhost
EOF

cat .env
```

## Criando a app

No vídeo a app foi criada de dentro da pasta `backend`:

```bash
cd backend
python ../manage.py startapp core
cd ..
```

O mesmo resultado se obtém criando a app na raiz e movendo-a:

```bash
python manage.py startapp core
mv core/ backend/
```

Edite o `apps.py` para o nome completo da app:

```python
# backend/core/apps.py
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.core'
```

## Editando o settings.py

```python
# backend/settings.py
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd apps
    'django_extensions',
    # my apps
    'backend.core',
]

...

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', 'db'),  # postgres
        'USER': config('POSTGRES_USER', 'postgres'),
        'PASSWORD': config('POSTGRES_PASSWORD', 'postgres'),
        # 'db' caso exista um serviço com esse nome.
        'HOST': config('DB_HOST', '127.0.0.1'),
        'PORT': '5433',
    }
}

...

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

...

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR.joinpath('staticfiles')
```

O banco SQLite padrão foi comentado e substituído pelo PostgreSQL. Cada `config()` lê o valor do `.env` e, se ele não existir, usa o segundo argumento como padrão. A porta é `5433`, a porta externa do container. O comentário do `HOST` lembra que, se o Django também rodasse dentro do docker-compose, o endereço seria o nome do serviço (`db`), e não `localhost`.

## Rodando os containers

```bash
docker-compose up -d
```

O `-d` roda os containers em segundo plano (*detached*). Na primeira vez o Docker baixa as imagens `postgres:13.4-alpine` e `dpage/pgadmin4` e cria os containers `db` e `pgadmin`.

Para saber se está tudo certo, abra o Portainer e atualize a lista de containers: o `db` aparece como *running*, e em **Logs** você vê o PostgreSQL pronto para receber conexões:

```
PostgreSQL init process complete; ready for start up.

... LOG:  starting PostgreSQL 13.4 on x86_64-pc-linux-musl, compiled by gcc (Alpine 10.3.1_git20210424) 10.3.1 20210424, 64-bit
... LOG:  listening on IPv4 address "0.0.0.0", port 5432
... LOG:  listening on IPv6 address "::", port 5432
... LOG:  database system is ready to accept connections
```

## Corrigindo um erro de instalação

Ao rodar as migrações pela primeira vez, aparece o erro:

```bash
python manage.py migrate
```

```
django.core.exceptions.ImproperlyConfigured: Error loading psycopg2 module: No module named 'psycopg2'
```

Falta o driver do PostgreSQL para o Python. Instale a versão binária e grave no `requirements.txt`:

```bash
pip install psycopg2-binary
pip freeze | grep psycopg2-binary >> requirements.txt
```

```
Successfully installed psycopg2-binary-2.9.2
```

## Rodando as migrações

```bash
python manage.py migrate
```

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying sessions.0001_initial... OK
```

As tabelas foram criadas no PostgreSQL do container.

## Criando os superusuários

```bash
python manage.py createsuperuser --username="admin" --email=""
python manage.py createsuperuser --username="regis" --email="regis@email.com"
```

## Entrando no container do banco para conferir os dados

Liste os containers:

```bash
docker container ls
```

```
CONTAINER ID   IMAGE                  COMMAND                  CREATED         STATUS         PORTS                                            NAMES
767e9d1aeb7b   dpage/pgadmin4         "/entrypoint.sh"         2 minutes ago   Up 2 minutes   443/tcp, 0.0.0.0:5050->80/tcp, :::5050->80/tcp   pgadmin
0126798e5172   postgres:13.4-alpine   "docker-entrypoint.s…"   2 minutes ago   Up 2 minutes   0.0.0.0:5433->5432/tcp, :::5433->5432/tcp        db
9a6a1981c645   portainer/portainer    "/portainer"             2 months ago    Up 11 hours    0.0.0.0:9000->9000/tcp, :::9000->9000/tcp        myportainer
```

Entre no `psql` dentro do container `db`:

```bash
docker container exec -it db psql
# ou
docker container exec -it db psql -h localhost -U postgres db
```

Conecte-se ao banco `db`, liste as tabelas e consulte os usuários:

```
postgres=# \c db
You are now connected to database "db" as user "postgres".
db=# \dt
db=# SELECT username, email FROM auth_user;
 username |      email
----------+-----------------
 admin    |
 regis    | regis@email.com
(2 rows)

db=# \q
```

Se o banco `db` não existisse, daria para criá-lo ali mesmo:

```sql
CREATE DATABASE db;
CREATE DATABASE db OWNER postgres;
```

## Conferindo os logs

```bash
docker container logs -f db
```

O `-f` fica acompanhando o log do container (saia com `Ctrl+C`). Você também pode ver tudo pelo Portainer.

## Rodando o Django localmente

```bash
python manage.py runserver
```

O Django roda normalmente na sua máquina, em [http://localhost:8000](http://localhost:8000), usando o banco do container. Entre no Admin com o usuário `admin`: os dois usuários criados estão lá.

## pgAdmin

Entre no pgAdmin em [http://localhost:5050](http://localhost:5050) (pelo Portainer também dá para abrir o endereço publicado do container `pgadmin`). Com `PGADMIN_CONFIG_SERVER_MODE: 'False'`, ele não pede login, só uma senha mestra (*master password*) para guardar as senhas das conexões.

Depois clique com o botão direito em **Servers > Create > Server...** e preencha:

* **General > Name:** `db`
* **Connection > Host name/address:** `db`
* **Connection > Port:** `5432`
* **Connection > Maintenance database:** `postgres`
* **Connection > Username:** `postgres`
* **Connection > Password:** `postgres`

Repare que aqui o host é `db` e a porta é `5432`, e não `localhost:5433`: o pgAdmin está dentro da rede `postgres` do docker-compose e acessa o banco pelo nome do container e pela porta interna.

Salve, e a conexão aparece. Navegue em **db > Schemas > public > Tables** e veja as tabelas do Django. Clicando com o botão direito em `auth_user` e em **View/Edit Data > All Rows**, o pgAdmin roda:

```sql
SELECT * FROM public.auth_user
ORDER BY id ASC
```

e mostra os dois usuários que criamos, `admin` e `regis`.

## Conclusão

Com um `docker-compose.yml` de poucas linhas, temos o PostgreSQL e o pgAdmin rodando em containers, sem instalar nada além do Docker, e o Django continua rodando localmente, conectado ao banco pela porta 5433. O Portainer completa o ambiente, mostrando o estado e os logs dos containers. Na próxima dica usamos esse mesmo projeto para fazer [busca por palavras acentuadas ou sem acento](059-django-busca-por-palavras-acentuadas-ou-sem-acento.md) com o PostgreSQL.

Observação: nas versões mais novas do Docker, o comando `docker-compose` virou `docker compose` (com espaço), e a chave `version` do arquivo deixou de ser necessária.
