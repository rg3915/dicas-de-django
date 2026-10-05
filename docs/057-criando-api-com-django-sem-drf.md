# Dica 57 - Criando API com Django SEM DRF

**Versões usadas no vídeo:** Django 3.2.10, django-extensions 3.1.5, python-decouple 3.5 e Python 3.8.
{: .versoes }

<a href="https://youtu.be/HLdREjEYVMU">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/django-api-without-drf](https://github.com/rg3915/django-api-without-drf)

Para fazer uma API REST em Python há várias opções: Flask, FastAPI, Django REST framework, Django Ninja... O desafio de hoje é fazer uma API REST **sem** o Django REST framework, só com o Django puro: `JsonResponse`, `ModelForm`, `json.loads` e alguns decorators. Vamos criar o projeto do zero, com um CRUD de vídeos em duas versões (`/api/v1/` com uma rota por ação e `/api/v2/` com só duas rotas), testar com o Postman e o httpie e escrever os testes.

## Criando o projeto

Com o virtualenv ativo, instale as dependências e gere o `requirements.txt`:

```bash
pip install django==3.2.10 django-extensions python-decouple
pip freeze
```

```
asgiref==3.4.1
Django==3.2.10
django-extensions==3.1.5
python-decouple==3.5
pytz==2021.3
sqlparse==0.4.2
```

```
# requirements.txt
Django==3.2.*
django-extensions==3.1.5
python-decouple==3.5
```

Crie o projeto `backend` na pasta atual (repare no ponto no final) e a app `core` dentro dele:

```bash
django-admin startproject backend .
cd backend/
python ../manage.py startapp core
cd ..
```

Como a app está dentro do pacote `backend`, corrija o nome dela no `apps.py`:

```python
# backend/core/apps.py
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.core'
```

## settings.py

Usamos o python-decouple para ler o `SECRET_KEY`, o `DEBUG` e o `ALLOWED_HOSTS` do arquivo `.env`, colocamos o `django_extensions` e a app `core` no `INSTALLED_APPS` e mudamos o idioma e o fuso horário:

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
    'django_extensions',
    'backend.core',
]

...

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'
```

O repositório tem o script `contrib/env_gen.py`, que gera o `.env` com um `SECRET_KEY` aleatório:

```bash
python contrib/env_gen.py
```

```
# .env
DEBUG=True
SECRET_KEY=...
ALLOWED_HOSTS=127.0.0.1,.localhost,0.0.0.0
```

## O modelo Video

```python
# backend/core/models.py
from django.db import models


class Video(models.Model):
    title = models.CharField('título', max_length=30)
    link = models.URLField(null=True, blank=True)
    view = models.IntegerField('visualização', default=0, null=True, blank=True)

    class Meta:
        ordering = ('id',)
        verbose_name = 'vídeo'
        verbose_name_plural = 'vídeos'

    def __str__(self):
        return f'{self.title}'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'link': self.link,
            'view': self.view,
        }
```

O método `to_dict()` é o nosso "serializer": ele transforma o objeto num dicionário, que o `JsonResponse` sabe converter em JSON.

Registre o modelo no Admin e crie o formulário, que vamos usar para validar e salvar os dados:

```python
# backend/core/admin.py
from django.contrib import admin

from .models import Video

admin.site.register(Video)
```

```python
# backend/core/forms.py
from django import forms

from .models import Video


class VideoForm(forms.ModelForm):

    class Meta:
        model = Video
        fields = ('title', 'link', 'view')
```

Rode as migrações e crie um superusuário:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --username="admin" --email=""
```

Entre no Admin e cadastre alguns vídeos. No vídeo foram cadastrados "Mini curso A Essência do Django" (`https://youtu.be/mlaCLGItR7Q`, 573 visualizações) e "Dica #50 - DRF: Django CORS headers + Lo" (`https://youtu.be/2SyQ9xXdMvw`, 195 visualizações). O título ficou cortado porque o `max_length` do título é 30.

## As rotas

```python
# backend/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('backend.core.urls', namespace='core')),
    path('admin/', admin.site.urls),
]
```

Na app, as rotas da versão 1 ficam numa lista `v1_urlpatterns`, incluída em `api/v1/`:

```python
# backend/core/urls.py
from django.urls import include, path

from backend.core import views as v

app_name = 'core'

v1_urlpatterns = [
    path('videos/', v.video_list, name='video_list'),
    path('videos/<int:pk>/', v.video_detail, name='video_detail'),
    path('videos/create/', v.video_create, name='video_create'),
    path('videos/<int:pk>/update/', v.video_update, name='video_update'),
    path('videos/<int:pk>/delete/', v.video_delete, name='video_delete'),
]

urlpatterns = [
    path('api/v1/', include(v1_urlpatterns)),
]
```

