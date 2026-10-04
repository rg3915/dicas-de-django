# Dica 12 - Fale conosco com formulário para enviar mensagem

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, Tailwind CSS (via CDN) e MailHog.
{: .versoes }

<a href="https://youtu.be/XXSAalrmtxI">
    <img src="../.gitbook/assets/youtube.png">
</a>

**Importante:** nas versões antigas desta página as tags de template apareciam com uma `\` no meio (`{\%`), por causa do GitBook. Aqui elas já estão escritas do jeito certo, sem a barra.

![](../.gitbook/assets/tags.png)

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django) (branch `aula12`)

Sabe quando você entra num site e tem um formulário de **Fale Conosco**? Vamos fazer isso no nosso site: o visitante preenche nome, e-mail, título e mensagem, e o Django envia essa mensagem por e-mail. Para não precisar de um servidor de e-mail de verdade, os e-mails vão para o **MailHog**, que captura tudo e mostra numa interface web.

Esta dica faz parte do *Projeto Dicas de Django*: ela continua o projeto da [Dica 11 - Criando Landpage de produtos](071-11-landpage.md), em que a página inicial (`index.html`) já tem o formulário **Fale Conosco** desenhado com Tailwind CSS, mas ainda sem fazer nada.

## Pré-requisitos

* O projeto das dicas anteriores, com a estrutura `backend/` (o projeto Django chama `backend` e as apps ficam dentro dele, como `backend.core`). Veja a [Dica 6 - Criando o projeto Django](066-06-projeto-django.md).
* O MailHog rodando com o `docker-compose` da [Dica 7 - PostgreSQL, pgAdmin e MailHog com docker-compose](067-07-docker-compose.md): SMTP na porta `1025` e interface web na porta `8025`.
* As configurações de e-mail no `settings.py`, também da Dica 7:

```python
# backend/settings.py
# Email config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
EMAIL_HOST = config('EMAIL_HOST', 'localhost')
EMAIL_PORT = config('EMAIL_PORT', 1025, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
```

No vídeo, o Regis começa criando a branch da aula, como nas dicas anteriores:

```bash
git checkout -b aula12
```

## Criando a app crm

As mensagens de contato ficam numa app nova, `crm`. Como as apps ficam dentro da pasta `backend`, entramos nela para rodar o `startapp` (chamando o `manage.py` da pasta de cima) e depois voltamos:

```bash
cd backend
python ../manage.py startapp crm
cd ..

touch backend/crm/forms.py
touch backend/crm/urls.py
```

Como a app está dentro de `backend`, o `name` dela no `apps.py` precisa do caminho completo:

```python
# backend/crm/apps.py
from django.apps import AppConfig


class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.crm'
```

E registramos a app no `INSTALLED_APPS`:

```python
# backend/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # apps de terceiros
    'django_extensions',
    # minhas apps
    'backend.core',
    'backend.crm',
]
```

## URLs

No `urls.py` principal, incluímos as URLs da app `crm` com o prefixo `crm/` e o namespace `crm`:

```python
# backend/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('backend.core.urls', namespace='core')),  # noqa E501
    path('crm/', include('backend.crm.urls', namespace='crm')),  # noqa E501
    path('admin/', admin.site.urls),  # noqa E501
]
```

O `crm/urls.py` foi copiado do `core/urls.py` e adaptado. Ele tem uma única rota, `contact/`, que recebe o formulário:

```python
# backend/crm/urls.py
from django.urls import path

from backend.crm import views as v

app_name = 'crm'


urlpatterns = [
    path('contact/', v.send_contact, name='send_contact'),  # noqa E501
]
```

Com isso, a URL completa fica `/crm/contact/`, e no template ela é referenciada como `crm:send_contact`.

## O formulário

O formulário é um `forms.Form` simples (não está ligado a nenhum model), com os quatro campos do Fale Conosco. Os comentários lembram o papel de cada campo no e-mail: o e-mail do visitante é o remetente (*sender*), o título é o assunto (*subject*) e o corpo é a mensagem (*message*).

```python
# backend/crm/forms.py
from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=255)
    email = forms.EmailField()  # sender
    title = forms.CharField(max_length=100)  # subject
    body = forms.CharField(widget=forms.Textarea)  # message
```

No vídeo, o formulário foi escrito primeiro com o rótulo como primeiro argumento, `forms.CharField('nome', max_length=255)`, como se faz nos campos de model. Nos campos de **formulário** isso não funciona: o `runserver` quebra com

```
TypeError: CharField.__init__() takes 1 positional argument but 2 positional arguments (and 1 keyword-only argument) were given
```

Nos campos de formulário, os argumentos são todos nomeados. Se quiser um rótulo, use `label='nome'`. No vídeo, as strings simplesmente foram removidas, e o código ficou como acima.

## A view que envia o e-mail

```python
# backend/crm/views.py
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from .forms import ContactForm


