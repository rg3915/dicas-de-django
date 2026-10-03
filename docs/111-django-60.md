# Novidades do Django 6.0

Publicado em 05/01/2026.

**Testado com:** Django 6.0 e Python 3.12.
{: .versoes }

<a href="https://youtu.be/zug6K_Lks9k">
    <img src="../.gitbook/assets/youtube.png">
</a>

Doc: [https://docs.djangoproject.com/en/6.0/releases/6.0/](https://docs.djangoproject.com/en/6.0/releases/6.0/)

Github: [https://github.com/rg3915/django60](https://github.com/rg3915/django60)

O Django 6.0 foi lançado em 3 de dezembro de 2025 e trouxe quatro novidades grandes: **Content Security Policy (CSP) nativo**, **template partials**, um **framework de tasks em background** e a adoção da **API moderna de e-mail do Python**.

Neste tutorial vamos ver cada uma delas num projeto real: um catálogo de produtos que usa partials para os cards, gera um PDF da lista de produtos em background e envia esse PDF por e-mail, tudo protegido por uma política CSP.

## Pré-requisitos

* **Python 3.12 ou superior.** O Django 6.0 não roda em versões anteriores; confira com `python --version` antes de atualizar.
* Docker, para subir o MailHog (servidor de e-mail de testes). É opcional: dá para ver os e-mails no console.
* As bibliotecas de sistema do WeasyPrint (Pango), usado para gerar o PDF. No macOS, `brew install pango`; no Debian/Ubuntu, `apt install libpango-1.0-0 libpangoft2-1.0-0`. Detalhes em [https://doc.courtbouillon.org/weasyprint/stable/first_steps.html](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html).

## Instalação

```bash
git clone https://github.com/rg3915/django60.git
cd django60

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python contrib/env_gen.py

python manage.py migrate
python manage.py createsuperuser
python manage.py create_data  # popula o banco com 36 produtos de exemplo
```

As dependências:

```
# requirements.txt
Django==6.0
django-extensions==4.1
django-tasks==0.10.0
Pillow==12.0.0
python-decouple==3.8
ruff==0.14.9
weasyprint==67.0
```

## O model de produto

Tudo gira em torno de um model simples:

```python
# apps/produto/models.py
from django.db import models


class Produto(models.Model):
    class Categoria(models.TextChoices):
        ELETRONICOS = 'eletronicos', 'Eletrônicos'
        LIVROS = 'livros', 'Livros'
        VESTUARIO = 'vestuario', 'Vestuário'
        ALIMENTOS = 'alimentos', 'Alimentos'
        ESPORTES = 'esportes', 'Esportes'
        CASA = 'casa', 'Casa e Decoração'

    nome = models.CharField('Nome', max_length=200)
    descricao = models.TextField('Descrição')
    preco = models.DecimalField('Preço', max_digits=10, decimal_places=2)
    categoria = models.CharField(
        'Categoria',
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.ELETRONICOS,
    )
    imagem = models.ImageField(
        'Imagem',
        upload_to='produtos/',
        blank=True,
        null=True,
        help_text='Imagem do produto (opcional)',
    )
    estoque = models.PositiveIntegerField('Estoque', default=0)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    modificado_em = models.DateTimeField('Modificado em', auto_now=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['categoria', '-criado_em']),
            models.Index(fields=['ativo', 'estoque']),
        ]

    def __str__(self):
        return f'{self.nome} - R$ {self.preco}'

    @property
    def disponivel(self):
        """Verifica se o produto está disponível para venda"""
        return self.ativo and self.estoque > 0

    @property
    def categoria_display(self):
        """Retorna o nome legível da categoria"""
        return self.get_categoria_display()
```

## 1. Content Security Policy nativo

A CSP é um cabeçalho HTTP que diz ao navegador de onde ele pode carregar scripts, estilos, imagens e fontes. Se um atacante conseguir injetar um `<script>` na página (XSS), o navegador se recusa a executá-lo, porque ele não está na lista de origens permitidas nem tem o nonce correto.

Antes do 6.0 era preciso instalar o pacote `django-csp`. Agora basta configurar três coisas no `settings.py`: o middleware, o context processor e a política.

```python
# apps/settings.py (trecho)
from django.middleware.csp import CSP

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Django 6.0 - Content Security Policy
    'django.middleware.csp.ContentSecurityPolicyMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Django 6.0 - CSP context processor para nonces
                'django.template.context_processors.csp',
            ],
        },
    },
]

SECURE_CSP = {
    'default-src': [CSP.SELF],
    'script-src': [CSP.SELF, CSP.NONCE],
    'style-src': [CSP.SELF, CSP.NONCE, 'https://cdn.jsdelivr.net'],
    'font-src': [CSP.SELF, 'data:'],
    'img-src': [CSP.SELF, 'data:', 'https:', 'https://picsum.photos'],
}
```

* **`ContentSecurityPolicyMiddleware`** monta o cabeçalho `Content-Security-Policy` a partir de `SECURE_CSP`. Existe também `SECURE_CSP_REPORT_ONLY`, que só reporta violações sem bloquear; é uma boa forma de testar a política antes de aplicá-la.
* **`CSP`** é um enum com as palavras-chave da especificação: `CSP.SELF` vira `'self'`, `CSP.NONE` vira `'none'`, `CSP.UNSAFE_INLINE` vira `'unsafe-inline'` e assim por diante. A documentação importa de `django.utils.csp`; o projeto importa de `django.middleware.csp`, que expõe o mesmo objeto.
* **`CSP.NONCE`** faz o Django gerar um valor aleatório por requisição e colocá-lo na política como `'nonce-...'`.
* **`django.template.context_processors.csp`** disponibiliza esse valor nos templates como `{{ csp_nonce }}`.

Nesta política, scripts só rodam se vierem do próprio site ou tiverem o nonce; estilos podem vir do site, do jsDelivr (onde está o Pico CSS) ou ter o nonce; imagens podem vir de qualquer HTTPS (o `picsum.photos` é redundante com `https:`, mas deixa a intenção explícita).

O cabeçalho gerado fica assim (o nonce muda a cada requisição):

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-udsbF1oSegOeFabQGZY4tw'; style-src 'self' 'nonce-udsbF1oSegOeFabQGZY4tw' https://cdn.jsdelivr.net; font-src 'self' data:; img-src 'self' data: https: https://picsum.photos
```

Nos templates, todo `<script>` inline precisa do nonce, senão o navegador o bloqueia:

```html
<!-- apps/core/templates/base.html (trecho) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css" nonce="{{ csp_nonce }}">

<script nonce="{{ csp_nonce }}">
  // Toast Manager - gerencia notificações na tela
  class ToastManager {
    // ...
  }
  window.toastManager = new ToastManager();
</script>
```

Teste: tire o `nonce` de um `<script>` inline, recarregue a página e abra o console do navegador. Você verá o erro de violação de CSP e o script não roda.

## 2. Template partials

Partials são fragmentos nomeados de template, definidos dentro de um arquivo e reutilizados sem precisar criar um arquivo separado para cada componente. São duas tags:

* `{% partialdef nome %} ... {% endpartialdef %}` define o fragmento. Por padrão, ele **não** é renderizado onde foi definido (para renderizar no lugar também, use `{% partialdef nome inline %}`).
* `{% partial nome %}` renderiza o fragmento, usando o contexto atual.

Além disso, qualquer ferramenta que carrega templates passa a aceitar a sintaxe `arquivo.html#nome`: `{% include %}`, `render()`, `get_template()`.

### Mesmo arquivo: a lista de produtos

```html
<!-- apps/produto/templates/produto/produto_list.html (trecho) -->
{% extends 'base.html' %}

{% block title %}Produtos - Django 6.0{% endblock %}

{% block content %}
{% partialdef produto_card %}
<article class="produto-card">
    <img src="{% if produto.imagem %}{{ produto.imagem.url }}{% else %}https://picsum.photos/seed/{{ produto.id }}/400/300{% endif %}"
         alt="{{ produto.nome }}"
         class="produto-card-img">

    <div class="produto-card-body">
        <hgroup>
            <h4>{{ produto.nome }}</h4>
            <p><kbd>{{ produto.get_categoria_display }}</kbd></p>
        </hgroup>

        <p class="produto-card-desc">{{ produto.descricao|truncatewords:15 }}</p>

        <div class="produto-card-footer-wrapper">
            <footer class="produto-card-footer">
                <strong class="produto-card-price">R$ {{ produto.preco }}</strong>
                {% if produto.disponivel %}
                    <small class="produto-card-stock">✓ {{ produto.estoque }} un.</small>
                {% else %}
                    <mark>Indisponível</mark>
                {% endif %}
            </footer>
            <a href="{% url 'produto:produto_detail' produto.pk %}" role="button" class="produto-card-btn">Ver Detalhes</a>
        </div>
    </div>
</article>
{% endpartialdef %}

<hgroup>
    <h1>Catálogo de Produtos</h1>
    <p>Demonstração de <strong>Template Partials</strong> do Django 6.0</p>
</hgroup>

<div class="grid grid-equal-rows">
    {% for produto in produtos %}
        {% partial produto_card %}
    {% empty %}
        <article>
            <p><strong>Nenhum produto encontrado</strong></p>
            <p><a href="{% url 'produto:produto_list' %}">Ver todos os produtos</a></p>
        </article>
    {% endfor %}
</div>
{% endblock %}
```

O arquivo completo também tem os filtros por categoria, os botões de PDF e e-mail, a paginação e um script de polling, que veremos na seção de tasks. O ponto aqui é: o card é definido uma vez no topo e renderizado a cada volta do `for` com `{% partial produto_card %}`, enxergando a variável `produto` do laço.

### Outro arquivo: produtos relacionados

Para compartilhar o card entre templates, o projeto tem um arquivo só de partials, `produto/partials.html`, com o mesmo `{% partialdef produto_card %}` (e um `produto_detail_card`). A página de detalhe inclui o card de lá:

```html
<!-- apps/produto/templates/produto/produto_detail.html (trecho) -->
{% partial produto_detail_card %}

{% if produtos_relacionados %}
    <h2>Produtos Relacionados</h2>
    <div class="grid">
        {% for produto_relacionado in produtos_relacionados %}
            {% with produto=produto_relacionado %}
                {% include "produto/partials.html#produto_card" %}
            {% endwith %}
        {% endfor %}
    </div>
{% endif %}
```

O `{% with %}` renomeia a variável para `produto`, que é o nome que o partial espera. O `produto_detail_card` é definido no topo do próprio `produto_detail.html` e renderizado com `{% partial %}`, como na lista.

Antes do 6.0 a saída era criar um arquivo por componente (`_produto_card.html`) e usar `{% include %}`, ou escrever uma template tag. Quem usava o pacote `django-template-partials` tem um guia de migração na documentação.

## 3. Background tasks

O Django 6.0 traz uma API padrão para definir e enfileirar tarefas que rodam fora do ciclo requisição/resposta, como gerar um relatório ou mandar um e-mail. É importante entender a divisão de responsabilidades:

* o **Django** define a API: o decorator `@task`, o método `.enqueue()`, os resultados e o setting `TASKS`;
* o Django **não** traz um worker. Os dois backends nativos são para desenvolvimento e testes: `ImmediateBackend` (executa na hora, de forma síncrona) e `DummyBackend` (não executa nada);
* para rodar em background de verdade, use um backend externo. O projeto usa o pacote **django-tasks**, com o `DatabaseBackend` (a fila fica no próprio banco) e o comando `db_worker`.

Para casos simples, isso dispensa Celery e um broker como Redis ou RabbitMQ. Para cenários complexos, o Celery continua sendo opção.

### Configuração

```python
# apps/settings.py (trecho)
INSTALLED_APPS = [
    # ...
    'django_extensions',
    # Django Tasks Database Backend
    'django_tasks.backends.database',
    'apps.core',
    'apps.produto',
]

TASKS = {
    'default': {
        'BACKEND': 'django_tasks.backends.database.backend.DatabaseBackend',
    }
}

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR.joinpath('media')
```

A app `django_tasks.backends.database` cria as tabelas da fila, por isso rode `python manage.py migrate` depois de adicioná-la.

### Definindo as tasks

```python
# apps/produto/tasks.py
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMessage
from django.tasks import task
from django.template.loader import render_to_string
from weasyprint import HTML

from .models import Produto


@task
def gerar_pdf_produtos(categoria=None):
    """
    Task em background para gerar PDF com lista de produtos.
    Django 6.0 - Background Tasks Framework
    """
    # Gerar timestamp no formato YYMMDD_HHMMSS
    timestamp = datetime.now().strftime('%y%m%d_%H%M%S')

    # Filtrar produtos
    if categoria:
        produtos = Produto.objects.filter(categoria=categoria, ativo=True)
        filename = f'produtos_{categoria}_{timestamp}.pdf'
    else:
        produtos = Produto.objects.filter(ativo=True)
        filename = f'produtos_todos_{timestamp}.pdf'

    # Renderizar template HTML
    html_content = render_to_string(
        'produto/pdf_template.html',
        {
            'produtos': produtos,
            'categoria': categoria,
            'total': produtos.count(),
        },
    )

    # Criar diretório media/pdfs se não existir
    pdf_dir = Path(settings.MEDIA_ROOT) / 'pdfs'
    pdf_dir.mkdir(parents=True, exist_ok=True)

    # Gerar PDF com Weasyprint
    pdf_path = pdf_dir / filename
    HTML(string=html_content).write_pdf(pdf_path)

    return {
        'success': True,
        'filename': filename,
        'path': str(pdf_path),
        'total_produtos': produtos.count(),
    }


@task
def gerar_e_enviar_pdf_por_email(email_destinatario, categoria=None):
    """
    Task em background para gerar PDF e enviar por email.
    Django 6.0 - Modern Email API + Background Tasks
    """
    # Gerar timestamp no formato YYMMDD_HHMMSS
    timestamp = datetime.now().strftime('%y%m%d_%H%M%S')

    # Filtrar produtos
    if categoria:
        produtos = Produto.objects.filter(categoria=categoria, ativo=True)
        filename = f'produtos_{categoria}_{timestamp}.pdf'
        categoria_nome = dict(Produto.Categoria.choices)[categoria]
        assunto = f'Catálogo de Produtos - {categoria_nome}'
    else:
        produtos = Produto.objects.filter(ativo=True)
        filename = f'produtos_todos_{timestamp}.pdf'
        assunto = 'Catálogo Completo de Produtos'

    # Renderizar template HTML para PDF
    html_content = render_to_string(
        'produto/pdf_template.html',
        {
            'produtos': produtos,
            'categoria': categoria,
            'total': produtos.count(),
        },
    )

    # Criar diretório media/pdfs se não existir
    pdf_dir = Path(settings.MEDIA_ROOT) / 'pdfs'
    pdf_dir.mkdir(parents=True, exist_ok=True)

    # Gerar PDF com Weasyprint
    pdf_path = pdf_dir / filename
    HTML(string=html_content).write_pdf(pdf_path)

    # Django 6.0 - Modern Email API
    # Criar email com PDF anexo
    email = EmailMessage(
        subject=assunto,
        body=f"""Olá!

Segue em anexo o catálogo de produtos solicitado.

Total de produtos: {produtos.count()}
{f'Categoria: {categoria_nome}' if categoria else 'Todas as categorias'}

Atenciosamente,
Equipe Django 6.0
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email_destinatario],
    )

    # Anexar PDF ao email
    with open(pdf_path, 'rb') as pdf_file:
        email.attach(filename, pdf_file.read(), 'application/pdf')

    # Enviar email
    email.send()

    return {
        'success': True,
        'email_enviado': email_destinatario,
        'filename': filename,
        'path': str(pdf_path),
        'total_produtos': produtos.count(),
    }
```

* `@task` (de `django.tasks`) transforma a função numa task. Ela continua sendo uma função comum no código, mas ganha o método `.enqueue()`.
* Os argumentos e o valor de retorno precisam ser serializáveis em JSON, porque vão para a fila e para a tabela de resultados. Por isso a task recebe a **categoria** (uma string) e não um queryset, e devolve um dicionário simples.
* A primeira task renderiza o template `pdf_template.html` com `render_to_string` e o converte em PDF com o WeasyPrint, salvando em `media/pdfs/`.
* A segunda faz o mesmo e envia o PDF anexado por e-mail.

### Enfileirando nas views

```python
# apps/produto/views.py (trecho)
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django_tasks.backends.database.models import DBTaskResult

from .models import Produto
from .tasks import gerar_e_enviar_pdf_por_email, gerar_pdf_produtos


def gerar_pdf(request):
    categoria = request.GET.get('categoria')

    # Enfileira a task em background
    task = gerar_pdf_produtos.enqueue(categoria=categoria)

    # Se for requisição AJAX, retornar JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(
            {
                'task_id': str(task.id),
                'message': 'PDF sendo gerado em background',
            }
        )

    messages.success(
        request,
        f'PDF de todos os produtos está sendo gerado em background. Task ID: {task.id}',
    )
    return redirect('produto:produto_list')


def task_status(request, task_id):
    """API para verificar status de uma task"""
    try:
        task = DBTaskResult.objects.get(id=task_id)

        status_map = {
            'READY': 'pending',
            'RUNNING': 'running',
            'SUCCEEDED': 'completed',
            'FAILED': 'error',
        }
        status = status_map.get(task.status, 'pending')
        response_data = {'status': status}

        if status == 'completed' and task.return_value:
            result = task.return_value
            response_data.update(
                {
                    'filename': result.get('filename'),
                    'download_url': f'/media/pdfs/{result.get("filename")}',
                    'total_produtos': result.get('total_produtos'),
                }
            )

        if status == 'error' and task.exception_class_path:
            response_data['error_message'] = task.exception_class_path

        return JsonResponse(response_data)

    except DBTaskResult.DoesNotExist:
        return JsonResponse({'error': 'Task não encontrada'}, status=404)
```

Simplifiquei a mensagem de sucesso de `gerar_pdf` (no repositório ela muda quando há categoria). O fluxo:

1. `gerar_pdf_produtos.enqueue(categoria=...)` grava a task na fila e devolve na hora um resultado com `id` (um UUID) e status `READY`. A view responde sem esperar o PDF.
2. No front-end, o clique em "Gerar PDF" é feito via `fetch` com o cabeçalho `X-Requested-With`, e a view devolve o `task_id` em JSON.
3. Um script (`PollingManager`, em `produto_list.html`, com `nonce="{{ csp_nonce }}"`) consulta `/produtos/task-status/<task_id>/` a cada 3 segundos. Essa view lê o `DBTaskResult` do django-tasks e, quando o status vira `SUCCEEDED`, devolve o link do PDF, que aparece num toast.

As rotas:

```python
# apps/produto/urls.py
from django.urls import path

from . import views

app_name = 'produto'

urlpatterns = [
    path('', views.ProdutoListView.as_view(), name='produto_list'),
    path('<int:pk>/', views.produto_detail, name='produto_detail'),
    path('gerar-pdf/', views.gerar_pdf, name='gerar_pdf'),
    path(
        'solicitar-pdf-email/',
        views.solicitar_pdf_email,
        name='solicitar_pdf_email',
    ),
    path('task-status/<uuid:task_id>/', views.task_status, name='task_status'),
]
```

### Rodando o worker

Sem worker, as tasks ficam paradas em `READY`. Em outro terminal:

```bash
python manage.py db_worker
```

Para processar o que estiver na fila e sair (útil em testes ou num cron), use `python manage.py db_worker --batch`. O andamento de cada task (pronta, executando, sucesso ou falha, com o retorno e o traceback) aparece no Django Admin, na seção do django-tasks.

## 4. API moderna de e-mail

Aqui vale ser preciso. A novidade do 6.0 é **interna**: o envio de e-mails do Django passou a usar a API moderna do pacote `email` do Python, centrada em `email.message.EmailMessage`, no lugar da API legada (`Compat32` e as classes de `email.mime`). Na prática:

* `EmailMessage.message()` agora devolve um `email.message.EmailMessage` do Python;
* `EmailMessage.message()` aceita o argumento `policy`;
* `EmailMessage.attach()` passou a aceitar um objeto `MIMEPart`;
* `SafeMIMEText` e `SafeMIMEMultipart` foram depreciadas.

A forma de uso que o projeto mostra, `EmailMessage(...)` seguido de `email.attach(nome, conteudo, mimetype)` e `email.send()`, já existia em versões anteriores. Ela continua funcionando igual, agora com um motor mais limpo e melhor com Unicode por baixo.

A view que dispara o envio usa um form simples (e-mail e categoria opcional) e enfileira a segunda task:

```python
# apps/produto/views.py (trecho)
from django.shortcuts import redirect, render

from .forms import SolicitarPDFEmailForm


def solicitar_pdf_email(request):
    if request.method == 'POST':
        form = SolicitarPDFEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            categoria = form.cleaned_data.get('categoria') or None

            task = gerar_e_enviar_pdf_por_email.enqueue(
                email_destinatario=email, categoria=categoria
            )

            messages.success(
                request,
                f'Catálogo completo será enviado para {email} '
                f'em instantes. Task ID: {task.id}',
            )
            return redirect('produto:solicitar_pdf_email')
    else:
        form = SolicitarPDFEmailForm()

    return render(
        request, 'produto/solicitar_pdf_email.html', {'form': form}
    )
```

```python
# apps/produto/forms.py
from django import forms

from .models import Produto


class SolicitarPDFEmailForm(forms.Form):
    email = forms.EmailField(
        label='Seu Email',
        max_length=254,
        required=True,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'seu@email.com',
                'autocomplete': 'email',
            }
        ),
        help_text='Enviaremos o catálogo de produtos em PDF para este email.',
    )

    categoria = forms.ChoiceField(
        label='Categoria',
        required=False,
        choices=[('', 'Todas as categorias')] + list(Produto.Categoria.choices),
        widget=forms.Select(),
        help_text='Escolha uma categoria específica ou deixe em branco para todas.',
    )
```

A configuração de e-mail aponta, por padrão, para o MailHog em `localhost:1025`:

```python
# apps/settings.py (trecho)
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.smtp.EmailBackend',
)
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=1025, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL', default='noreply@django60.com'
)
```

E o MailHog sobe com Docker Compose:

```yaml
# docker-compose.yml
version: '3.8'

services:
  mailhog:
    image: mailhog/mailhog:latest
    container_name: django60_mailhog
    ports:
      - "1025:1025"  # SMTP server
      - "8025:8025"  # Web UI
    networks:
      - django60_network
    restart: unless-stopped

networks:
  django60_network:
    driver: bridge
```

Se não quiser usar Docker, coloque `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` no `.env` e o e-mail será impresso no terminal do worker.

## Rodando tudo

São três processos:

```bash
# terminal 1: MailHog
docker compose up -d

# terminal 2: worker das tasks
python manage.py db_worker

# terminal 3: servidor
python manage.py runserver
```

Roteiro de teste:

1. Acesse `http://localhost:8000/produtos/`: os cards vêm do partial `produto_card`.
2. Abra um produto: o card de detalhe vem de `{% partial %}` e os relacionados de `{% include "produto/partials.html#produto_card" %}`.
3. Clique em "Gerar PDF de Todos": o toast avisa que o PDF está sendo gerado e, alguns segundos depois, mostra o link. O arquivo fica em `media/pdfs/`.
4. Clique em "Solicitar Catálogo por Email", informe um e-mail e envie. Abra `http://localhost:8025` e veja a mensagem com o PDF anexado no MailHog.
5. No admin (`http://localhost:8000/admin/`), veja os resultados das tasks e seus status.
6. Inspecione os cabeçalhos da resposta no DevTools e procure `Content-Security-Policy`.

## Resumo

* **Python 3.12+** é obrigatório no Django 6.0.
* **CSP**: `ContentSecurityPolicyMiddleware`, `SECURE_CSP` com o enum `CSP` e `{{ csp_nonce }}` via context processor, sem pacote externo.
* **Template partials**: `{% partialdef %}` e `{% partial %}` no mesmo arquivo, e `arquivo.html#nome` em `include` e `render`.
* **Tasks**: `@task` e `.enqueue()` são nativos, mas a execução depende de um backend; com o django-tasks, `DatabaseBackend` e `db_worker`.
* **E-mail**: o motor interno passou a usar a API moderna do Python; a API pública que você já usava continua a mesma.

Documentação: [CSP](https://docs.djangoproject.com/en/6.0/ref/csp/), [Tasks](https://docs.djangoproject.com/en/6.0/topics/tasks/), [linguagem de templates](https://docs.djangoproject.com/en/6.0/ref/templates/language/) e [django-tasks](https://github.com/RealOrangeOne/django-tasks).
