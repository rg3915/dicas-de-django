# Django + InertiaJS (Vue) - palestra

Publicado em 09/09/2026.

**Testado com:** Django 6.1, Inertia v3, Vue 3 e Python 3.14.
{: .versoes }

<a href="https://youtu.be/b3GmwJQWLrs">
    <img src="../.gitbook/assets/youtube.png">
</a>

Palestra apresentada no DevConverge LATAM em 05/09/2026: Django e VueJS com InertiaJS.

Projeto da palestra: [https://github.com/rg3915/django-inertia-vuejs](https://github.com/rg3915/django-inertia-vuejs)

Slides: [https://slides.com/regissantos/inertiajs](https://slides.com/regissantos/inertiajs)

Neste tutorial vamos montar o CRUD de filmes da palestra: Django no back-end, Vue 3 no front-end e o Inertia.js fazendo a ponte entre os dois. O resultado é uma SPA de verdade, sem API REST, sem Vue Router, sem Pinia e sem CORS.

## O problema que o Inertia resolve

Na arquitetura separada, uma tela de filmes tem duas rotas: `api/filmes/` no Django e `/filmes` no Vue Router, que consome a primeira. Isso traz junto:

* uma API REST (DRF ou Django Ninja) com serializers;
* autenticação duplicada (sessão no Django, JWT no front);
* configuração de CORS;
* dois sistemas de rotas, dois projetos, dois deploys.

Se a API tem outros consumidores (um app mobile, terceiros), esse custo se paga. Mas num monolito você está criando uma API só para o seu próprio front consumir.

O Inertia se coloca no meio, como um tradutor, e se apresenta como "o monolito moderno":

1. **Primeira visita**: o Django devolve uma página HTML completa com os dados da página embutidos em JSON. Carrega rápido.
2. **Navegações seguintes**: o Inertia intercepta o clique e faz a requisição com o cabeçalho `X-Inertia`. O Django devolve só um JSON com o nome do componente e as props, e o Vue troca apenas o que mudou.
3. **Formulários**: o Django processa, salva e faz `redirect`, como sempre. O Inertia segue o redirect e busca a próxima página sozinho.

As rotas ficam só no Django. A autenticação é só a do Django, sem token no navegador.

## Pré-requisitos

* Python 3.14 (o projeto usa Django 6.1 e `inertia-django` 2.0, protocolo Inertia v3).
* Node.js 20 ou mais recente.
* Docker e Docker Compose (para o PostgreSQL).

## 1. Projeto Django

```bash
mkdir django-inertia-vuejs
cd django-inertia-vuejs
python -m venv .venv
source .venv/bin/activate
pip install django django-extensions django-vite inertia-django "psycopg[binary]" python-decouple
django-admin startproject apps .
cd apps
python ../manage.py startapp core
cd ..
```

O repositório usa o `uv`, com essas mesmas dependências no `pyproject.toml`; nele, basta `uv sync`. O **django-vite** liga o Django ao servidor de desenvolvimento do Vite.

Em `apps/core/apps.py`, ajuste `name = 'apps.core'`.

## 2. Banco de dados

```bash
# .env
SECRET_KEY=mude-me

POSTGRES_DB=movies_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5431

PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin
```

Gere uma chave para o `SECRET_KEY` com:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:18.6-alpine
    restart: unless-stopped
    env_file: .env
    ports:
      - "5431:5432"
    volumes:
      # Postgres 18+ espera um único mount em /var/lib/postgresql.
      - pgdata:/var/lib/postgresql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  pgdata:
```

No repositório o compose também sobe o pgAdmin na porta 5050. Repare no comentário do volume: a partir do Postgres 18, montar em `/var/lib/postgresql/data`, como se fazia até o 17, faz o container entrar em loop de reinício.

```bash
docker compose up -d
```

## 3. Settings

Os trechos do `apps/settings.py` que importam:

```python
# apps/settings.py
# ... (veja o arquivo completo no GitHub)
INSTALLED_APPS = [
    # ...
    'django_extensions',
    'django_vite',
    'inertia',
    'apps.core',
]

MIDDLEWARE = [
    # ...
    'inertia.middleware.InertiaMiddleware',  # adicionar após SessionMiddleware
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.joinpath('templates')],  # pasta do base.html
        'APP_DIRS': True,
        # OPTIONS igual ao gerado pelo startproject
    },
]

# ...
# Inertia
INERTIA_LAYOUT = 'base.html'