@require_http_methods(['POST'])
def send_contact(request):
    form = ContactForm(request.POST or None)

    if form.is_valid():
        subject = form.cleaned_data.get('title')
        message = form.cleaned_data.get('body')
        sender = form.cleaned_data.get('email')
        send_mail(
            subject,
            message,
            sender,
            ['localhost'],
            fail_silently=False,
        )
        return redirect('core:index')
```

Passo a passo:

* `@require_http_methods(['POST'])`: a view aceita **somente** POST. Um GET em `/crm/contact/` devolve `405 Method Not Allowed`. Não existe página de contato; o formulário fica na página inicial e só envia os dados para cá.
* `ContactForm(request.POST or None)`: preenche o formulário com os dados enviados.
* `form.is_valid()` valida os campos, e os valores limpos ficam em `form.cleaned_data`.
* `send_mail(subject, message, from_email, recipient_list, fail_silently=False)` é a função de envio de e-mail do Django (`django.core.mail`). A ordem dos argumentos é essa: assunto, mensagem, remetente e a **lista** de destinatários. No vídeo, o destinatário é simplesmente `['localhost']`, já que o MailHog aceita qualquer endereço. Num site real, aqui entraria o e-mail de quem atende o Fale Conosco. Com `fail_silently=False`, um erro de SMTP levanta exceção em vez de ser ignorado.
* No fim, `redirect('core:index')` volta para a página inicial.

## O template

No `index.html` (da Dica 11), o formulário Fale Conosco tinha `action="."`. Trocamos pela URL da view nova. Repare em dois detalhes que fazem tudo funcionar:

* o `{% csrf_token %}`, obrigatório em qualquer POST no Django;
* o atributo `name` de cada campo, que tem que ser **exatamente** o nome do campo no `ContactForm`: `name`, `email`, `title` e `body`.

```html
<!-- backend/core/templates/index.html -->
<h3 class="text-2xl font-extrabold mb-4">Fale Conosco</h3>
<p class="mb-4 leading-relaxed">Envie uma mensagem e diga como podemos te ajudar.</p>
<div>
  <form action="{% url 'crm:send_contact' %}" method="POST">
    {% csrf_token %}
    <input
      id="id_name"
      name="name"
      type="text"
      class="form-control"
      placeholder="Seu Nome"
    />
    <input
      id="id_email"
      name="email"
      type="email"
      class="form-control"
      placeholder="Seu E-mail"
    />
    <input
      id="id_title"
      name="title"
      type="text"
      class="form-control"
      placeholder="Título da mensagem"
    />
    <textarea
      id="id_body"
      name="body"
      type="text"
      class="form-control"
      rows="5"
    ></textarea>
    <button type="submit" class="bg-purple-600 hover:bg-purple-700 text-white py-3 rounded-lg w-full">Enviar</button>
  </form>
</div>
```

A classe `form-control` é a classe utilitária criada com `@apply` no `<head>` do `index.html` na Dica 11.

## Testando

Com o MailHog e o banco no ar (`docker-compose up -d`), rode o servidor:

```bash
python manage.py runserver
```

```
System check identified no issues (0 silenced).
November 25, 2022 - 14:56:23
Django version 4.1.3, using settings 'backend.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Abra [http://localhost:8000/#contato](http://localhost:8000/#contato), preencha o formulário (no vídeo: "Regis Santos", `regis@email.com`, um título e uma mensagem) e clique em **Enviar**. No terminal aparece o POST com redirecionamento (302) seguido do GET da página inicial:

```
"POST /crm/contact/ HTTP/1.1" 302 0
"GET / HTTP/1.1" 200 28490
```

Agora abra o MailHog em [http://localhost:8025](http://localhost:8025): a mensagem está lá, com o título como assunto, o e-mail do visitante como remetente e o texto digitado como corpo.

No vídeo, o primeiro envio não chegou ao MailHog porque a página ainda estava aberta com o HTML antigo (`action="."`), e o POST foi para `/`. Depois de recarregar a página, o envio foi para `/crm/contact/` e o e-mail apareceu. Se acontecer o mesmo com você, recarregue a página e confira no DevTools (aba *Network*) se o POST vai para `/crm/contact/`.

## Resumo

* O formulário do `index.html` envia um POST para `/crm/contact/`.
* Os `name` dos campos do HTML batem com os campos do `ContactForm`.
* A view `send_contact` valida o formulário, monta o e-mail com `send_mail` e redireciona para a página inicial.
* O MailHog recebe o e-mail na porta `1025` e mostra na interface da porta `8025`.

Observação: a view do vídeo não trata o formulário inválido. Como os campos do HTML não têm `required`, enviar o formulário com um campo vazio faz a view terminar sem `return`, e o Django mostra o erro `The view backend.crm.views.send_contact didn't return an HttpResponse object`. Para evitar isso, coloque `required` nos campos do HTML ou acrescente um `return redirect('core:index')` também fora do `if`.
