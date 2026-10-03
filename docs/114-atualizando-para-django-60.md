# Atualizando um projeto para o Django 6.0

Publicado em 02/03/2026.

**Testado com:** atualização do Django 4.0 com Python 3.10 para o Django 6.0 com Python 3.14.2.
{: .versoes }

<a href="https://youtu.be/R1IiagAoZio">
    <img src="../.gitbook/assets/youtube.png">
</a>

Projeto: [https://github.com/rg3915/django-experience](https://github.com/rg3915/django-experience)

Imagine que você começou num emprego novo e herdou um projeto que não é seu: o dev anterior saiu e o último commit tem três anos. O `django-experience` é exatamente isso: estava em Python 3.10, Django 4.0 e Django REST framework 3.12. Neste tutorial vamos atualizá-lo para Python 3.14, Django 6.0 e DRF 3.16, do jeito mais básico possível, com `pip` e `requirements.txt`.

## Pré-requisitos

* Python 3.12 ou mais recente. O Django 6.0 suporta Python 3.12, 3.13 e 3.14; a série 5.2 foi a última com suporte a 3.10 e 3.11. Eu usei o 3.14.2.
* Docker e Docker Compose (o projeto usa PostgreSQL em container).
* Git.

## 1. Clonar e criar a virtualenv

Siga o README do projeto:

```bash
git clone https://github.com/rg3915/django-experience.git
cd django-experience
python -m venv .venv
source .venv/bin/activate
```

## 2. Entender o requirements antigo

Este era o `requirements.txt` antes da atualização:

```text
# requirements.txt (antes)
autopep8==1.6.0
django-extensions==3.1.*
django-filter==21.1
django-seed==0.3.*
Django==4.0.*
djangorestframework==3.12.*
djhtml==1.4.11
djoser==2.1.0
dr-scaffold==2.1.*
drf-yasg==1.20.*
ipdb
psycopg2-binary==2.9.*
python-decouple==3.5
pytz
```

Todas as versões estão fixadas. Se você rodar `pip install -r requirements.txt` com Python 3.14, vai instalar o Django 4.0, que não suporta essa versão do Python. O objetivo é instalar as versões mais recentes de cada pacote e depois fixar as novas.

## 3. Instalar as versões novas

Copie a lista para um arquivo à parte (para não perder a referência) e instale os pacotes sem as versões, um por um. Dá para fazer com Poetry ou uv, mas aqui a ideia é usar o básico:

```bash
pip install autopep8
pip install django-extensions
pip install django-filter
pip install django-seed
pip install Django
pip install djangorestframework
pip install djhtml
pip install djoser
pip install dr-scaffold
pip install drf-yasg
pip install ipdb
pip install psycopg2-binary
pip install python-decouple
pip install pytz
```

Instalar um por um tem uma vantagem: se algum pacote não tiver versão compatível com o Python ou o Django novos, você descobre exatamente qual é.

Confira o resultado:

```bash
pip freeze | grep -i django
```

O Django foi para a 6.0 e o DRF para a 3.16.1.

## 4. Gravar o requirements novo

```bash
pip freeze > requirements.txt
```

Eu deixo o arquivo completo, com as dependências secundárias também fixadas. O resultado no repositório ficou assim:

```text
# requirements.txt (depois)
asgiref==3.11.0
asttokens==3.0.1
autopep8==2.3.2
certifi==2025.11.12
cffi==2.0.0
charset-normalizer==3.4.4
cryptography==46.0.3
decorator==5.2.1
defusedxml==0.7.1
Django==6.0
django-extensions==4.1
django-filter==25.2
django-seed==0.3.1
djangorestframework==3.16.1
djangorestframework_simplejwt==5.5.1
djhtml==3.0.10
djoser==2.3.3
dr-scaffold==2.1.2
drf-yasg==1.21.11
executing==2.2.1
Faker==39.0.0
idna==3.11
inflect==7.5.0
inflection==0.5.1
ipdb==0.13.13
ipython==9.8.0
ipython_pygments_lexers==1.1.1
isort==7.0.0
jedi==0.19.2
matplotlib-inline==0.2.1
more-itertools==10.8.0
oauthlib==3.3.1
packaging==25.0
parso==0.8.5
pexpect==4.9.0
prompt_toolkit==3.0.52
psycopg2-binary==2.9.11
ptyprocess==0.7.0
pure_eval==0.2.3
pycodestyle==2.14.0
pycparser==2.23
Pygments==2.19.2
PyJWT==2.10.1
python-decouple==3.8
python3-openid==3.2.0
pytz==2025.2
PyYAML==6.0.3
requests==2.32.5
requests-oauthlib==2.0.0
social-auth-app-django==5.7.0
social-auth-core==4.8.3
sqlparse==0.5.5
stack-data==0.6.3
toposort==1.10
traitlets==5.14.3
typeguard==4.4.4
typing_extensions==4.15.0
tzdata==2025.3
uritemplate==4.2.0
urllib3==2.6.2
wcwidth==0.2.14
```

Repare no `psycopg2-binary==2.9.11`: as notas do Django 6.0 pedem psycopg2 2.9.9 ou mais recente (ou psycopg 3.1.12 ou mais recente).

## 5. Atualizar o README

Registre as versões novas no README, para o próximo dev não passar pelo mesmo:

```markdown
> Projeto Atualizado em 21/12/25

## Este projeto foi feito com:

* [Python 3.14.2](https://www.python.org/)
* [Django 6.0](https://www.djangoproject.com/)
* [Django Rest Framework 3.16.1](https://www.django-rest-framework.org/)
* [Bootstrap 4.0](https://getbootstrap.com/)
* [htmx 1.6.1](https://htmx.org/)
```

Bootstrap e htmx são carregados no front-end e não dependem do Django, então ficaram como estavam.

## 6. Gerar o .env

O projeto tem um script que gera o `.env` com uma `SECRET_KEY` aleatória:

```bash
python contrib/env_gen.py
cat .env
```

```bash
# .env (gerado)
DEBUG=True
SECRET_KEY=<chave aleatória>
ALLOWED_HOSTS=127.0.0.1,.localhost,0.0.0.0

POSTGRES_DB=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=localhost
```

## 7. Subir o banco (o passo que faltava no README)

Seguindo o README, o próximo passo seria o `migrate`. Ele falha com erro de conexão na porta 5433. O `settings.py` aponta para essa porta:

```python
# backend/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', 'db'),  # postgres
        'USER': config('POSTGRES_USER', 'postgres'),
        'PASSWORD': config('POSTGRES_PASSWORD', 'postgres'),
        # 'db' caso exista um serviço com esse nome.
        'HOST': config('DB_HOST', '127.0.0.1'),
        'PORT': 5433,
    }
}
```

E quem publica essa porta é o `docker-compose.yml`, que o README não mandava subir. Aproveitei para atualizar a imagem do Postgres de `postgres:14-alpine` para `postgres:16.9-alpine`:

```yaml
# docker-compose.yml
version: "3.8"

services:
  database:
    container_name: db
    image: postgres:16.9-alpine
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

Atenção: se você já tinha um volume `pgdata` criado com o Postgres 14, a imagem 16 não abre esses dados (versões principais diferentes têm formatos diferentes). Em ambiente de desenvolvimento, o mais simples é apagar o volume antigo com `docker compose down -v`. Com dados que importam, faça um dump antes.

```bash
docker compose up --build -d
python manage.py migrate
```

Agora o `migrate` funciona.

## 8. O que mudou no Django 6.0 e afetaria este projeto

Antes de sair navegando, vale conferir as notas de lançamento. Os pontos que mais quebram projetos antigos:

* **Python 3.12 no mínimo**, como vimos.
* **`DEFAULT_AUTO_FIELD` agora é `BigAutoField` por padrão** e as linhas correspondentes saíram dos templates do `startproject` e do `startapp`. Este projeto já definia `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'` no `settings.py` e `default_auto_field` em cada `apps.py`, então nada muda. Se o seu projeto nunca tratou o aviso `models.W042`, adicione `DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'` para não gerar migrações de troca de tipo de chave primária.
* **E-mail**: o Django passou a usar a API moderna de e-mail do Python. Subclasses customizadas de `EmailMessage` que mexem em métodos internos precisam ser revisadas.
* **Expressões customizadas do ORM** devem retornar os parâmetros do `as_sql()` como tupla.

Para confirmar que nenhum model ficou com migração pendente por causa do upgrade:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
```

No `django-experience`, os dois retornam sem problemas (`System check identified no issues` e `No changes detected`).

## 9. Superusuário, dados e navegação

```bash
python manage.py createsuperuser --username="admin" --email=""
python manage.py create_data
python manage.py runserver
```

O `create_data` é um comando do próprio projeto (`backend/core/management/commands/create_data.py`) que gera clientes, usuários, grupos e permissões com o Faker. Ele também não estava no README; acrescentei:

```bash
# Para gerar dados aleatórios
python manage.py create_data
```

Agora navegue pelas telas. Tarefas: adicionar e salvar funcionou. Pedidos: ao clicar em adicionar, erro. A causa não é o Django 6.0, é o dado. O formulário de pedido filtra os funcionários pelo departamento do usuário logado:

```python
# backend/order/forms.py
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Retorna o funcionário logado.
        employee = user.user_employees.first()

        # Retorna o departamento do funcionário logado.
        department = employee.department
```

O usuário `admin` acabou de ser criado e não tem um `Employee` associado, então `employee` é `None` e `employee.department` estoura um `AttributeError`. A correção é cadastrar os dados no admin:

1. Em **Departamentos**, crie um departamento (eu criei "TI").
2. Em **Funcionários**, crie um funcionário com o usuário `admin` e o departamento "TI".
3. Em **Usuários**, preencha o nome do `admin`; a lista de pedidos mostra o nome completo do funcionário, e sem ele a coluna fica vazia.

Volte em Pedidos, adicione um pedido e ele salva. Confira também a API do DRF: continua funcionando.

Essa é a lição principal: erro de upgrade (ou de dado) aparece no uso, não no `pip install`. Navegue por todas as telas e endpoints.

## 10. Rodar os testes

```bash
python manage.py test
```

O projeto tem poucos testes (5, na app `video`), e todos passam no Django 6.0. Rode também com os avisos ligados, para ver o que vai quebrar na próxima versão:

```bash
python -W default manage.py test
```

No `django-experience` aparece um `DeprecationWarning` do `drf_yasg` sugerindo definir `SWAGGER_USE_COMPAT_RENDERERS = False` no `settings.py`. Não impede nada hoje, mas é o tipo de aviso que vale resolver antes de virar erro.

## 11. Commit

```bash
git add README.md docker-compose.yml requirements.txt
git commit -m "Projeto atualizado para Django 6.0"
```

No repositório, o commit da atualização alterou só esses três arquivos. O projeto não usava recursos sofisticados que tivessem sido removidos, então o código Python ficou intacto.

## Resumo

1. Ative uma virtualenv com Python 3.12 ou mais recente.
2. Instale os pacotes sem versão fixa e rode `pip freeze > requirements.txt`.
3. Atualize o README com as versões e com os passos que faltavam.
4. Suba o banco, rode `migrate`, `check` e `makemigrations --check`.
5. Navegue por todas as telas e pela API, e rode os testes com avisos ligados.

Referências:

* Notas de lançamento do Django 6.0: [https://docs.djangoproject.com/en/6.0/releases/6.0/](https://docs.djangoproject.com/en/6.0/releases/6.0/)
* Como atualizar o Django para uma versão nova: [https://docs.djangoproject.com/en/6.0/howto/upgrade-version/](https://docs.djangoproject.com/en/6.0/howto/upgrade-version/)