# Django Vite
DJANGO_VITE = {
    'default': {
        'dev_mode': True,
        'dev_server_host': 'localhost',
        'dev_server_port': 5173,
        'manifest_path': BASE_DIR.joinpath(
            'frontend', 'dist', '.vite', 'manifest.json'
        ),
    }
}
# ... (veja o arquivo completo no GitHub)
```

Código completo: [apps/settings.py](https://github.com/rg3915/django-inertia-vuejs/blob/4133ad4d607535b49e1e0d598aa6ab432c9b91bc/apps/settings.py)

* `'inertia'` e o `InertiaMiddleware` são a instalação do Inertia. O middleware olha o cabeçalho `X-Inertia` e decide se devolve HTML ou JSON.
* `INERTIA_LAYOUT` é obrigatório e não tem valor padrão: é o template que envolve todas as páginas. Isso mostra o tamanho do Inertia: ele substitui o sistema de templates, e só. Rotas, sessão e ORM continuam com o Django.
* `DJANGO_VITE` em `dev_mode` carrega os arquivos do servidor do Vite na porta 5173. Em produção, `dev_mode` vira `False` e o Django lê o `manifest.json` gerado pelo `npm run build`.
* O CSRF fica com os padrões do Django (`csrftoken` e `X-CSRFToken`); quem se adapta é o cliente, no `main.js`.

## 4. Layout base

```html
<!-- templates/base.html -->
{% load django_vite %}
<!DOCTYPE html>
<html lang="pt-br" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movies</title>
    <script>
        try {
            var saved = localStorage.getItem("theme")
            if (saved === "dark" || saved === "light") {
                document.documentElement.dataset.theme = saved
            }
        } catch (e) {}
    </script>
    {% vite_hmr_client %}
    {% vite_asset 'src/main.js' %}
</head>
<body>
    {% block inertia %}{% endblock %}
</body>
</html>
```

O `inertia-django` preenche o `{% block inertia %}` com a `<div id="app">` e um `<script type="application/json">` com os dados da página. `vite_hmr_client` e `vite_asset` vêm do django-vite. O script inline aplica o tema salvo antes da primeira pintura, para a página não piscar.

## 5. Model e form

```python
# apps/core/models.py
from django.core.validators import MaxValueValidator
from django.db import models


class Movie(models.Model):
    class Status(models.TextChoices):
        WANT = 'want', 'Quero Ver'
        WATCHING = 'watching', 'Assistindo'
        WATCHED = 'watched', 'Assistido'

    title = models.CharField(max_length=200)
    director = models.CharField(max_length=200, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(5)]
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.WANT
    )
    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Filme'
        verbose_name_plural = 'Filmes'

    def __str__(self):
        return self.title

    @property
    def status_label(self):
        """'watched' -> 'Assistido'. O rótulo legível vai pronto pro Vue."""
        return self.get_status_display()

    @property
    def stars(self):
        """3 -> '★★★☆☆'. Renderizar isso no servidor evita lógica no template."""
        filled = min(self.rating or 0, 5)
        return '★' * filled + '☆' * (5 - filled)

    def serializable_values(self, exclude=[]):
        tree = {}
        for field in self._meta.fields:
            if field.name in exclude:
                continue
            tree[field.name] = self.serializable_value(field.name)

        # Campos derivados: não existem no banco, mas o componente Vue os recebe
        # como props junto com o resto — sem serializer, sem endpoint extra.
        tree['status_label'] = self.status_label
        tree['stars'] = self.stars
        return tree
```

O `serializable_values` é a dica da palestra para não precisar de serializer: ele percorre `_meta.fields` e monta o dicionário sozinho. Se você renomear um campo do model, não tem um dicionário escrito à mão para lembrar de atualizar.

```python
# apps/core/forms.py
from django import forms

from .models import Movie


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ('title', 'director', 'year', 'genre', 'rating', 'status', 'notes')
```

Rode as migrações:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 6. Views com props

```python
# apps/core/views.py
import json

from django.http import QueryDict
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from inertia import render

from .forms import MovieForm
from .models import Movie


def _get_post_data(request):
    """O Inertia envia JSON, mas o Django ModelForm espera QueryDict."""
    if request.content_type == 'application/json':
        return QueryDict(mutable=True) | json.loads(request.body)
    return request.POST


# ... (_index_props: veja o arquivo completo no GitHub)


def movie_list(request):
    return render(request, 'Movies/Index', props=_index_props())


