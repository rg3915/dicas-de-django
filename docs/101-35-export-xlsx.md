# Dica 35 - Exportando XLSX mais rápido com pyexcelerate

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, PyExcelerate 0.10.0 e Jupyter Notebook.
{: .versoes }

<a href="https://youtu.be/0DuLOvnJTMw">
    <img src="../.gitbook/assets/youtube.png">
</a>

[https://pypi.org/project/PyExcelerate/](https://pypi.org/project/PyExcelerate/)

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

Na [dica anterior](100-34-export-csv.md) exportamos os produtos para CSV. Agora vamos exportar para uma planilha do Excel (`.xlsx`) com o **PyExcelerate**, uma biblioteca feita para escrever arquivos XLSX rapidamente; dizem que ela é mais rápida que o OpenPyXL para gravar muitos dados.

## Pré-requisitos

* O projeto das dicas anteriores, com produtos cadastrados no model `Product` (campos `title` e `price`).
* O Jupyter Notebook com o shell do Django, como na [dica 31](097-31-import-csv-pandas.md):

```bash
python manage.py shell_plus --notebook
```

## Instalação

```bash
pip install pyexcelerate
pip freeze | grep pyexcelerate >> requirements.txt
```

```
Requirement already satisfied: pyexcelerate in ./.venv/lib/python3.10/site-packages (0.10.0)
Requirement already satisfied: six>=1.4.0 in ./.venv/lib/python3.10/site-packages (from pyexcelerate) (1.16.0)
Requirement already satisfied: Jinja2 in ./.venv/lib/python3.10/site-packages (from pyexcelerate) (3.1.2)
Requirement already satisfied: MarkupSafe>=2.0 in ./.venv/lib/python3.10/site-packages (from Jinja2->pyexcelerate) (2.1.1)
```

Atenção: o `pip freeze` lista o pacote com letras maiúsculas (`PyExcelerate==0.10.0`), então o `grep pyexcelerate` não encontra nada e o `requirements.txt` não é atualizado. No vídeo a linha foi acrescentada à mão. Use `grep -i` para ignorar maiúsculas e minúsculas:

```bash
pip freeze | grep -i pyexcelerate >> requirements.txt
```

O `requirements.txt` termina assim:

```
# requirements.txt
...
faker-commerce==1.0.3
django-import-export==3.1.0
pandas==1.5.3
dask==2023.3.1
PyExcelerate==0.10.0
```

## Exportando XLSX

No Jupyter, clique em **New** e escolha o kernel **Django Shell-Plus** (os models, como `Product`, já vêm importados). Cada bloco abaixo é uma célula.

```python
from pyexcelerate import Workbook
```

O PyExcelerate grava uma planilha a partir de uma lista de linhas, em que cada linha é uma tupla (ou lista) com os valores das colunas. Então montamos essa lista com uma list comprehension, uma tupla `(título, preço)` para cada produto:

```python
data = [(product.title, product.price) for product in Product.objects.all()]
```

```python
data
```

```
[('Awesome Hat eebc1fde', Decimal('23.92')),
 ('Bacon f83adfb0', Decimal('5.12')),
 ('Ball 387f27f3', Decimal('92.36')),
 ('Car 40ddaeab', Decimal('74.68')),
 ...
 ('book', Decimal('120.00')),
 ('iphone', Decimal('7000.00')),
 ('notebook', Decimal('6500.00')),
 ('pc game', Decimal('9000.00')),
 ('television', Decimal('4500.00'))]
```

(No vídeo o banco tinha os 100 produtos do CSV e os 5 do XLSX importados na [dica 33](099-33-import-xlsx.md).)

Falta o cabeçalho. Queremos que a primeira linha da planilha seja `title` e `price`, então inserimos uma tupla na posição `0` da lista com `insert`:

```python
data.insert(0, ('title', 'price'))  # Insere uma tupla no começo da lista.
```

```python
data
```

```
[('title', 'price'),
 ('Awesome Hat eebc1fde', Decimal('23.92')),
 ('Bacon f83adfb0', Decimal('5.12')),
 ...
```

Agora criamos a pasta de trabalho, uma aba com os dados e salvamos o arquivo:

```python
wb = Workbook()
```

```python
wb.new_sheet("sheet name", data=data)
```

```
<pyexcelerate.Worksheet.Worksheet at 0x7f2e22e47d90>
```

```python
wb.save("/tmp/products_out.xlsx")
```

* `Workbook()` cria uma planilha nova, em memória;
* `new_sheet("sheet name", data=data)` cria uma aba chamada `sheet name` e preenche as células com a lista: cada tupla vira uma linha, cada valor uma coluna;
* `save` grava o arquivo `.xlsx`.

Os valores `Decimal` do `price` são gravados como números. Abrindo `/tmp/products_out.xlsx` no LibreOffice Calc (ou no Excel), temos a coluna A com os títulos e a coluna B com os preços, terminando com os produtos book (120), iphone (7000), notebook (6500), pc game (9000) e television (4500).

O código completo, em uma célula só:

```python
from pyexcelerate import Workbook

data = [(product.title, product.price) for product in Product.objects.all()]
data.insert(0, ('title', 'price'))  # Insere uma tupla no começo da lista.

wb = Workbook()
wb.new_sheet("sheet name", data=data)
wb.save("/tmp/products_out.xlsx")
```

## Conclusão

Com o PyExcelerate, exportar para XLSX é montar uma lista de tuplas (com o cabeçalho na posição 0) e passar para `new_sheet`. Na [próxima dica](102-36-export-csv-xlsx-front.md) levamos a exportação de CSV e XLSX para o front do projeto.
