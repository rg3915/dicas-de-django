# Django Ninja 1.3.0 - PatchDict

Publicado em 12/11/2024.

<a href="https://youtu.be/_k-Iu96oL4c">
    <img src="../.gitbook/assets/youtube.png">
</a>

Release: [https://github.com/vitalik/django-ninja/releases/tag/v1.3.0](https://github.com/vitalik/django-ninja/releases/tag/v1.3.0)

Github do projeto: [https://github.com/rg3915/alpinejs-django-ninja-crud](https://github.com/rg3915/alpinejs-django-ninja-crud)

A versão 1.3.0 do Django Ninja trouxe uma novidade pequena e muito útil: o `PatchDict`. Com ele, um endpoint `PATCH` aceita só os campos que você quer alterar, mesmo que o schema de entrada tenha campos obrigatórios.

Neste tutorial vamos montar a API de despesas do projeto `alpinejs-django-ninja-crud` (models, schemas e rotas CRUD), adicionar uma relação nova com `Person`, ver o problema que aparece na edição e resolver com `PatchDict`. No fim, escrevemos os testes com pytest-django.

## PUT x PATCH

Antes do código, a diferença entre os dois verbos HTTP:

* **PUT** substitui o recurso inteiro pelo dado enviado. Se faltar um campo, ele é considerado ausente.
* **PATCH** aplica uma alteração parcial: atualiza só os campos enviados e mantém o resto.

O problema clássico é usar o mesmo schema do `POST` (com campos obrigatórios) no `PATCH`. Aí o cliente é obrigado a mandar tudo de novo, o que não é uma atualização parcial de verdade.

## Pré-requisitos

* Python 3.10 ou superior (o projeto usa Django 5.0, que não roda no Python 3.9).
* Noções de Django (models, migrations) e de API REST.
* Django Ninja 1.3.0 ou superior.

## Clonando e rodando o projeto

```bash
git clone https://github.com/rg3915/alpinejs-django-ninja-crud.git
cd alpinejs-django-ninja-crud

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

# cria o arquivo .env com SECRET_KEY, DEBUG e ALLOWED_HOSTS
python contrib/env_gen.py

python manage.py migrate
python manage.py runserver
```

O `requirements.txt` do repositório já está com a versão nova do Django Ninja:

```
# requirements.txt
Django==5.0.1
django-extensions==3.2.3
django-ninja==1.3.0
python-decouple==3.8
ruff==0.1.9
```

Se você está atualizando um projeto antigo (no vídeo o projeto estava na 1.1.0), rode:

```bash
pip install -U django-ninja
pip freeze | grep ninja
```

A tela inicial é um CRUD de despesas feito com AlpineJS que consome a API. A documentação interativa da API fica em `http://localhost:8000/api/v1/docs`.

## Os models

A app `expense` tem dois models: `Person` (a pessoa responsável pela despesa) e `Expense` (a despesa). O `Person` foi adicionado depois que o projeto já tinha dados, por isso a chave estrangeira é opcional (`null=True, blank=True`): registros antigos ficam sem pessoa e a migração não quebra.

```python
# backend/expense/models.py
from datetime import datetime

from django.db import models


class Person(models.Model):
    name = models.CharField('nome', max_length=100, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'pessoa'
        verbose_name_plural = 'pessoas'

    def __str__(self):
        return f'{self.name}'


class Expense(models.Model):
    description = models.CharField('descrição', max_length=120)
    value = models.DecimalField('valor', max_digits=7, decimal_places=2)
    date_payment = models.DateField('data', null=True, blank=True)
    person = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        verbose_name='pessoa',
        related_name='expenses',
        null=True,
        blank=True
    )
    created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'despesa'
        verbose_name_plural = 'despesas'

    def __str__(self):
        return f'{self.description}'

    def date_payment_display(self):
        if self.date_payment:
            date_str = self.date_payment.isoformat()
            iso_date = datetime.fromisoformat(date_str)
            return iso_date.strftime('%d/%m/%Y')
        return ''
```

Pontos importantes:

* `on_delete=models.SET_NULL`: se a pessoa for apagada, a despesa continua existindo, só que sem pessoa.
* `related_name='expenses'`: permite fazer `person.expenses.all()`.
* `date_payment_display()` devolve a data no formato brasileiro. Esse método vira um campo extra na resposta da API.

Depois de mexer no model, gere e aplique a migração:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Registrando a API

O `NinjaAPI` é criado num arquivo próprio e recebe o router da app `expense`:

```python
# backend/api.py
from ninja import NinjaAPI

api = NinjaAPI()

api.add_router('', 'backend.expense.api.router')
```

E as URLs do projeto expõem a API em `/api/v1/`:

```python
# backend/urls.py
from django.contrib import admin
from django.urls import include, path

from .api import api

urlpatterns = [
    path('', include('backend.core.urls', namespace='core')),
    path('expense/', include('backend.expense.urls', namespace='expense')),
    path('api/v1/', api.urls),
    path('admin/', admin.site.urls),
]
```

## Schemas e rotas CRUD

Este é o arquivo principal do tutorial, já com o `PatchDict`:

```python
# backend/expense/api.py
from http import HTTPStatus

from django.shortcuts import get_object_or_404
from ninja import PatchDict, ModelSchema, Router
from ninja.orm import create_schema

from .models import Expense

router = Router(tags=['Expenses'])


ExpenseSchema = create_schema(
    Expense, custom_fields=(('date_payment_display', str, None),)
)


class ExpenseCreateSchema(ModelSchema):
    person_id: int
    # https://github.com/vitalik/django-ninja/issues/444#issuecomment-1148543491

    class Meta:
        model = Expense
        fields = (
            'description',
            'value',
            'date_payment',
        )


@router.get('expenses', response=list[ExpenseSchema])
def list_expense(request):
    return Expense.objects.all()


@router.get('expenses/{pk}', response=ExpenseSchema)
def detail_expense(request, pk: int):
    return get_object_or_404(Expense, pk=pk)


@router.post('expenses', response={HTTPStatus.CREATED: ExpenseSchema})
def create_expense(request, payload: ExpenseCreateSchema):
    return Expense.objects.create(**payload.dict())


@router.patch('expenses/{pk}', response=ExpenseSchema)
def update_expense(request, pk: int, payload: PatchDict[ExpenseCreateSchema]):
    instance = get_object_or_404(Expense, pk=pk)
    # data = payload.dict()

    for attr, value in payload.items():
        setattr(instance, attr, value)

    instance.save()
    return instance


@router.delete('expenses/{pk}')
def delete_expense(request, pk: int):
    instance = get_object_or_404(Expense, pk=pk)
    instance.delete()
    return {'success': True}
```

O que cada parte faz:

* **`ExpenseSchema`** (saída): gerado com `create_schema` a partir do model. O `custom_fields` acrescenta o campo `date_payment_display` (do tipo `str`), que o Ninja preenche chamando o método de mesmo nome no model.
* **`ExpenseCreateSchema`** (entrada): um `ModelSchema` com `description`, `value` e `date_payment`, mais `person_id: int`. Declarar a chave estrangeira com o sufixo `_id` faz o Ninja aceitar o id da pessoa, e o `Expense.objects.create(**payload.dict())` grava direto na coluna `person_id`. A dica é do próprio criador do Ninja, na issue citada no comentário.
* **`list_expense` e `detail_expense`**: `GET` da lista e de um item. O `get_object_or_404` devolve 404 se o id não existir.
* **`create_expense`**: `POST` que devolve status 201 (`HTTPStatus.CREATED`).
* **`delete_expense`**: apaga e devolve `{'success': True}`, que o front-end usa para remover a linha da tabela.

## O problema na edição

Antes da 1.3.0, a rota de edição recebia `payload: ExpenseCreateSchema`. Como `person_id` é declarado como `int` (obrigatório), ao editar uma despesa antiga, que não tem pessoa, a API respondia com erro 422 dizendo que `person_id` é um campo obrigatório. O mesmo acontece com `value`, que é obrigatório no model: se o cliente não enviar, a validação falha.

A saída seria criar um segundo schema com todos os campos opcionais, só para o `PATCH`. É exatamente isso que o `PatchDict` faz por você.

## A solução com PatchDict

Basta envolver o schema de entrada:

```python
from ninja import PatchDict

@router.patch('expenses/{pk}', response=ExpenseSchema)
def update_expense(request, pk: int, payload: PatchDict[ExpenseCreateSchema]):
    ...
```

Com `PatchDict[ExpenseCreateSchema]`:

* todos os campos do schema passam a ser opcionais;
* o `payload` é um **dicionário** (não mais um objeto Pydantic) contendo **somente** os campos que o cliente enviou.

Por isso não se usa mais `payload.dict()`, e sim `payload.items()`. O laço com `setattr` copia para a instância apenas o que veio na requisição; o resto fica como estava no banco. Por fim, `instance.save()` grava e a função devolve a instância, serializada com `ExpenseSchema`.

Um exemplo de requisição que agora funciona, alterando só a descrição:

```bash
curl -X PATCH http://localhost:8000/api/v1/expenses/1 \
  -H 'Content-Type: application/json' \
  -d '{"description": "Livro de Python"}'
```

## O lado do front-end

O CRUD em AlpineJS já envia `PATCH` na edição. Ele remove o `id` do objeto e manda o resto no corpo:

```javascript
// backend/core/static/js/expense.js (trecho)
updateItem(url) {
  const id = this.editItem.id
  // Remove o id e associa o restante a bodyData
  const { id: _, ...bodyData } = this.editItem

  axios.patch(`${url}/${id}`, bodyData, { headers })
    .then(response => {
      this.updateItemInList(response.data)
      this.resetForm()
    })
},
```

Com o `PatchDict`, editar uma despesa sem pessoa passa a funcionar sem erro de validação.

## Testes com pytest-django

Update parcial é o tipo de coisa que precisa de teste. Instale o pytest-django (ele não está no `requirements.txt` do repositório):

```bash
pip install pytest-django
```

Crie o arquivo de configuração na raiz do projeto:

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = backend.settings
python_files = tests.py test_*.py *_tests.py
addopts = -p no:warnings
```

* `DJANGO_SETTINGS_MODULE` diz ao pytest qual settings usar.
* `python_files` define quais arquivos contêm testes (incluindo o `tests.py` padrão das apps).
* `-p no:warnings` esconde os avisos para deixar a saída limpa.

Agora os testes:

```python
# backend/expense/tests.py
from http import HTTPStatus

import pytest

from .models import Expense


@pytest.mark.django_db
def test_atualiza_despesa_sem_person(client):
    Expense.objects.create(description='Livro', value=90)

    payload = dict(
        description='Livro de Python',
        value=50
    )

    response = client.patch('/api/v1/expenses/1', payload, content_type='application/json')

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_atualiza_despesa_sem_person_e_sem_value(client):
    Expense.objects.create(description='Livro', value=90)

    payload = dict(
        description='Livro de Python'
    )

    response = client.patch('/api/v1/expenses/1', payload, content_type='application/json')

    assert response.status_code == HTTPStatus.OK
```

Como funciona:

* `@pytest.mark.django_db` libera o acesso ao banco de testes (cada teste roda numa transação desfeita no final).
* `client` é a fixture do pytest-django com o cliente de testes do Django.
* O primeiro teste cria uma despesa sem pessoa e manda um `PATCH` só com `description` e `value`.
* O segundo manda apenas `description`, sem `person_id` e sem `value`, que são obrigatórios no schema original.
* O `content_type='application/json'` é necessário para o cliente serializar o dicionário como JSON.

Rode:

```bash
pytest
# ou, com mais detalhes e permitindo parar em breakpoint():
pytest -vv -s
```

Os dois testes passam. Sem o `PatchDict`, ambos falhariam com status 422, porque nenhum deles envia `person_id`.

Duas melhorias que ficam como lição de casa:

* em vez de fixar o id `1` na URL, guarde a despesa criada (`expense = Expense.objects.create(...)`) e use `f'/api/v1/expenses/{expense.pk}'`;
* confira também o JSON da resposta e o registro no banco, por exemplo `expense.refresh_from_db()` seguido de `assert expense.description == 'Livro de Python'` e `assert expense.value == 90` no segundo teste, provando que o valor não enviado foi mantido.

## Cuidados

O `PatchDict` aceita qualquer subconjunto de campos, então ele não avisa se o cliente esqueceu um campo que deveria ter mandado. Também deixa alterar campos sensíveis com facilidade: trocar a pessoa ligada a uma despesa, por exemplo, é só enviar outro `person_id`. Use com consciência do que a rota permite editar e, se necessário, restrinja o schema de entrada aos campos que realmente podem mudar.

## Resumo

* `PUT` substitui o recurso; `PATCH` altera só o que foi enviado.
* No Django Ninja 1.3.0, `PatchDict[Schema]` torna todos os campos opcionais e entrega um dicionário só com o que veio na requisição.
* Percorra `payload.items()` com `setattr` e salve a instância.
* Garanta o comportamento com testes que mandam payloads parciais.

Documentação do Django Ninja: [https://django-ninja.dev/](https://django-ninja.dev/)

### Capítulos

* 00:00 Intro
* 01:24 Clonando e rodando o projeto
* 04:33 PatchDict
* 06:07 pytest