def movie_create(request):
    data = _get_post_data(request)
    form = MovieForm(data)

    if form.is_valid():
        form.save()
        messages.success(request, 'Filme criado com sucesso!')
        return redirect('movie_list')

    props = _index_props()
    props['errors'] = form.errors
    props['showDialog'] = 'create'
    props['formData'] = dict(data)
    return render(request, 'Movies/Index', props=props)


# ... (movie_update e movie_delete: veja o arquivo completo no GitHub)
```

Código completo: [apps/core/views.py](https://github.com/rg3915/django-inertia-vuejs/blob/4133ad4d607535b49e1e0d598aa6ab432c9b91bc/apps/core/views.py)

* O `render` agora vem de `inertia`, não de `django.shortcuts`. O segundo argumento, `'Movies/Index'`, é o nome do componente Vue; `props` é um dicionário que chega ao componente como props.
* O Inertia envia os formulários como JSON. Como o `ModelForm` espera um `QueryDict`, o `_get_post_data` faz a conversão.
* Formulário válido: salva, registra uma mensagem e faz `redirect`, como em qualquer view Django.
* Formulário inválido: renderiza a mesma página com `errors`, `showDialog` e `formData`, para o Vue reabrir o diálogo com os erros e o que o usuário digitou.
* As mensagens do `django.contrib.messages` chegam ao front automaticamente em `page.flash.messages` (Inertia v3).

## 7. URLs

```python
# apps/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
]
```

```python
# apps/core/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('create/', views.movie_create, name='movie_create'),
    path('<int:pk>/update/', views.movie_update, name='movie_update'),
    path('<int:pk>/delete/', views.movie_delete, name='movie_delete'),
]
```

É Django puro, nada mudou. E como não há API, também não há documentação de API para manter: `python manage.py show_urls` (django-extensions) lista todas as rotas, as views e os nomes.

## 8. Front-end: Vite e Vue

```bash
mkdir -p frontend/src/Pages/Movies frontend/src/Components frontend/src/composables
cd frontend
npm init -y
npm install vue @inertiajs/vue3 @vitejs/plugin-vue @picocss/pico
npm install -D vite
cd ..
```

```json
// frontend/package.json
{
  "name": "frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@inertiajs/vue3": "^3.7.0",
    "@picocss/pico": "^2.1.1",
    "@vitejs/plugin-vue": "^6.0.8",
    "vue": "^3.5.41"
  },
  "devDependencies": {
    "vite": "^8.2.2"
  }
}
```

```js
// frontend/vite.config.js
import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"

export default defineConfig({
    plugins: [vue()],
    root: ".",
    base: "/static/",
    build: {
        outDir: "dist",
        manifest: true,
        rollupOptions: {
            input: "src/main.js",
        },
    },
    server: {
        origin: "http://localhost:5173",
    },
})
```

O `base: "/static/"` casa com o `STATIC_URL` do Django, e o `manifest: true` gera o arquivo que o django-vite lê em produção.

```js
// frontend/src/main.js
import "@picocss/pico"
import { createApp, h } from "vue"
import { createInertiaApp } from "@inertiajs/vue3"

createInertiaApp({
    resolve: (name) => {
        const pages = import.meta.glob("./Pages/**/*.vue", { eager: true })
        return pages[`./Pages/${name}.vue`]
    },

    // A partir do Inertia v3 o axios foi trocado por um cliente XHR próprio,
    // que por padrão usa os nomes de CSRF do Laravel (XSRF-TOKEN / X-XSRF-TOKEN).
    // Aqui ensinamos o cliente a falar a língua do Django.
    http: {
        xsrfCookieName: "csrftoken",
        xsrfHeaderName: "X-CSRFToken",
    },

    setup({ el, App, props, plugin }) {
        createApp({ render: () => h(App, props) })
            .use(plugin)
            .mount(el)
    },
})
```

O `resolve` transforma o nome que a view passou (`'Movies/Index'`) no arquivo `./Pages/Movies/Index.vue`. O bloco `http` é a única configuração específica do Django: sem ele, os `POST` seriam recusados pelo `CsrfViewMiddleware`.

## 9. O componente da página

```vue
<!-- frontend/src/Pages/Movies/Index.vue -->
<script setup>
import { ref, onMounted } from "vue"
import { router, useForm } from "@inertiajs/vue3"
// ... (imports dos componentes)
// Quem passa esses dados é o Django:
//   render(request, "Movies/Index", props={"movies": data, "stats": {...}})
const props = defineProps([
    "movies", "stats",
    "errors", "showDialog", "editMovie", "formData",
])
// ...

