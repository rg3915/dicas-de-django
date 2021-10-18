# 50 - DRF: Django CORS headers

<a href="https://youtu.be/2SyQ9xXdMvw">
    <img src="../.gitbook/assets/youtube.png">
</a>

https://pt.wikipedia.org/wiki/Cross-origin_resource_sharing

https://github.com/adamchainz/django-cors-headers


```
python -m pip install django-cors-headers
pip freeze | grep django-cors-headers >> requirements.txt
```


Edite `settings.py`

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8080',
]

INSTALLED_APPS = [
    ...,
    'corsheaders',
    ...,
]

MIDDLEWARE = [
    ...,
    # corsheaders
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...,
]

```

```
# Se necessário
python manage.py drf_create_token huguinho
```

### Frontend

```
npm install -g @vue/cli
vue create frontend

# adicione Router, Vuex e sass-loader (CSS Pre-processors) na instalação
Tire o Linter / Formatter
Marque também Sass/SCSS (with node-sass)

cd frontend
npm install axios bulma bulma-toast
npm audit fix
```

```js
// main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

axios.defaults.baseURL = 'http://127.0.0.1:8000'

createApp(App).use(store).use(router, axios).mount('#app')
```


```js
// App.vue
// ...
<router-link to="/login">Login</router-link>
// ...
<style lang="scss">
@import '../node_modules/bulma';
// ...
</style>
```


Edite router/index.js

```
import Login from '../views/Login.vue'

{
  path: '/login',
  name: 'Login',
  component: Login
}
```

touch src/views/Login.vue

```js
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
            <p v-for="error in errors" v-bind:key="error">{{ error }}</p>
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
