# Dica 31 - Importando CSV com Pandas

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, pandas 1.5.3 (com numpy 1.24.2) e Jupyter Notebook.
{: .versoes }

<a href="https://youtu.be/xQIIaUrxUzY">
    <img src="../.gitbook/assets/youtube.png">
</a>

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

Documentação do pandas: [https://pandas.pydata.org/](https://pandas.pydata.org/)

Nas dicas [29](095-29-import-csv.md) e [30](096-30-import-csv-inmemoryuploadedfile.md) lemos o CSV de produtos com o módulo `csv` da biblioteca padrão. Agora vamos ler o mesmo arquivo com o **pandas**, que carrega o CSV inteiro num `DataFrame` (uma tabela em memória) com uma única linha, e depois gravar os produtos no banco do Django com `bulk_create`. Tudo é feito interativamente, num Jupyter Notebook com o shell do Django.

Para uma comparação de desempenho entre pandas, Dask e datatable na leitura de CSV, a versão antiga desta página indicava o artigo "Pandas vs Dask vs Datatable: A Performance Comparison for Processing CSV Files", do Towards Data Science (o link não está mais no ar).

## Pré-requisitos

* O projeto das dicas anteriores, com o model `Product` (campos `title`, `unique=True`, e `price`, um `DecimalField`).
* O arquivo `/tmp/products.csv` com 100 produtos (colunas `title` e `price`), gerado pelo script `backend/product/gen_products.py` com o faker-commerce (dicas [28](094-28-faker-commerce.md) e [29](095-29-import-csv.md)).
* O django-extensions instalado (ele fornece o `shell_plus`) e o Jupyter Notebook. A instalação do Jupyter não aparece no vídeo; se você não tiver, instale com `pip install notebook`.

## Instalação

```bash
pip install pandas
pip freeze | grep pandas >> requirements.txt
```

No vídeo o pandas já estava instalado, e o `pip` mostra as versões:

```
Requirement already satisfied: pandas in ./.venv/lib/python3.10/site-packages (1.5.3)
Requirement already satisfied: numpy>=1.21.0 in ./.venv/lib/python3.10/site-packages (from pandas) (1.24.2)
Requirement already satisfied: pytz>=2020.1 in ./.venv/lib/python3.10/site-packages (from pandas) (2022.7.1)
Requirement already satisfied: python-dateutil>=2.8.1 in ./.venv/lib/python3.10/site-packages (from pandas) (2.8.2)
Requirement already satisfied: six>=1.5 in ./.venv/lib/python3.10/site-packages (from python-dateutil>=2.8.1->pandas) (1.16.0)
```

E no `requirements.txt` fica `pandas==1.5.3`.

## Abrindo o notebook com o shell do Django

```bash
python manage.py shell_plus --notebook
```

O Jupyter abre no navegador. No canto direito, clique em **New** e escolha o kernel **Django Shell-Plus**. Com esse kernel, o notebook já vem com o Django configurado e com os models importados automaticamente (por isso usamos `Product` abaixo sem importar).

## Lendo o CSV com o pandas

Cada bloco abaixo é uma célula do notebook (execute com Shift+Enter).

```python
import pandas as pd
```

```python
df = pd.read_csv('/tmp/products.csv')
```

```python
df
```

O notebook mostra o `DataFrame` (o começo e o fim, com `...` no meio):

```
                             title  price
0                   Table 95d9d2f9  99.73
1                  Gloves 511bae99  89.01
2          Gorgeous Shoes eeb71af3  51.24
3      Generic Cotton Car 38dbcb9c  83.57
4           Cotton Towels 4d6326c3  32.99
..                             ...    ...
95               Computer f338a397  62.97
96                    Car 40ddaeab  74.68
97  Ergonomic Wooden Soap fde2ecb5  58.15
98       For repair Bacon 1e9d3dca   3.55
99          Gorgeous Ball e51b0ec6  44.38

[100 rows x 2 columns]
```

(No notebook a saída aparece como uma tabela HTML, com a linha "100 rows × 2 columns" no fim.)

Com o `DataFrame` em mãos, é fácil fazer contas sobre os dados. Por exemplo, o maior e o menor valor:

```python
df.max()
```

```
title    Wooden Table 82fbb9a1
price                    99.73
dtype: object
```

```python
df.min()
```

```
title    Awesome Hat eebc1fde
price                    1.37
dtype: object
```

Repare que `max()` e `min()` calculam **cada coluna separadamente**: o preço é o maior (ou menor) da coluna `price`, e o título é o último (ou primeiro) em ordem alfabética, e não necessariamente o título do produto mais caro (ou mais barato). Para pegar a linha do produto mais caro, use `df.loc[df['price'].idxmax()]`.

## Salvando no banco

Primeiro, garantimos que a tabela está vazia (o `title` é único, então importar duas vezes o mesmo arquivo daria erro):

```python
Product.objects.all().delete()
```

Depois, definimos a mesma função `save_data` das dicas anteriores, que monta os objetos `Product` e grava todos de uma vez com `bulk_create`:

```python
def save_data(data):
    '''
    Salva os dados no banco.
    '''
    aux = []
    for item in data:
        title = item.get('title')
        price = item.get('price')
        obj = Product(
            title=title,
            price=price,
        )
        aux.append(obj)

    Product.objects.bulk_create(aux)
```

Agora transformamos cada linha do `DataFrame` num dicionário. O `df.itertuples()` percorre as linhas devolvendo uma *namedtuple* para cada uma, então acessamos as colunas como atributos (`row.title`, `row.price`):

```python
data = []
```

```python
for row in df.itertuples():
    _dict = dict(title=row.title, price=row.price)
    data.append(_dict)
```

```python
data
```

```
[{'title': 'Table 95d9d2f9', 'price': 99.73},
 {'title': 'Gloves 511bae99', 'price': 89.01},
 ...
 {'title': 'For repair Bacon 1e9d3dca', 'price': 3.55},
 {'title': 'Gorgeous Ball e51b0ec6', 'price': 44.38}]
```

Atenção ao nome da chave: tem que ser `price`, igual ao `item.get('price')` do `save_data`. No vídeo foi digitado `pricee=row.price` por engano (a saída de `data` mostra `'pricee': 99.73` etc., e a correção "price" aparece escrita na tela, na edição do vídeo). Com a chave errada, o `item.get('price')` devolve `None` e os produtos são gravados sem preço; com `price`, como acima, o preço é gravado normalmente.

Por fim, salvamos e conferimos:

```python
save_data(data)
```

```python
Product.objects.all().count()
```

```
100
```

Os 100 produtos foram importados com o pandas. Atualizando a lista de produtos no navegador, eles aparecem lá.

## Conclusão

Com o pandas, a leitura do CSV é uma linha (`pd.read_csv`), e o `DataFrame` ainda permite explorar os dados (`max`, `min` etc.) antes de gravar. A gravação no banco continua igual: uma lista de dicionários passada para o `save_data` com `bulk_create`. Na [próxima dica](098-32-import-csv-dask.md) fazemos o mesmo com o Dask.
