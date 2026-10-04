# Dica 34 - Exportando CSV

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, django-import-export 3.1.0 e Jupyter Notebook.
{: .versoes }

<a href="https://youtu.be/eS4U_kBNWu8">
    <img src="../.gitbook/assets/youtube.png">
</a>

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

Depois de várias dicas importando dados, agora vamos fazer o caminho inverso: **exportar** os produtos do banco para um arquivo CSV. Primeiro com o módulo `csv` da biblioteca padrão do Python, no Jupyter Notebook; depois pelo painel de admin, com o django-import-export.

## Pré-requisitos

* O projeto das dicas anteriores, com produtos cadastrados no model `Product` (campos `title` e `price`).
* O Jupyter Notebook com o shell do Django, como na [dica 31](097-31-import-csv-pandas.md):

```bash
python manage.py shell_plus --notebook
```

* Para a exportação pelo admin, o django-import-export configurado como na [dica 30](096-30-import-csv-inmemoryuploadedfile.md#importando-csv-pelo-admin-com-django-import-export).

## Exportando CSV

No Jupyter, clique em **New** e escolha o kernel **Django Shell-Plus** (os models, como `Product`, já vêm importados). Em duas células, digite:

```python
import csv
```

```python
with open('/tmp/products_out.csv', 'w') as f:
    csv_writer = csv.writer(f)

    csv_writer.writerow(['title', 'price'])
    for product in Product.objects.all():
        csv_writer.writerow([product.title, product.price])
```

O que acontece:

* `open('/tmp/products_out.csv', 'w')` cria (ou sobrescreve) o arquivo de saída, em modo de escrita;
* `csv.writer(f)` cria um "escritor" de CSV sobre esse arquivo; ele cuida do separador (vírgula) e de colocar aspas quando um valor tiver vírgula;
* a primeira chamada de `writerow` grava o cabeçalho;
* depois, para cada produto, `writerow` grava uma linha com o título e o preço.

Abrindo o arquivo `/tmp/products_out.csv` num editor, temos:

```
title,price
Awesome Hat eebc1fde,23.92
Bacon f83adfb0,5.12
Ball 387f27f3,92.36
Car 40ddaeab,74.68
Cheese 850e0db1,10.88
Cheese d10c8b0b,54.45
Cheese f8e50b73,83.86
Chicken 5163ecff,36.55
Chips 1b002d9c,62.23
Computer 421d44fe,59.80
...
```

Os produtos saem em ordem alfabética por causa do `ordering = ('title',)` do model, e o preço sai com duas casas decimais porque é um `DecimalField`.

## Exportando CSV pelo Admin

Use o [django-import-export](https://django-import-export.readthedocs.io/en/latest/). Como ele já foi configurado na [dica 30](096-30-import-csv-inmemoryuploadedfile.md#importando-csv-pelo-admin-com-django-import-export) (com o `ProductAdmin` herdando de `ImportExportModelAdmin`), não é preciso escrever mais nada:

1. no admin, vá na lista de produtos (`/admin/product/product/`) e clique em **Exportar**;
2. em **Formato**, escolha **csv**;
3. clique em **Enviar**.

O navegador baixa um arquivo com o nome do model e a data, no vídeo `Product-2023-03-15.csv`. A diferença é que o django-import-export exporta **todos os campos** do model:

```
id,created,modified,title,description,price,category,slug
104849,2023-03-15 06:11:01,2023-03-15 06:11:01,Awesome Hat eebc1fde,,23.92,,
104839,2023-03-15 06:11:01,2023-03-15 06:11:01,Bacon f83adfb0,,5.12,,
104861,2023-03-15 06:11:01,2023-03-15 06:11:01,Ball 387f27f3,,92.36,,
...
```

Se quiser exportar só alguns campos, basta dizer quais no `Meta` do resource, por exemplo `fields = ('title', 'price')`; é simples de resolver.

No código final do repositório, o `ProductAdmin` também herda de `ExportActionModelAdmin`, o que acrescenta a ação "Exportar produtos selecionados" na lista do admin, para exportar só os produtos marcados:

```python
# backend/product/admin.py
from import_export.admin import ExportActionModelAdmin, ImportExportModelAdmin

...


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, ExportActionModelAdmin):
    resource_classes = [ProductResource]
    ...
```

## Conclusão

Exportar CSV com Python é simples: `open` + `csv.writer` + `writerow` para o cabeçalho e para cada registro. E, pelo admin, o django-import-export faz isso com dois cliques. Na [próxima dica](101-35-export-xlsx.md) exportamos para XLSX.