// useForm: estado reativo do formulário + métodos post, put etc.
const createForm = useForm({
    title: "",
    // ...
})

// POST direto numa rota do Django. Não existe Vue Router.
function submitCreate() {
    createForm.post("/create/", {
        onSuccess: () => {
            createForm.reset()
            showCreateDialog.value = false
        },
    })
}

// ... (edição, exclusão e reabertura do diálogo com erros: veja o arquivo completo no GitHub)
</script>

<template>
    <!-- ... -->
        <MovieFormDialog
            v-model:open="showCreateDialog"
            :form="createForm"
            :errors="showCreateDialog ? errors : {}"
            title="Novo Filme"
            @submit="submitCreate"
        />
    <!-- ... -->
</template>
<!-- ... -->
```

Código completo: [frontend/src/Pages/Movies/Index.vue](https://github.com/rg3915/django-inertia-vuejs/blob/4133ad4d607535b49e1e0d598aa6ab432c9b91bc/frontend/src/Pages/Movies/Index.vue)

Fluxo do formulário: `createForm.post("/create/")` envia JSON para a view `movie_create`. Se ela responde com `redirect` (sucesso), o Inertia busca a lista atualizada e troca as props sem recarregar a página. Se ela responde renderizando a página com `errors`, o diálogo continua aberto mostrando os erros. O `form.processing` fica `true` enquanto a requisição está em andamento.

## 10. A tabela com busca reativa

```vue
<!-- frontend/src/Components/MovieTable.vue -->
<script setup>
import { computed, ref } from "vue"

const props = defineProps(["movies"])
defineEmits(["edit", "delete"])

// Os filmes já chegaram como props do Django: filtrar é só uma computed
// sobre um array em memória. Nenhum fetch, nenhum endpoint, nenhum loading.
const search = ref("")

const filteredMovies = computed(() => {
    const term = search.value.trim().toLowerCase()

    if (!term) return props.movies

    return props.movies.filter((movie) =>
        [movie.title, movie.director, movie.genre]
            .filter(Boolean)
            .some((field) => field.toLowerCase().includes(term))
    )
})
</script>

<template>
    <!-- ... -->
        <div role="search">
            <input
                v-model="search"
                type="search"
                placeholder="Buscar por título, diretor ou gênero…"
                aria-label="Buscar filmes"
            >
        </div>
    <!-- ... -->
                <tr v-for="movie in filteredMovies" :key="movie.id">
                    <td>{{ movie.title }}</td>
                    <td>{{ movie.director }}</td>
                    <td>{{ movie.year }}</td>
                    <td class="stars">{{ movie.stars }}</td>
                    <td>{{ movie.status_label }}</td>
                    <!-- ... (veja o arquivo completo no GitHub) -->
</template>
```

Código completo: [frontend/src/Components/MovieTable.vue](https://github.com/rg3915/django-inertia-vuejs/blob/4133ad4d607535b49e1e0d598aa6ab432c9b91bc/frontend/src/Components/MovieTable.vue)

`stars` e `status_label` vêm prontos do model. No repositório o componente tem ainda um bloco `<style scoped>` para alinhar a barra de busca.

## 11. Diálogo do formulário e barra de estatísticas

```vue
<!-- frontend/src/Components/MovieFormDialog.vue -->
<script setup>
import { ref, watch } from "vue"
import { useModal } from "../composables/useModal"

const props = defineProps(["form", "errors", "title", "open"])
const emit = defineEmits(["update:open", "submit"])
// ... (abre e fecha o <dialog> conforme o v-model:open)
</script>

<template>
    <dialog ref="dialogRef" @close="handleClose">
        <article>
            <header>
                <button aria-label="Close" rel="prev" @click="handleClose"></button>
                <h3>{{ title }}</h3>
            </header>
            <form @submit.prevent="$emit('submit')">
                <label>
                    Título
                    <input v-model="form.title" :aria-invalid="!!errors?.title" />
                    <small v-if="errors?.title" style="color: red">{{ errors.title[0] }}</small>
                </label>
                <!-- ... (os outros campos seguem o mesmo padrão) -->
                <footer>
                    <div class="grid">
                        <button type="button" class="outline secondary" @click="handleClose">Cancelar</button>
                        <button type="submit" :disabled="form.processing" :aria-busy="form.processing">Salvar</button>
                    </div>
                </footer>
            </form>
        </article>
    </dialog>
