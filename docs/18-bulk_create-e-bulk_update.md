# 18 - bulk_create e bulk_update

<a href="https://youtu.be/U99VT4UwJ5k">
    <img src="../.gitbook/assets/youtube.png">
</a>


## bulk_create

O [bulk_create](https://docs.djangoproject.com/en/3.0/ref/models/querysets/#bulk-create) serve para inserir uma grande quantidade de dados num banco de forma super rápida.

Vamos usar o

`python manage.py shell_plus`

Primeiro vamos criar uns dados aleatórios

```python
import secrets
import string

N = 12
list_items = []

for i in range(100):
    res = ''.join(secrets.choice(string.ascii_lowercase) for i in range(N))
    list_items.append(res)
```

Agora vamos inserir os dados com bulk_create

```python
aux = []
for item in list_items:
    obj = Article(title=item, subtitle=item)
    aux.append(obj)

Article.objects.bulk_create(aux)
```

## bulk_update

Como o nome já diz, o [bulk_update](https://docs.djangoproject.com/en/3.0/ref/models/querysets/#bulk-update) serve para atualizar os dados.


```python
articles = Article.objects.all()
category = Category.objects.first()
for article in articles:
    article.category = category

Article.objects.bulk_update(articles, ['category'])
```
