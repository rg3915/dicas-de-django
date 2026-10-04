# Dica 16 - Logout

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10 e Tailwind CSS 3.2.4 (CSS compilado do template Windster).
{: .versoes }

<a href="https://youtu.be/SPnFqVRAows">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`), por causa do GitBook. Aqui elas já estão escritas do jeito certo, sem a barra.

![](../.gitbook/assets/tags.png)

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django) (branch `aula16`)

Na [Dica 15 - Login com e-mail no Django](075-15-login-com-email.md) fizemos o login com a `LoginView`. Fazer o **logout** é ainda mais simples: o Django já tem a `LogoutView`, basta criar a rota e colocar o link **Sair** no dashboard. Aproveitamos para mostrar o nome do usuário logado na barra superior.

```bash
git checkout -b aula16
```

## A rota de logout

No `accounts/urls.py`, importe a `LogoutView` junto com a `LoginView` e acrescente a rota `logout/`:

```python
# backend/accounts/urls.py
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  # noqa E501
    path('logout/', LogoutView.as_view(), name='logout'),  # noqa E501
]
```

A `LogoutView` encerra a sessão e redireciona para o `LOGOUT_REDIRECT_URL`, que configuramos na Dica 15 como `'core:index'` (a página inicial).

## Nome do usuário e link Sair na barra superior

No `includes/nav.html` (a barra superior do dashboard, da [Dica 13](073-13-dashboard.md)), dentro do `div` com `class="hidden lg:flex items-center"`, acrescente duas linhas: o `Olá` com o primeiro nome do usuário, antes do "Open source", e o link **Sair**, depois do botão do GitHub. O trecho fica assim:

```html
<!-- backend/core/templates/includes/nav.html -->
<div class="hidden lg:flex items-center">
  <span class="text-base font-normal text-gray-500 mr-5">Olá {{ request.user.first_name }}</span>
  <span class="text-base font-normal text-gray-500 mr-5">Open source ❤️</span>
  <div class="-mb-1">
    <a class="github-button" href="https://github.com/themesberg/windster-tailwind-css-dashboard" data-color-scheme="no-preference: dark; light: light; dark: light;" data-icon="octicon-star" data-size="large" data-show-count="true" aria-label="Star themesberg/windster-tailwind-css-dashboard on GitHub">Star</a>
  </div>
  <a href="{% url 'logout' %}" class="text-base font-normal text-gray-500 ml-5">Sair</a>
</div>
```

* `request.user` está disponível no template por causa do context processor `django.template.context_processors.request`, que já vem no `settings.py` padrão. `first_name` é o campo do nosso `User` customizado da [Dica 14](074-14-django-custom-user-email.md). Se o usuário não tiver primeiro nome cadastrado, aparece só "Olá".
* `{% url 'logout' %}` aponta para `/accounts/logout/`.

## Testando

```bash
python manage.py runserver
```

1. Entre no dashboard com o seu usuário. A barra superior mostra "Olá" com o seu primeiro nome (no vídeo, "Olá Admin").
2. Clique em **Sair**: a sessão é encerrada e você vai para a página inicial.
3. Tente acessar [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/) de novo: como você não está mais logado, o `@login_required` manda para a tela de login.

Observação: no Django 4.1, usado no vídeo, a `LogoutView` ainda aceitava GET, por isso um link simples funciona. O logout por GET ficou obsoleto no Django 4.1 e foi removido no Django 5.0; nas versões novas, o **Sair** precisa ser um formulário com `method="post"` e `{% csrf_token %}`.
