# Django Ninja 1.3.0 - PatchDict

Publicado em 12/11/2024.

<a href="https://youtu.be/_k-Iu96oL4c">
    <img src="../.gitbook/assets/youtube.png">
</a>

Release: [https://github.com/vitalik/django-ninja/releases/tag/v1.3.0](https://github.com/vitalik/django-ninja/releases/tag/v1.3.0)

Github do projeto: [https://github.com/rg3915/alpinejs-django-ninja-crud](https://github.com/rg3915/alpinejs-django-ninja-crud)

## PUT x PATCH

* **PUT** substitui o recurso inteiro.
* **PATCH** altera só os campos enviados (update parcial).

## PatchDict

No Django Ninja 1.3.0, use `PatchDict[SeuSchema]` no payload do endpoint PATCH. Assim você envia só os campos que quer mudar, sem erro de campo obrigatório.

```python
# backend/expense/api.py
from django.shortcuts import get_object_or_404
from ninja import PatchDict, Router

from .models import Expense

router = Router(tags=['Expenses'])


@router.patch('expenses/{pk}', response=ExpenseSchema)
def update_expense(request, pk: int, payload: PatchDict[ExpenseCreateSchema]):
    instance = get_object_or_404(Expense, pk=pk)

    for attr, value in payload.items():
        setattr(instance, attr, value)

    instance.save()
    return instance
```

## Teste

Update parcial precisa de teste: com **pytest-django**, crie um registro, mande um PATCH com só parte dos campos e confira o status e os valores.

### Capítulos

* 00:00 Intro
* 01:24 Clonando e rodando o projeto
* 04:33 PatchDict
* 06:07 pytest
