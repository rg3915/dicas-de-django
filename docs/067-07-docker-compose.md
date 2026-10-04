# Dica 07 - PostgreSQL, pgAdmin e MailHog com docker-compose

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, Docker 20.10.21 com docker-compose (arquivo na versão "3.8"), PostgreSQL 14 (alpine), psycopg2-binary 2.9.5, gunicorn 20.1.0 e whitenoise 6.2.0.
{: .versoes }

<a href="https://youtu.be/eOMTjETFCko">
    <img src="../.gitbook/assets/youtube.png">
</a>

Continuando o projeto da [Dica 06](066-06-projeto-django.md), hoje vamos trabalhar com Docker e docker-compose. Já mostrei em vídeos anteriores como subir o PostgreSQL num container e rodar o Django **fora** dele, na máquina local. Agora vamos fazer as duas coisas: rodar o Django tanto fora quanto **dentro** do container, junto com PostgreSQL, pgAdmin, MailHog, nginx e WhiteNoise.

Código da aula: [https://github.com/rg3915/dicas-de-django/tree/aula07](https://github.com/rg3915/dicas-de-django/tree/aula07)

## A arquitetura

![](../.gitbook/assets/docker-compose.png)

No ambiente de desenvolvimento ficamos assim (em produção é diferente):

* **db**: PostgreSQL. Dentro da rede do docker-compose ele escuta na porta 5432; para fora, na **5431**.
* **pgadmin**: interface web do PostgreSQL, em `localhost:5051`. Ele fala com o `db` pela 5432, dentro da rede.
* **mailhog**: simula um servidor de e-mail. SMTP na porta 1025 e a interface web (HTTP) na 8025.
* **nginx**: recebe as requisições em `0.0.0.0:80` e repassa para o Django pela porta 8000.
* **app**: o Django dentro do container, rodando com gunicorn na porta 8000.
* Todos os serviços estão na mesma rede (`dicas-de-django-network`), para conversarem entre si.
* Fora do docker-compose: o Django local, em `localhost:8000`, que se conecta ao PostgreSQL pela 5431; e o Portainer, em `localhost:9000`, que monitora todos os containers.

No dia a dia vamos usar o Django **fora** do container, porque é mais fácil de depurar; o Django dentro do container fica como opção.

## Pré-requisitos

* O projeto da [Dica 06](066-06-projeto-django.md).
* Docker e docker-compose instalados. Instale o [docker](https://docs.docker.com/get-docker/) e o [docker-compose](https://docs.docker.com/compose/install/) na sua máquina.

```bash
git checkout -b aula07

docker --version
docker-compose --version
```

```
Docker version 20.10.21, build baeda1f
```

## Portainer

Vamos usar o [Portainer](https://www.portainer.io/) para monitorar nossos containers. Ele roda num container à parte, fora do docker-compose:

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

Acesse [http://localhost:9000](http://localhost:9000) e entre com o seu usuário (no vídeo, `admin`). No começo só aparece o container do próprio Portainer. Em **Containers** você vê o estado de cada container e, se algum der problema, pode abrir os **Logs** dele por ali.

![](../.gitbook/assets/portainer.png)

## docker-compose com PostgreSQL, pgAdmin e MailHog

```bash
touch docker-compose.yml
```

Edite `docker-compose.yml`

```yml
# docker-compose.yml
version: "3.8"

services:
  db:
    container_name: dicas_de_django_db
    image: postgres:14-alpine
    restart: always
    user: postgres  # importante definir o usuário
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - LC_ALL=C.UTF-8
      - POSTGRES_PASSWORD=postgres  # senha padrão
      - POSTGRES_USER=postgres  # usuário padrão
      - POSTGRES_DB=dicas_de_django_db  # necessário porque foi configurado assim no settings
    ports:
      - 5431:5432  # repare na porta externa 5431
    networks:
      - dicas-de-django-network

  pgadmin:
    container_name: dicas_de_django_pgadmin
    image: dpage/pgadmin4
    restart: unless-stopped
    volumes:
       - pgadmin:/var/lib/pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: admin
      PGADMIN_CONFIG_SERVER_MODE: 'False'
    ports:
      - 5051:80
    networks:
      - dicas-de-django-network

  mailhog:
    container_name: dicas_de_django_mailhog
    image: mailhog/mailhog
    restart: always
    logging:
      driver: 'none'
    ports:
      - 1025:1025
      - 8025:8025
    networks:
      - dicas-de-django-network

volumes:
  pgdata:  # mesmo nome do volume externo definido na linha 10
  pgadmin:

networks:
  dicas-de-django-network:
```

Explicando o serviço `db`:

* `image: postgres:14-alpine`: PostgreSQL 14 na imagem Alpine, bem menor.
* `user: postgres`: é importante definir o usuário que roda o processo.
* `volumes`: o volume nomeado `pgdata` guarda os dados do banco, então eles sobrevivem quando o container é recriado. O nome tem que ser o mesmo declarado em `volumes:` no fim do arquivo.
* `environment`: senha, usuário e nome do banco. O `POSTGRES_DB=dicas_de_django_db` cria o banco com o mesmo nome que vamos usar no `settings.py`.
* `ports: 5431:5432`: a porta externa é **5431** de propósito. Se você tiver um PostgreSQL instalado na máquina, ele já ocupa a 5432 e daria conflito.

O `pgadmin` usa o login `admin@admin.com` / `admin`, e o `PGADMIN_CONFIG_SERVER_MODE: 'False'` deixa ele no modo desktop (um usuário só, sem tela de cadastro). O `mailhog` não precisa de configuração: SMTP na 1025, interface web na 8025; o `logging: driver: 'none'` só desliga o log dele, que é muito verboso.

Suba os containers:

```bash
docker-compose up -d
```

## Configurando o Django para o PostgreSQL e o MailHog

Edite `settings.py`. Comente (ou apague) o SQLite e troque pelo PostgreSQL; logo abaixo, a configuração de e-mail:

```python
# backend/settings.py
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', 'dicas_de_django_db'),  # postgres
        'USER': config('POSTGRES_USER', 'postgres'),
        'PASSWORD': config('POSTGRES_PASSWORD', 'postgres'),
        # 'db' caso exista um serviço com esse nome.
        # 'HOST': config('DB_HOST', 'db'),
        'HOST': config('DB_HOST', 'localhost'),
        'PORT': config('DB_PORT', 5431, cast=int),
    }
}

# Email config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
EMAIL_HOST = config('EMAIL_HOST', 'localhost')  # localhost 0.0.0.0
EMAIL_PORT = config('EMAIL_PORT', 1025, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
```

* O segundo argumento do `config` é o valor padrão, usado quando a variável não está no `.env`.
* `HOST` é `localhost` e `PORT` é `5431`, porque por enquanto o Django roda **fora** do container e enxerga o PostgreSQL pela porta externa.
* E-mail: o `EMAIL_HOST` é `localhost` e a porta `1025`, que é o SMTP do MailHog. O MailHog não pede usuário nem senha, então `EMAIL_HOST_USER` e `EMAIL_HOST_PASSWORD` ficam vazios, e o TLS desligado.

Edite `contrib/env_gen.py` e acrescente a variável da porta junto com as do banco, para que os próximos `.env` gerados já venham com ela:

```
DB_PORT=
```

Edite `.env` (que não vai para o git) e deixe as variáveis do banco explícitas:

```
# .env
DEBUG=True
SECRET_KEY=...
ALLOWED_HOSTS=127.0.0.1,.localhost,0.0.0.0

#DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
POSTGRES_DB=dicas_de_django_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5431

#DEFAULT_FROM_EMAIL=
#EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
#EMAIL_HOST=localhost
#EMAIL_PORT=
#EMAIL_HOST_USER=
#EMAIL_HOST_PASSWORD=
#EMAIL_USE_TLS=True
```

## Rodando o Django local

```bash
python manage.py migrate
```

Na primeira vez dá erro, porque falta o driver do PostgreSQL:

```
django.core.exceptions.ImproperlyConfigured: Error loading psycopg2 module: No module named 'psycopg2'
```

Instale o `psycopg2-binary` e guarde no `requirements.txt`:

```bash
pip install psycopg2-binary
pip freeze | grep psycopg2 >> requirements.txt
```

Agora sim:

```bash
python manage.py migrate
python manage.py createsuperuser --username="admin" --email=""
python manage.py runserver
```

No `createsuperuser`, como usei uma senha curta, o Django avisa e pergunta se quer continuar mesmo assim:

```
Password:
Password (again):
Esta senha é muito curta. Ela precisa conter pelo menos 8 caracteres.
Esta senha é muito comum.
Bypass password validation and create user anyway? [y/N]: y
Superuser created successfully.
```

```
System check identified no issues (0 silenced).
November 25, 2022 - 13:45:44
Django version 4.1.3, using settings 'backend.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Entre no admin, em [http://localhost:8000/admin/](http://localhost:8000/admin/), e cadastre um usuário novo (no vídeo, `regis`), só para termos dados para ver no pgAdmin. No Portainer, atualizando a lista, aparecem os containers do docker-compose rodando.

## pgAdmin

Acesse [http://localhost:5051](http://localhost:5051) e conecte no pgAdmin. Clique em **Add New Server**:

* aba **General**, Name: `db` (qualquer nome);
* aba **Connection**: Host name/address `db` (o nome do serviço no docker-compose, porque o pgAdmin está dentro da mesma rede), Port `5432`, Username `postgres`, Password `postgres`.

![](../.gitbook/assets/pgadmin.png)

Em **Databases > dicas_de_django_db > Schemas > public > Tables**, clique com o **botão direito** em `auth_user` e escolha **View/Edit Data > All Rows**. Aparecem o `admin` e o usuário cadastrado pelo admin do Django.

Situação até aqui: PostgreSQL, pgAdmin e MailHog dentro do Docker, e o Django fora.

## Rodando o Django dentro do container

Falta colocar o próprio Django e o nginx no docker-compose. Instale o gunicorn, que é o servidor WSGI que vai rodar o Django no container:

```bash
pip install gunicorn
pip freeze | grep gunicorn >> requirements.txt
```

Crie o `Dockerfile`, na raiz do projeto:

```dockerfile
# Dockerfile
FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV dev
ENV DOCKER_CONTAINER 1
RUN mkdir /app
WORKDIR /app
EXPOSE 8000

COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt

COPY manage.py .
COPY backend backend

CMD python manage.py collectstatic --no-input
CMD gunicorn backend.wsgi:application -b 0.0.0.0:8000
```

* A imagem base é o Python 3.10 slim.
* Cria a pasta `/app`, define como pasta de trabalho e expõe a porta 8000.
* Copia o `requirements.txt` antes do código e instala as dependências. Assim, se só o código mudar, o Docker reaproveita a camada do `pip install`.
* Copia o `manage.py` e a pasta `backend`.
* Por fim, o comando do gunicorn: `backend.wsgi:application` na porta 8000.

Repare que há dois `CMD`. Num Dockerfile só o **último** `CMD` vale, então o `collectstatic` não roda por ali. E, de qualquer forma, o `command` do docker-compose (abaixo) sobrepõe o `CMD`.

Edite `docker-compose.yml` e acrescente os serviços `app` e `nginx` depois do `mailhog`:

```yml
# docker-compose.yml
version: "3.8"

services:
  ...

  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: dicas_de_django_app
    hostname: app
    stdin_open: true
    expose:
      - '8000'
    volumes:
      - .env.docker:/app/.env
    command: bash -c "gunicorn backend.wsgi:application -b 0.0.0.0:8000"
    depends_on:
      - db
    networks:
      - dicas-de-django-network

  nginx:
    container_name: dicas_de_django_nginx
    image: nginx
    hostname: nginx
    ports:
      - '80:8000'
    volumes:
      - ./docker/config/nginx/:/etc/nginx/conf.d/
    depends_on:
      - app
    networks:
      - dicas-de-django-network
```

* `build`: a imagem do `app` é construída com o nosso `Dockerfile`.
* `expose: '8000'`: a porta fica visível só dentro da rede (para o nginx), não na máquina.
* `volumes: .env.docker:/app/.env`: o container lê um `.env` próprio, o `.env.docker`, que criaremos já já.
* `command`: o mesmo comando do gunicorn, sobrepondo o `CMD` do Dockerfile.
* `depends_on: db`: o `app` só sobe depois do `db`.
* O `nginx` publica a porta **80** da máquina para a 8000 do container dele, e lê a configuração da pasta `docker/config/nginx/`.

O arquivo completo, com os cinco serviços, está em [aula07/docker-compose.yml](https://github.com/rg3915/dicas-de-django/blob/aula07/docker-compose.yml).

Crie a configuração do nginx:

```bash
mkdir -p docker/config/nginx/
touch docker/config/nginx/app.conf
```

Edite `docker/config/nginx/app.conf`

```nginx
# docker/config/nginx/app.conf
# define group app
upstream app {
  # define server app
  server app:8000;
}

# server
server {
  listen 8000;
  charset utf-8;

  client_max_body_size 50M;

  # domain localhost
  server_name localhost;

  # Handle favicon.ico
  location = /favicon.ico {
    return 204;
    access_log off;
    log_not_found off;
  }

  # Django app
  location / {
    proxy_pass http://app;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $host;
    proxy_redirect off;
  }
}
```

O importante aqui: no `upstream`, `server app:8000` aponta para o serviço `app` (o nome do serviço vira o nome do host dentro da rede); o nginx escuta (`listen`) na 8000, e o `proxy_pass` é só `http://app`, o nome do `upstream`.

Crie o `.env.docker`, copiando o `.env`. A diferença é o banco: dentro da rede do Docker o host é o serviço `db` e a porta é a interna, `5432`.

```
# .env.docker
DEBUG=True
SECRET_KEY=...
ALLOWED_HOSTS=127.0.0.1,.localhost,0.0.0.0

#DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/NAME
POSTGRES_DB=dicas_de_django_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

#DEFAULT_FROM_EMAIL=
#EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
#EMAIL_HOST=localhost
#EMAIL_PORT=
#EMAIL_HOST_USER=
#EMAIL_HOST_PASSWORD=
#EMAIL_USE_TLS=True
```

Coloque `.env.docker` no `.gitignore`, porque ele também tem a `SECRET_KEY`:

```
.env.docker
```

Suba tudo de novo, agora construindo a imagem do `app`:

```bash
docker-compose up --build -d

docker container ls
```

```
CONTAINER ID   IMAGE                 COMMAND                  ...   PORTS                                            NAMES
3469535ff0d5   nginx                 "/docker-entrypoint.…"   ...   80/tcp, 0.0.0.0:80->8000/tcp                     dicas_de_django_nginx
248cea769ab0   dicas-de-django_app   "bash -c 'gunicorn b…"   ...   8000/tcp                                         dicas_de_django_app
c361a90c1ce9   mailhog/mailhog       "MailHog"                ...   0.0.0.0:1025->1025/tcp, 0.0.0.0:8025->8025/tcp   dicas_de_django_mailhog
b43f1ce0380d   postgres:14-alpine    "docker-entrypoint.s…"   ...   0.0.0.0:5431->5432/tcp                           dicas_de_django_db
befb4e509306   dpage/pgadmin4        "/entrypoint.sh"         ...   443/tcp, 0.0.0.0:5051->80/tcp                    dicas_de_django_pgadmin
629cb34930b2   portainer/portainer   "/portainer"             ...   0.0.0.0:9000->9000/tcp                           myportainer
```

Rode as migrations e crie o superusuário **dentro** do container:

```bash
docker container exec -it dicas_de_django_app python manage.py migrate
docker container exec -it dicas_de_django_app python manage.py createsuperuser --username="admin" --email=""
```

No vídeo, o `migrate` responde `No migrations to apply.` e o `createsuperuser` diz `Error: That usuário is already taken.`: o Django do container usa o **mesmo** banco (o mesmo volume `pgdata`) em que já rodamos tudo pelo Django local. Pode ignorar.

Acesse [http://localhost](http://localhost) (porta 80): é o Django rodando no container, através do nginx.

## Servindo arquivos estáticos no Docker com WhiteNoise

Ao abrir [http://localhost/admin/](http://localhost/admin/), o admin aparece sem CSS: na aba Network do navegador, os arquivos estáticos dão 404. O gunicorn não serve arquivos estáticos (quem faz isso no `runserver` é o próprio Django, em modo debug).

Para servir os estáticos no Docker vamos usar o [WhiteNoise](http://whitenoise.evans.io/en/latest/).

```bash
pip install whitenoise

pip freeze | grep whitenoise >> requirements.txt
```

Edite `settings.py` e coloque o middleware logo abaixo do `SecurityMiddleware`, como diz a documentação:

```python
# backend/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <<<
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

Reconstrua a imagem, porque o `requirements.txt` mudou:

```bash
docker-compose up --build -d
```

Agora o admin e os nossos estáticos carregam. Com `DEBUG=True`, o WhiteNoise encontra os arquivos direto nas pastas `static` das apps, sem precisar do `collectstatic`.

O `requirements.txt` no fim da aula:

```
# requirements.txt
click==8.1.3
python-decouple==3.6
requests==2.28.1
Django==4.1.3
django-extensions==3.2.1
psycopg2-binary==2.9.5
gunicorn==20.1.0
whitenoise==6.2.0
```

## Conclusão

Agora temos PostgreSQL, pgAdmin e MailHog no docker-compose, e o Django rodando tanto fora quanto dentro do container (com gunicorn, nginx e WhiteNoise). Nas próximas dicas vamos usar o Django **fora** do container, porque fica mais fácil de depurar.

Observação: num Mac com Apple Silicon (arm64), o `psycopg2-binary==2.9.5` dentro do container vem com uma `libpq` antiga e o Django do container falha com `SCRAM authentication requires libpq version 10 or above`. O Django local não é afetado; para o container, use uma versão mais nova do `psycopg2-binary`.
