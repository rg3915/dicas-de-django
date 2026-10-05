# Micro SaaS: a verdade que ninguém te conta

Publicado em 02/12/2024.

**Testado com:** Django 5.1.3 e Python 3.12.
{: .versoes }

<a href="https://youtu.be/OySJ1KEhgSo">
    <img src="../.gitbook/assets/youtube.png">
</a>

Será que fazer um Micro SaaS é fácil e simples mesmo?

Github: [https://github.com/rg3915/micro-saas-yt](https://github.com/rg3915/micro-saas-yt)

Tem muito vídeo por aí dizendo "fiz um Micro SaaS num fim de semana e faturei 50 mil em 40 dias". O que quase ninguém mostra é o que vem antes e depois do código. Esta página tem duas partes:

1. o que um Micro SaaS realmente exige, além da ideia;
2. um exemplo prático: transformar um script que resolve um problema pequeno e específico (agrupar uma planilha Excel por categoria com subtotais) numa aplicação web com Django.

O repositório é a semente de um Micro SaaS, não um produto pronto. Ele **não tem** login, planos, assinatura nem pagamento: tem só a funcionalidade principal. Isso é proposital, e a primeira parte explica por quê.

## Parte 1: o que ninguém te conta

### Experiência prévia

Antes do produto vem a bagagem:

* **conhecimento de mercado**: saber quem tem o problema e quanto ele vale para essa pessoa;
* **experiência na tecnologia escolhida**, seja Python, Go, PHP ou JavaScript. Um Micro SaaS não é lugar para aprender o framework do zero;
* **experiência em deploy**: Fly.io, Vercel, Render, uma VPS ou outro serviço. Colocar no ar, configurar domínio, HTTPS, banco, backup e variáveis de ambiente leva tempo se você nunca fez.

### Planejamento sólido

Nos vídeos de sucesso a ideia parece surgir do nada e virar produto em horas. Na prática, mesmo um produto simples precisa de planejamento do produto em si, da experiência do usuário (UX) e do fluxo de dados (o que entra, o que é processado, o que é guardado e por quanto tempo).

### Pagamento

Você vai precisar receber. Não precisa começar com assinatura recorrente integrada a um gateway: um boleto ou uma cobrança manual resolvem no começo. Mas o fluxo de cobrança precisa existir antes do primeiro cliente.

### Suporte e manutenção

Sistema sem bug é sistema que ninguém usa. Quando os clientes chegam, os bugs aparecem, inclusive de madrugada e no fim de semana, com cliente reclamando que algo parou em produção. Planeje como e quando você vai atender.

### Legalidade e proteção de dados

Termos de uso, política de privacidade e adequação à LGPD. Vale contratar um advogado que entenda de contratos de tecnologia para escrever os termos e condições; isso evita dor de cabeça com clientes no futuro.

### Viés de sobrevivência

Há empreendedores que mostram vários produtos faturando milhares de dólares por mês. Eles mostram os que deram certo, não os muitos que deram errado. Esteja preparado para o caso mais comum: a ideia não decolar.

### Ideia brilhante não é obrigatória

Nem sempre você terá uma ideia revolucionária. Muitas vezes o Micro SaaS nasce de um cliente específico com um problema específico que você resolve de forma simples. É o caso do exemplo a seguir.

## Parte 2: do script ao Django

### O problema

Temos uma planilha com as colunas categoria, produto, quantidade e preço:

| categoria | produto | quantidade | preço |
|---|---|---|---|
| A | p1 | 5 | 23 |
| A | p2 | 4 | 22 |
| A | p3 | 2 | 12 |
| B | p1 | 4 | 53 |
| B | p2 | 4 | 5 |
| B | p4 | 2 | 3 |
| D | p5 | 7 | 6 |
| D | p1 | 5 | 2 |
| D | p2 | 9 | 6 |

Queremos gerar uma nova planilha agrupada por categoria: uma linha com o título da categoria, os produtos com a coluna `Total` (quantidade x preço), uma linha de subtotal e uma linha em branco antes da próxima categoria. O resultado esperado é:

| Categoria | Produto | Quantidade | Preço | Total |
|---|---|---|---|---|
| A | | | | |
| A | p1 | 5 | 23 | 115 |
| A | p2 | 4 | 22 | 88 |
| A | p3 | 2 | 12 | 24 |
| Subtotal | | | | 227 |
| | | | | |
| B | | | | |
| B | p1 | 4 | 53 | 212 |
| ... | | | | |

As duas planilhas estão no repositório: `planilha_original.xlsx` e `processado_planilha.xlsx`.

No vídeo, o primeiro rascunho do script foi pedido ao Claude ("leia o xlsx com openpyxl, agrupe por categoria com subtotal e salve numa nova planilha"). Depois foi pedida uma versão web; a IA fez em Flask, foi pedida de novo em Django, e o projeto final foi montado e ajustado à mão. A IA acelera, mas quem sabe Django é quem monta e corrige.

### Pré-requisitos

* Python 3.12 (o projeto usa Django 5.1.3).
* Noções de views, templates e upload de arquivos no Django.

### Instalação

```bash
git clone https://github.com/rg3915/micro-saas-yt.git
cd micro-saas-yt

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

# gera o .env com a SECRET_KEY
python contrib/env_gen.py

python manage.py migrate
python manage.py runserver
```

Dependências:

```
# requirements.txt
Django==5.1.3
django-extensions==3.2.3
openpyxl==3.1.5
python-decouple==3.8
```

* `openpyxl` lê e escreve arquivos `.xlsx`.
* `python-decouple` lê a `SECRET_KEY` do arquivo `.env`, para que ela nunca seja versionada.

### Estrutura do projeto

```
micro-saas-yt/
├── app/
│   ├── core/
│   │   ├── templates/
│   │   │   └── index.html
│   │   ├── apps.py
│   │   └── views.py
│   ├── settings.py
│   └── urls.py
├── contrib/
│   └── env_gen.py
├── manage.py
├── planilha_original.xlsx
├── processado_planilha.xlsx
└── requirements.txt
```

O projeto Django se chama `app` e a única app é `app.core`. Não há models: o arquivo é processado em memória e devolvido ao usuário, sem nada ser gravado.

### Settings

As partes que mudam em relação ao `startproject` padrão:

```python
# app/settings.py (trecho)
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'app.core',
]
```

Repare que `DEBUG` e `ALLOWED_HOSTS` estão fixos no código. Para um deploy de verdade, leia os dois do `.env` com `config('DEBUG', default=False, cast=bool)` e `config('ALLOWED_HOSTS', default=[], cast=Csv())` (o `env_gen.py` já gera essas variáveis).

A app precisa do `name` com o caminho completo, porque está dentro do pacote `app`:

```python
# app/core/apps.py
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.core'
```

### URLs

```python
# app/urls.py
from django.contrib import admin
from django.urls import path

from app.core.views import index


urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
]
```

### A view e o processamento

Todo o trabalho está em `views.py`: uma view que recebe o upload e uma função que processa a planilha.

```python
# app/core/views.py
# ... (veja o arquivo completo no GitHub)


def index(request):
    template_name = 'index.html'

    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            messages.error(request, 'Nenhum arquivo selecionado')
            return redirect('index')

        if not file.name.endswith('.xlsx'):
            messages.error(request, 'Por favor, envie apenas arquivos .xlsx')
            return redirect('index')

        try:
            # Processar o arquivo
            output = processar_planilha(file)

            # Retornar o arquivo processado
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename=processado_{file.name}'
            return response

        except Exception as e:
            messages.error(request, f'Erro ao processar arquivo: {str(e)}')
            return redirect('index')

    return render(request, template_name)


def processar_planilha(arquivo_entrada):
    # Carregar a planilha da memória
    wb = load_workbook(filename=arquivo_entrada)
    ws = wb.active

    # Dicionário para armazenar os dados agrupados
    dados_por_categoria = defaultdict(list)

    # Ler os dados e agrupar por categoria
    for row in ws.iter_rows(min_row=2, values_only=True):
        if len(row) < 4 or not all(row[:4]):
            continue
        categoria, produto, quantidade, preco = row[:4]
        # ... (veja o arquivo completo no GitHub)
    # Salvar em memória
    output = BytesIO()
    new_wb.save(output)
    output.seek(0)
    return output
```

Código completo: [app/core/views.py](https://github.com/rg3915/micro-saas-yt/blob/06230098de0b3855b0b175bc4ca07484100b79cf/app/core/views.py)

A view `index`:

* no `GET`, só renderiza o formulário;
* no `POST`, pega o arquivo em `request.FILES['file']`, valida se existe e se termina com `.xlsx`, e usa o framework de mensagens (`messages.error`) para avisar o usuário quando algo dá errado;
* se o processamento funciona, devolve um `HttpResponse` com o conteúdo do arquivo, o `content_type` de planilha do Excel e o cabeçalho `Content-Disposition: attachment`, que faz o navegador baixar o arquivo com o nome `processado_<nome original>`.

A função `processar_planilha`:

1. **Leitura**: `load_workbook` aceita o arquivo enviado diretamente, sem salvar em disco. `iter_rows(min_row=2, values_only=True)` pula o cabeçalho e devolve tuplas de valores.
2. **Agrupamento**: um `defaultdict(list)` acumula os produtos por categoria. Linhas incompletas ou com quantidade e preço não numéricos são ignoradas.
3. **Escrita**: cria um `Workbook` novo, escreve o cabeçalho em negrito e, para cada categoria em ordem alfabética, escreve a linha de título com fundo cinza, os produtos com o total, a linha de subtotal em negrito e pula uma linha (`current_row += 2`).
4. **Largura das colunas**: mede o maior texto de cada coluna (A a E, por isso `chr(64 + col)`) e ajusta a largura.
5. **Saída em memória**: salva num `BytesIO` e volta o ponteiro para o início com `seek(0)`.

### O template

```html
<!-- app/core/templates/index.html (sem o bloco <style>) -->
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- PicoCSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css" />

    <title>{% block title %}Processador de Planilhas{% endblock %}</title>
</head>

<body>
  <div class="container">

    {% if messages %}
    <div class="messages">
      {% for message in messages %}
      <div class="message {{ message.tags }}">{{ message }}</div>
      {% endfor %}
    </div>
    {% endif %}

    {% block content %}
    <div class="card">
      <h1>Upload de Planilha Excel</h1>

      <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        <div class="form-group">
          <label for="file">Selecione uma planilha Excel (.xlsx)</label>
          <input type="file" name="file" id="file" accept=".xlsx" required>
        </div>
        <button type="submit">Processar Planilha</button>
      </form>

      <div class="instructions card" style="margin-top: 2rem;">
        <h2>Instruções:</h2>
        <ul>
          <li>A planilha deve estar no formato .xlsx</li>
          <li>As colunas devem estar na seguinte ordem:
            <ul>
              <li>Categoria</li>
              <li>Produto</li>
              <li>Quantidade</li>
              <li>Preço</li>
            </ul>
          </li>
          <li>Após o processamento, uma nova planilha será baixada automaticamente</li>
        </ul>
      </div>
    </div>
    {% endblock %}
  </div>
</body>

</html>
```

Omiti aqui o bloco `<style>` do arquivo original (só CSS de cards, mensagens e botão) e um item das instruções que fala de uma aba "Histórico", que não existe no projeto. Os pontos essenciais:

* `enctype="multipart/form-data"` é obrigatório para enviar arquivos; sem ele, `request.FILES` chega vazio.
* `accept=".xlsx"` filtra a janela de seleção do navegador, mas não substitui a validação no servidor.
* o laço em `messages` mostra os erros gerados pela view; a classe `message.tags` vira `error` e recebe o estilo vermelho.

### Testando

Rode o servidor, acesse `http://localhost:8000`, envie o `planilha_original.xlsx` do repositório e confira que o navegador baixa `processado_planilha_original.xlsx` com o agrupamento e os subtotais 227, 238 e 106. Envie um `.csv` para ver a mensagem de erro.

## O que falta para virar um Micro SaaS

O repositório resolve o problema do cliente. Para cobrar por isso, a lista da primeira parte vira tarefas concretas:

* **contas de usuário**: login e cadastro, para saber quem usa;
* **cobrança**: começar simples (boleto ou cobrança manual) e, se fizer sentido, integrar um gateway com assinatura e limitar o uso por plano;
* **deploy**: `DEBUG` e `ALLOWED_HOSTS` vindos do ambiente, arquivos estáticos, HTTPS e monitoramento de erros;
* **robustez**: limite de tamanho de upload, tratamento de planilhas com colunas fora de ordem e testes automatizados da função `processar_planilha`;
* **jurídico**: termos de uso, política de privacidade e LGPD, principalmente porque o cliente está enviando dados dele para o seu servidor;
* **suporte**: um canal de atendimento e a disposição para responder quando algo quebrar.

## Resumo

Micro SaaS não sai num fim de semana. A parte do código pode até ser pequena, como mostra este projeto de uma view e uma função, mas a experiência na stack e em deploy, o planejamento, a cobrança, o suporte e a parte legal pesam mais do que a ideia. Comece resolvendo um problema real e específico, e cresça a partir dele.
