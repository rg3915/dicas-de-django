# Dica 50 - DRF: Django CORS headers

**Versões usadas no vídeo:** Django 3.2.7, Django REST framework 3.12, djoser 2.1, django-cors-headers 3.8.0 e Python 3.9; no front-end, Vue CLI 4.5.13 com Vue 3, axios 0.22 e Bulma 0.9.
{: .versoes }

<a href="https://youtu.be/2SyQ9xXdMvw">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/drf-example](https://github.com/rg3915/drf-example)

[https://pt.wikipedia.org/wiki/Cross-origin_resource_sharing](https://pt.wikipedia.org/wiki/Cross-origin_resource_sharing)

[https://github.com/adamchainz/django-cors-headers](https://github.com/adamchainz/django-cors-headers)

Nesta dica vamos resolver um problema muito comum quando um front-end faz requisições para a nossa API REST: o erro de **CORS**. E, de quebra, vamos fazer a tela de login de uma aplicação em Vue.js que autentica na API feita em Django REST framework.

## O problema

Temos uma aplicação em Vue.js com uma tela de login. Com o console do navegador aberto (Inspecionar elemento > Console), ao digitar usuário e senha e clicar em **Entrar**, a tela mostra "Algo deu errado. Por favor tente novamente!" e o console mostra:

```
Access to XMLHttpRequest at 'http://127.0.0.1:8000/api/v1/auth/token/login/' from origin 'http://localhost:8080' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.

POST http://127.0.0.1:8000/api/v1/auth/token/login/ net::ERR_FAILED
```

O motivo: o Vue.js está rodando em `http://localhost:8080` e o Django em `http://localhost:8000`. Portas diferentes contam como **origens diferentes**. O [CORS](https://pt.wikipedia.org/wiki/Cross-origin_resource_sharing) (Cross-Origin Resource Sharing, ou compartilhamento de recursos com origens diferentes) é o mecanismo que permite que recursos restritos de uma página sejam pedidos por outro domínio, fora daquele ao qual o recurso pertence. Por padrão o navegador bloqueia; quem libera é o servidor, respondendo com o header `Access-Control-Allow-Origin`. No Django, quem faz isso é o [django-cors-headers](https://github.com/adamchainz/django-cors-headers).

## Pré-requisitos

* O projeto `drf-example` das dicas anteriores, com o djoser e o login por token em `api/v1/auth/token/login/` ([Dica 47](047-djoser.md)).
* Node.js e npm instalados, para o front-end.

## Instalando o django-cors-headers

Com a virtualenv ativa, na pasta do projeto:

```bash
source .venv/bin/activate
python -m pip install django-cors-headers
pip freeze | grep cors >> requirements.txt
```

O `requirements.txt` fica assim:

```
click==8.0.*
django-extensions
Django==3.2.*
djangorestframework==3.12.*
djoser==2.1.*
dr-scaffold==1.4.*
drf-yasg==1.20.*
python-decouple
djangorestframework-simplejwt==4.8.0
django-cors-headers==3.8.0
```

## Configurando o settings.py

Edite `backend/settings.py`. Três coisas:

1. `CORS_ALLOWED_ORIGINS`: a lista de origens que podem fazer requisições para a API. Aqui, `http://localhost:8080`, onde roda o front-end.
2. `corsheaders` no `INSTALLED_APPS`.
3. O `CorsMiddleware` no `MIDDLEWARE`, logo **acima** do `CommonMiddleware`. A documentação pede que ele fique o mais alto possível, e antes de qualquer middleware que gere respostas, como o `CommonMiddleware`.

```python
# backend/settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8080',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd apps
    'rest_framework',
    'rest_framework.authtoken',
    'django_extensions',
    'dr_scaffold',
    'drf_yasg',
    'djoser',
    'corsheaders',
    # my apps
    'accounts',
    'blog',
    'product',
    'ecommerce',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # corsheaders
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

Só isso. Rode o servidor:

```bash
python manage.py runserver
```

Se o usuário ainda não tiver token:

```bash
# Se necessário
python manage.py drf_create_token huguinho
```

## Frontend

Agora a segunda parte: o front-end em Vue.js que faz o login de verdade.

### Criando o projeto Vue

Instale o Vue CLI e crie o projeto `frontend`, na pasta do projeto Django:

```bash
npm install -g @vue/cli
vue create frontend
```

Escolha **Manually select features** e marque (com a barra de espaço):

* Choose Vue version
* Babel
* Router
* Vuex
* CSS Pre-processors

e **tire** o Linter / Formatter. Depois:

* Vue.js: **3.x**
* Use history mode for router? **Yes**
* CSS pre-processor: **Sass/SCSS (with node-sass)**
* Where do you prefer placing config for Babel, ESLint, etc.? **In dedicated config files**
* Save this as a preset for future projects? **N**

Entre na pasta e instale o axios (para as requisições), o Bulma (o CSS) e o bulma-toast:

```bash
cd frontend
npm install axios bulma bulma-toast
npm audit fix
```

O `npm audit fix` corrige as vulnerabilidades que o npm aponta no fim da instalação.

O `package.json` fica com estas dependências:

```json
"dependencies": {
  "axios": "^0.22.0",
  "bulma": "^0.9.3",
  "bulma-toast": "^2.4.1",
  "core-js": "^3.6.5",
  "vue": "^3.0.0",
  "vue-router": "^4.0.0-0",
  "vuex": "^4.0.0-0"
},
"devDependencies": {
  "@vue/cli-plugin-babel": "~4.5.0",
  "@vue/cli-plugin-router": "~4.5.0",
  "@vue/cli-plugin-vuex": "~4.5.0",
  "@vue/cli-service": "~4.5.0",
  "@vue/compiler-sfc": "^3.0.0",
  "node-sass": "^4.12.0",
  "sass-loader": "^8.0.2"
}
```

### main.js

Importe o axios e defina a URL base da API, assim nas requisições basta passar o caminho (`/api/v1/...`):

```js
// frontend/src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

axios.defaults.baseURL = 'http://127.0.0.1:8000'

createApp(App).use(store).use(router, axios).mount('#app')
```

### App.vue

Troque o link de **About** por **Login** e importe o Bulma no começo do `<style>`:

```html
<!-- frontend/src/App.vue -->
<template>
  <div id="nav">
    <router-link to="/">Home</router-link> |
    <router-link to="/login">Login</router-link>
  </div>
  <router-view/>
</template>

<style lang="scss">
@import '../node_modules/bulma';
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;

  a {
    font-weight: bold;
    color: #2c3e50;

    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
</style>
```

### router/index.js

Importe a view `Login` e acrescente a rota `/login`:

```js
// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
```

### views/Login.vue

Crie o arquivo:

```bash
touch src/views/Login.vue
```

```html
<!-- frontend/src/views/Login.vue -->
<template>
  <div class="container">
    <div class="columns">
      <div class="column is-4 is-offset-4">
        <h1 class="title">Login</h1>

        <form @submit.prevent="submitForm">

          <div class="field">
            <label>Usuário</label>
            <div class="control">
              <input type="text" name="username" class="input" v-model="username" autofocus>
            </div>
          </div>

          <div class="field">
            <label>Senha</label>
            <div class="control">
              <input type="password" name="password" class="input" v-model="password">
            </div>
          </div>

          <div class="notification is-danger" v-if="errors.length">
            <p v-for="error in errors" :key="error">{{ error }}</p>
          </div>

          <div class="field">
            <div class="control">
              <button class="button is-success">Entrar</button>
            </div>
          </div>

        </form>

      </div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'

  export default {
    name: 'Login',
    data() {
      return {
        username: '',
        password: '',
        errors: []
      }
    },
    methods: {
      async submitForm() {
        axios.defaults.headers.common['Authorization'] = ''
        localStorage.removeItem('token')
        const formData = {
          username: this.username,
          password: this.password
        }
        await axios
          .post('/api/v1/auth/token/login/', formData)
          .then(response => {
            const token = response.data.auth_token
            axios.defaults.headers.common['Authorization'] = 'Token ' + token
            localStorage.setItem('token', token)
          })
          .catch(error => {
            if (error.response) {
              for (const property in error.response.data) {
                this.errors.push(`${property}: ${error.response.data[property]}`)
              }
            } else if (error.message) {
              this.errors.push('Algo deu errado. Por favor tente novamente!')
            }
          })
      }
    }
  }
</script>
```

Como funciona:

* O template usa as classes do Bulma (`container`, `columns`, `field`, `control`, `input`, `button`, `notification`).
* `@submit.prevent="submitForm"` impede o envio normal do formulário e chama o método `submitForm`.
* `v-model` liga os campos `username` e `password` ao `data()` do componente.
* O bloco `notification is-danger` só aparece (`v-if`) se houver erros, e o `v-for` mostra um parágrafo por erro.
* No `submitForm`: limpa o header `Authorization` e o token guardado no `localStorage`, monta o `formData` e faz o POST em `/api/v1/auth/token/login/`. Se der certo, pega o `auth_token` da resposta, coloca no header padrão do axios (`Authorization: Token <token>`) e guarda no `localStorage`. Se der errado, mostra os erros que a API devolveu ou, se não houve resposta (como no caso do bloqueio de CORS), a mensagem genérica.

## Testando

Com o Django rodando em um terminal (`python manage.py runserver`), rode o front-end em outro:

```bash
npm run serve
```

Abra `http://localhost:8080/login`, deixe aberta a aba **Network** do navegador com o filtro **Fetch/XHR**, digite o usuário e a senha e clique em **Entrar**. Agora a requisição `login/` passa, e a resposta traz o token:

```json
{
    "auth_token": "8bd341833c8e43bebce157475467d4af513b3ffc"
}
```

Problema de CORS resolvido: a API passou a responder com o header `Access-Control-Allow-Origin: http://localhost:8080`, e o navegador libera a requisição. Uma origem que não está em `CORS_ALLOWED_ORIGINS` (por exemplo `http://localhost:3000`) continua bloqueada.
