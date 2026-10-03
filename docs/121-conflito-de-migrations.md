# Como resolver conflito de migrations no Django

Publicado em 03/10/2026.

<a href="https://youtu.be/OypqG84JKHQ">
    <img src="../.gitbook/assets/youtube.png">
</a>

Documentação: [https://docs.djangoproject.com/en/stable/topics/migrations/#version-control](https://docs.djangoproject.com/en/stable/topics/migrations/#version-control)

Dois times, duas branches, e cada uma criou a sua migration `0012` no mesmo app. O git mesclou sem reclamar; quem reclamou foi o Django, no `migrate`:

```
Conflicting migrations detected; multiple leaf nodes in the migration graph
```

## Não renomeie

O conserto "óbvio" (renomear a migration para `0013`) é o errado. Migration publicada é imutável: o nome é a chave na tabela `django_migrations`. Renomeando, a mesma migration passa a ter dois nomes.

## O jeito certo: --merge

```
git checkout develop
git merge feature/archive-cancelled-orders
python manage.py makemigrations sales --merge --name merge_order_discount_and_archive_cancelled
python manage.py makemigrations sales --check --dry-run
python manage.py migrate sales --plan
pytest sales/tests
python manage.py migrate sales
```

A migration de merge tem as duas folhas em `dependencies` e `operations` vazio: ela só une o grafo.

## Um teste para pegar o próximo conflito

Coloque na suíte um teste com `MigrationLoader` e `detect_conflicts()`: o próximo conflito aparece nos testes, e não no deploy.

## Short

* [Conflito de migrations no Django: não renomeie!](https://youtube.com/shorts/7rDSpRgUq3k) (03/10/2026)
