# 10 pacotes do Awesome Django num projeto real

<!--agendado-->

> 📅 **Vídeos agendados:** a parte 1 sai no YouTube em **17/10/2026, às 09:00**, e a parte 2 em **24/10/2026, às 10:00** (vídeo completo + short de cada uma).

<!--/agendado-->

**Testado com:** Django 6.1.1 e Python 3.12.
{: .versoes }

Lista completa: [https://awesomedjango.org/](https://awesomedjango.org/)

Código do projeto: [https://github.com/rg3915/awesome-django-pacotes](https://github.com/rg3915/awesome-django-pacotes)

O [awesomedjango.org](https://awesomedjango.org/) reúne centenas de pacotes para Django. Para escolher, eu ranqueei os pacotes da lista pelos downloads no PyPI e pelas estrelas no GitHub, e instalei dez deles numa loja de livros (a "Livraria Awesome") com Django 6.1. Todos funcionaram no 6.1, sem precisar voltar para o 5.2 LTS.

## Parte 1: os 5 que estão em quase todo projeto

Somados, eles passam de 60 milhões de downloads por mês.

<!--yt-block DgAovvO3BkA video-->

Versão curta: <!--yt-pending ZV-wHV1W9E8 short-->short da parte 1 (17/10)<!--/yt-pending-->

| Pacote | Downloads/mês | Para quê |
|---|---|---|
| django-cors-headers | 18,4 mi | liberar o front (React, Vue) em outro domínio |
| whitenoise | 13,9 mi | estáticos em produção, com cache e Brotli, sem Nginx |
| django-filter | 13,6 mi | filtros pela URL, junto com o DRF |
| django-storages | 11,7 mi | uploads no S3, Google Cloud ou Azure |
| django-environ | 6,6 mi | `.env` e `DATABASE_URL`, fora do código |

### django-environ

Tudo que muda entre máquinas sai do código e vai para o `.env`, inclusive o banco inteiro numa URL:

```python
# config/settings.py
import environ

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])
DATABASES = {"default": env.db("DATABASE_URL")}
```

```
# .env
SECRET_KEY=troque-por-uma-chave-secreta-de-verdade
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Trocar para PostgreSQL é só mudar a linha: `DATABASE_URL=postgres://usuario:senha@localhost:5432/livraria`.

### django-cors-headers

O front em `localhost:5173` só consegue chamar a API se o Django disser que aquela origem pode:

```python
INSTALLED_APPS += ["corsheaders"]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware", ...]  # o mais alto possível

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
```

### whitenoise

Com `DEBUG=False`, o Django para de servir os estáticos. O whitenoise serve, com nome versionado (cache longo) e arquivos comprimidos em gzip e Brotli:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # logo depois do SecurityMiddleware
    ...
]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

```
DEBUG=False uv run python manage.py collectstatic --noinput
curl -I -H "Accept-Encoding: br" http://127.0.0.1:8010/static/admin/css/base.<hash>.css
```

### django-filter

Filtros pela URL em poucas linhas, junto com o Django REST Framework:

```python
# loja/filters.py
import django_filters

from .models import Livro


class LivroFilter(django_filters.FilterSet):
    categoria = django_filters.CharFilter(field_name="categoria__slug")

    class Meta:
        model = Livro
        fields = {
            "preco": ["gt", "lt"],
            "publicado_em": ["year"],
            "autor": ["icontains"],
        }
```

```python
# loja/api.py
class LivroViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Livro.objects.select_related("categoria")
    serializer_class = LivroSerializer
    filterset_class = LivroFilter
```

Agora valem `/api/livros/?preco__gt=50`, `?categoria=poesia` e `?publicado_em__year=1930`.

### django-storages

Os uploads vão para um bucket S3 (aqui, um MinIO local) trocando só o settings. Sem a variável no `.env`, continua no disco:

```python
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default=None)

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage"
        if AWS_S3_ENDPOINT_URL
        else "django.core.files.storage.FileSystemStorage",
    },
    ...
}
```

## Parte 2: 5 pacotes que parecem mágica

<!--yt-block Qw3HjPzrcm8 video-->

Versão curta: <!--yt-pending PJY4A8yyA7c short-->short da parte 2 (24/10)<!--/yt-pending-->

### django-simple-history

Uma linha no model e cada alteração vira histórico: quem mudou, o quê e quando. Pelo admin dá para comparar versões e reverter.

```python
from simple_history.models import HistoricalRecords


class Livro(models.Model):
    ...
    history = HistoricalRecords()
```

```python
MIDDLEWARE += ["simple_history.middleware.HistoryRequestMiddleware"]  # grava o usuário
```

### django-import-export

Importar e exportar Excel e CSV pelo admin, com prévia antes de gravar:

```python
# loja/resources.py
class LivroResource(resources.ModelResource):
    categoria = fields.Field(
        column_name="categoria",
        attribute="categoria",
        widget=ForeignKeyWidget(Categoria, field="nome"),
    )

    class Meta:
        model = Livro
        fields = ("id", "titulo", "autor", "preco", "categoria", "publicado_em", "estoque")
```

```python
# loja/admin.py
@admin.register(Livro)
class LivroAdmin(SimpleHistoryAdmin, ImportExportModelAdmin, ModelAdmin):
    resource_classes = [LivroResource]
    list_display = ["titulo", "autor", "categoria", "preco", "estoque", "publicado_em"]
```

### django-unfold

Um tema moderno para o admin, com modo escuro, filtros e painéis. Os apps do unfold entram **antes** do `django.contrib.admin`, e há integrações prontas com os dois pacotes acima:

```python
INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.import_export",
    "unfold.contrib.simple_history",
    "django.contrib.admin",
    ...
]

UNFOLD = {"SITE_TITLE": "Livraria Awesome", "THEME": "dark"}
```

No projeto, `USE_UNFOLD=False uv run python manage.py runserver` sobe o admin padrão, para comparar o antes e o depois.

### django-allauth

Cadastro, login por e-mail com confirmação obrigatória e login social com Google e GitHub:

```python
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
```

```python
# config/urls.py
path("accounts/", include("allauth.urls")),
```

### django-silk

Um raio-x de cada requisição: tempo, consultas SQL e de onde cada uma veio. No projeto, `/relatorio/` tem um N+1 de propósito:

```python
def relatorio_n_mais_1(request):
    livros = Livro.objects.all()  # 1 query + 1 por categoria no template
    ...

def relatorio_otimizado(request):
    livros = Livro.objects.select_related("categoria")  # 1 query só
    ...
```

No `/silk/`, o relatório foi de 31 consultas para 1.

## Como rodar o projeto

```
git clone https://github.com/rg3915/awesome-django-pacotes.git
cd awesome-django-pacotes
uv sync
cp .env.example .env            # e troque a SECRET_KEY
uv run python manage.py migrate
uv run python manage.py popular_loja
uv run python manage.py runserver 8010
```

O `popular_loja` cria as categorias, 30 livros brasileiros, usuários e um histórico de alterações no *Dom Casmurro*. Versões exatas de cada pacote estão no `uv.lock` do repositório.