No vídeo as rotas foram acrescentadas uma a uma, à medida que as views eram criadas.

## Listando os vídeos

Os imports que vamos usar em todo o `views.py`:

```python
# backend/core/views.py
import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import VideoForm
from .models import Video


@require_http_methods(['GET'])
def video_list(request):
    videos = Video.objects.all()
    data = [video.to_dict() for video in videos]
    return JsonResponse({'data': data})
```

A list comprehension chama `to_dict()` em cada vídeo, e devolvemos tudo dentro da chave `data`. O `@require_http_methods(['GET'])` faz a view aceitar apenas o método GET; qualquer outro recebe `405 Method Not Allowed`.

Com o django-extensions, `python manage.py show_urls` confirma a rota, e em [http://localhost:8000/api/v1/videos/](http://localhost:8000/api/v1/videos/) aparece:

```json
{
  "data": [
    {
      "id": 1,
      "title": "Mini curso A Essência do Django",
      "link": "https://youtu.be/mlaCLGItR7Q",
      "view": 573
    },
    {
      "id": 2,
      "title": "Dica #50 - DRF: Django CORS headers + Lo",
      "link": "https://youtu.be/2SyQ9xXdMvw",
      "view": 195
    }
  ]
}
```

## Detalhe de um vídeo

```python
# backend/core/views.py
@require_http_methods(['GET'])
def video_detail(request, pk):
    video = Video.objects.get(pk=pk)
    data = video.to_dict()
    return JsonResponse({'data': data})
```

Em `/api/v1/videos/1/` aparece só o vídeo 1.

## Criando um vídeo

Para criar, o método é POST. Como não há formulário HTML com `{% csrf_token %}`, a view precisa do `@csrf_exempt`, senão o Django barra a requisição com 403.

Os dados podem chegar de dois jeitos:

* **form-data** (como um formulário): os dados vêm em `request.POST`, e podemos usar o `VideoForm`;
* **JSON** (corpo `raw`, tipo JSON): `request.POST` vem vazio, e os dados estão em `request.body`, em bytes.

Para descobrir isso, o vídeo usa o `ipdb` (`pip install ipdb` e `import ipdb; ipdb.set_trace()` dentro da view). Ao enviar um JSON pelo Postman, no depurador:

```
ipdb> request
<WSGIRequest: POST '/api/v1/videos/create/'>
ipdb> request.POST
<QueryDict: {}>
ipdb> request.body
b'{\n    "title": "Um",\n    "link": "um.com",\n    "view": 1\n}'
```

O `request.body` é uma string de bytes com o JSON, e `json.loads(request.body)` transforma isso num dicionário. A view fica assim:

```python
# backend/core/views.py
@csrf_exempt
@require_http_methods(['POST'])
def video_create(request):
    form = VideoForm(request.POST or None)

    if request.POST:
        # Dados obtidos pelo formulário.
        if form.is_valid():
            video = form.save()

    elif request.body:
        # Dados obtidos via json.
        data = json.loads(request.body)
        video = Video.objects.create(**data)

    else:
        return JsonResponse({'message': 'Algo deu errado.'})

    return JsonResponse({'data': video.to_dict()})
```

* Se veio `request.POST`, validamos e salvamos com o formulário.
* Se veio `request.body`, convertemos o JSON e criamos o vídeo com `Video.objects.create(**data)`: os dois asteriscos desempacotam o dicionário em argumentos nomeados (`title=..., link=..., view=...`).
* Se não veio nada, devolvemos uma mensagem de erro.

No Postman, faça um POST em `http://localhost:8000/api/v1/videos/create/` com **Body > form-data** (`title`, `link`, `view`) ou com **Body > raw > JSON**:

```json
{
    "title": "Um",
    "link": "um.com",
    "view": 1
}
```

Nos dois casos a resposta é o vídeo criado, já com o `id`.

## Editando um vídeo

```python
# backend/core/views.py
@csrf_exempt
@require_http_methods(['POST'])  # Não aceita PUT
def video_update(request, pk):
    video = get_object_or_404(Video, pk=pk)
    form = VideoForm(request.POST or None, instance=video)

    if request.POST:
        # Dados obtidos pelo formulário.
        if form.is_valid():
            video = form.save()

    elif request.body:
        # Dados obtidos via json.
        data = json.loads(request.body)

        for attr, value in data.items():
            setattr(video, attr, value)
        video.save()

    else:
        return JsonResponse({'message': 'Algo deu errado.'})

    return JsonResponse({'data': video.to_dict()})
```

As diferenças em relação à criação:

* o vídeo é buscado com `get_object_or_404`, que devolve 404 se o `pk` não existir;
* o formulário recebe `instance=video`, para atualizar em vez de criar;
* no caminho do JSON, **não** podemos usar `Video.objects.create(**data)`, porque isso criaria um vídeo novo (foi o que aconteceu no primeiro teste do vídeo). O certo é percorrer o dicionário e mudar cada atributo com `setattr(video, attr, value)` e depois salvar. Assim, dá para mandar só os campos que mudaram.

Aqui usamos POST; com PUT, o Django não preenche o `request.POST`, por isso o comentário `# Não aceita PUT`.

Teste com um POST em `http://localhost:8000/api/v1/videos/4/update/`: a resposta mostra o vídeo 4 alterado, sem criar um novo.

## Deletando um vídeo

```python
# backend/core/views.py
@csrf_exempt
@require_http_methods(['DELETE'])
def video_delete(request, pk):
    video = get_object_or_404(Video, pk=pk)
    video.delete()
    return JsonResponse({'data': 'Item deletado com sucesso.'})
```

Agora o método tem que ser DELETE: um POST em `/api/v1/videos/5/delete/` devolve `405 Method Not Allowed`. Com DELETE, a resposta é:

```json
{
    "data": "Item deletado com sucesso."
}
```

## Testando com o httpie

Além do Postman, dá para testar pelo terminal com o [httpie](https://httpie.io/):

```bash
pip install httpie
```

Listar e ver um vídeo:

```bash
http http://localhost:8000/api/v1/videos/
http http://localhost:8000/api/v1/videos/1/
```

```
{
    "data": {
        "id": 1,
        "link": "https://youtu.be/mlaCLGItR7Q",
        "title": "Mini curso A Essência do Django",
        "view": 573
    }
}
```

Criar um vídeo (o httpie envia os campos `chave=valor` como JSON):

```bash
http POST http://localhost:8000/api/v1/videos/create/ \
title="Dica #49 - DRF: Autenticação via JWT com djoser"
```

Atenção à barra no final do endereço. Sem ela (`.../videos/create`), o Django tenta redirecionar para a URL com barra, mas não consegue fazer isso num POST, e devolve o erro:

```
RuntimeError: You called this URL via POST, but the URL doesn't end in a slash and you have APPEND_SLASH set. Django can't redirect to the slash URL while maintaining POST data. Change your form to point to localhost:8000/api/v1/videos/create/ (note the trailing slash), or set APPEND_SLASH=False in your Django settings.
```

## Versão 2: simplificando as rotas

Repare que na v1 temos cinco rotas: duas sem `pk` (listar e criar) e três com `pk` (detalhe, editar e deletar). Dá para juntar tudo em **duas** rotas, escolhendo a ação pelo método HTTP, como faz uma API REST:

```python
# backend/core/urls.py
from django.urls import include, path

from backend.core import views as v

app_name = 'core'

v1_urlpatterns = [
    path('videos/', v.video_list, name='video_list'),
    path('videos/<int:pk>/', v.video_detail, name='video_detail'),
    path('videos/create/', v.video_create, name='video_create'),
    path('videos/<int:pk>/update/', v.video_update, name='video_update'),
    path('videos/<int:pk>/delete/', v.video_delete, name='video_delete'),
]

v2_urlpatterns = [
    path('videos/', v.videos, name='videos'),
    path('videos/<int:pk>/', v.video, name='video'),
]

urlpatterns = [
    path('api/v1/', include(v1_urlpatterns)),
    path('api/v2/', include(v2_urlpatterns)),
]
```

A view `videos` lista no GET e cria no POST:

```python
# backend/core/views.py
@csrf_exempt
def videos(request):
    videos = Video.objects.all()
    data = [video.to_dict() for video in videos]
    form = VideoForm(request.POST or None)

    if request.method == 'POST':
        if request.POST:
            # Dados obtidos pelo formulário.
            if form.is_valid():
                video = form.save()

        elif request.body:
            # Dados obtidos via json.
            data = json.loads(request.body)
            video = Video.objects.create(**data)

        else:
            return JsonResponse({'message': 'Algo deu errado.'})

        return JsonResponse({'data': video.to_dict()})

    return JsonResponse({'data': data})
```

E a view `video` mostra no GET, edita no POST e deleta no DELETE:

```python
# backend/core/views.py
@csrf_exempt
def video(request, pk):
    video = get_object_or_404(Video, pk=pk)
    form = VideoForm(request.POST or None, instance=video)

    if request.method == 'GET':
        data = video.to_dict()
        return JsonResponse({'data': data})

    if request.method == 'POST':
        if request.POST:
            # Dados obtidos pelo formulário.
            if form.is_valid():
                video = form.save()

        elif request.body:
            # Dados obtidos via json.
            data = json.loads(request.body)

            for attr, value in data.items():
                setattr(video, attr, value)
            video.save()

        else:
            return JsonResponse({'message': 'Algo deu errado.'})

        return JsonResponse({'data': video.to_dict()})

    if request.method == 'DELETE':
        video.delete()
        return JsonResponse({'data': 'Item deletado com sucesso.'})
```

O código de cada ação é o mesmo da v1; só mudou a forma de escolher a ação.

Os endpoints finais, listados com `python manage.py show_urls`:

```
/api/v1/videos/                 backend.core.views.video_list   core:video_list
/api/v1/videos/<int:pk>/        backend.core.views.video_detail core:video_detail
/api/v1/videos/<int:pk>/delete/ backend.core.views.video_delete core:video_delete
/api/v1/videos/<int:pk>/update/ backend.core.views.video_update core:video_update
/api/v1/videos/create/          backend.core.views.video_create core:video_create
/api/v2/videos/                 backend.core.views.videos       core:videos
/api/v2/videos/<int:pk>/        backend.core.views.video        core:video
```

Exemplos com o httpie na v2:

```bash
# Adiciona vídeo
http POST http://localhost:8000/api/v2/videos/ \
title="Dica #49 - DRF: Autenticação via JWT com djoser - Django REST framework" \
link="https://youtu.be/dOomllYxj9E" \
view=198

# Lista vídeos
http http://localhost:8000/api/v2/videos/

# Visualiza um vídeo
http http://localhost:8000/api/v2/videos/1/

# Edita um vídeo
http POST http://localhost:8000/api/v2/videos/1/ \
title="Dica #49 - DRF: Autenticação via JWT com djoser"

# Deleta um vídeo
http DELETE http://localhost:8000/api/v2/videos/1/
```

## Testes

Por fim, os testes da v2. O `self.client` do `TestCase` faz as requisições, e com `content_type='application/json'` o `data` é enviado como JSON no corpo:

```python
# backend/core/tests.py
import json

from django.test import TestCase

from .models import Video


class VideoTest(TestCase):

    def setUp(self):
        self.payload = {
            "title": "Dica #47 - DRF: djoser - Django REST framework",
            "link": "https://youtu.be/HUtG2Eg47Gw",
            "view": 307
        }

    def test_video_create(self):
        response = self.client.post(
            '/api/v2/videos/',
            data=self.payload,
            content_type='application/json'
        )
        resultado = json.loads(response.content)
        esperado = {
            "data": {
                "id": 1,
                **self.payload
            }
        }
        self.assertEqual(esperado, resultado)

    def test_video_list(self):
        Video.objects.create(**self.payload)

        response = self.client.get(
            '/api/v2/videos/',
            content_type='application/json'
        )
        resultado = json.loads(response.content)
        esperado = {
            "data": [
                {
                    "id": 1,
                    **self.payload
                }
            ]
        }
        self.assertEqual(esperado, resultado)

    # ... (veja o arquivo completo no GitHub)
```

Código completo: [backend/core/tests.py](https://github.com/rg3915/django-api-without-drf/blob/47efbf4c59d1a6c6f000ac18ab9187d107f65cd0/backend/core/tests.py)

No vídeo foram escritos ao vivo o `test_video_create` e o `test_video_list` (no de lista, o esperado é uma **lista** dentro de `data`, detalhe que deu erro na primeira tentativa); os demais já estavam no repositório. Para rodar:

```bash
python manage.py test
```

```
.....
----------------------------------------------------------------------
Ran 5 tests in 0.033s

OK
```

## Conclusão

Com o Django puro dá para fazer uma API REST completa: um `to_dict()` no modelo faz o papel do serializer, o `JsonResponse` devolve o JSON, o `ModelForm` valida os dados de formulário, o `json.loads(request.body)` lê os dados em JSON, e `@csrf_exempt` e `@require_http_methods` controlam o acesso. O DRF continua sendo a escolha para projetos maiores (autenticação, paginação, documentação, serializers), mas é ótimo entender o que acontece por baixo.