</template>
```

Código completo: [frontend/src/Components/MovieFormDialog.vue](https://github.com/rg3915/django-inertia-vuejs/blob/4133ad4d607535b49e1e0d598aa6ab432c9b91bc/frontend/src/Components/MovieFormDialog.vue)

Os `errors` são o `form.errors` do Django, no formato `{"title": ["Este campo é obrigatório."]}`.

```vue
<!-- frontend/src/Components/StatsBar.vue -->
<script setup>
defineProps(["stats"])
</script>

<template>
    <hgroup>
        <h1>Filmes</h1>
        <p>
            Total: {{ stats.total }} |
            Quero ver: {{ stats.want }} |
            Assistindo: {{ stats.watching }} |
            Assistidos: {{ stats.watched }}
        </p>
    </hgroup>
</template>
```

## 12. Modal, confirmação, mensagens e tema

O `Index.vue` usa mais quatro peças de apoio, que não têm nada de específico do Django ou do Inertia. Copie-as do repositório:

* `frontend/src/composables/useModal.js`: abre e fecha o `<dialog>` com `showModal()`/`close()` e aplica no `<html>` as classes `modal-is-open`, `modal-is-opening` e `modal-is-closing`, que o Pico CSS usa nas animações.
* `frontend/src/Components/ConfirmDialog.vue`: o mesmo padrão do `MovieFormDialog` (prop `open` com `v-model`), com os botões Cancelar e Confirmar, que emite `confirm`.
* `frontend/src/Components/ThemeSwitch.vue`: um switch que grava `data-theme` no `<html>` e no `localStorage`.
* `frontend/src/Components/Toast.vue`: mostra as mensagens do Django. Esta tem um detalhe do Inertia v3 que vale ver:

```js
// frontend/src/Components/Toast.vue (trecho do <script setup>)
import { ref, watch } from "vue"
import { usePage } from "@inertiajs/vue3"

// Cada item vem no formato { level, message }, com as tags do Django.
const page = usePage()

const visible = ref([])

watch(() => page.flash?.messages, (msgs) => {
    if (!msgs || !msgs.length) return

    msgs.forEach((msg, i) => {
        const item = { ...msg, id: Date.now() + i }
        visible.value.push(item)

        setTimeout(() => {
            visible.value = visible.value.filter(v => v.id !== item.id)
        }, 4000)
    })
}, { immediate: true })
```

O `messages.success(...)` da view chega em `page.flash.messages`, fora das props e sem middleware customizado. O template percorre `visible` com `v-for` e aplica a classe do nível (`success`, `error`, `warning`, `info`).

## 13. Rodando

Popule o banco com os filmes da demonstração e crie um superusuário. O `seed_movies` é um comando do próprio projeto (copie `apps/core/management/commands/seed_movies.py` do repositório); ele é idempotente e aceita `--clear` para apagar tudo antes:

```bash
python manage.py seed_movies
python manage.py createsuperuser
```

São dois terminais:

```bash
# Terminal 1 - Django
python manage.py runserver
```

```bash
# Terminal 2 - Vite
cd frontend
npm install
npm run dev
```

Acesse `http://localhost:8000` e teste:

1. Digite `tarantino` na busca: a lista filtra na hora, sem nenhuma requisição ao servidor.
2. Clique em **Novo filme**, deixe o título vazio e salve: o erro de validação do Django aparece no diálogo.
3. Edite um filme e salve: a lista atualiza e aparece o toast, sem recarregar a página.
4. Abra a aba Rede do navegador: a primeira carga é HTML; as seguintes são JSON com o cabeçalho `X-Inertia`.

Para produção, `npm run build` gera `frontend/dist/` com o manifest, e `dev_mode` passa a `False`.

## Quando não usar Inertia

* Com **FastAPI**: o foco dele é API, e o Inertia pressupõe um framework que renderiza o layout.
* Quando a API tem **outros consumidores**, como um app mobile ou terceiros. Aí a API REST se justifica.

A pergunta é: quem vai consumir isso além do meu próprio front-end? Se a resposta é ninguém, o Inertia entrega uma interface moderna sem abrir mão do monolito. Ele também tem adaptadores para Rails, Laravel e Phoenix no back-end, e para Vue, React e Svelte no front-end.

Referências:

* inertia-django: [https://github.com/inertiajs/inertia-django](https://github.com/inertiajs/inertia-django)
* Inertia.js: [https://inertiajs.com/](https://inertiajs.com/)
* django-vite: [https://github.com/MrBin99/django-vite](https://github.com/MrBin99/django-vite)
