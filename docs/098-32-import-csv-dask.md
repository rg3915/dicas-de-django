# Dica 32 - Importando CSV com Dask

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10, Dask 2023.3.1 (`dask[dataframe]`), pandas 1.5.3 e Jupyter Notebook.
{: .versoes }

<a href="https://youtu.be/_gIY9fWxYLw">
    <img src="../.gitbook/assets/youtube.png">
</a>

Código: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

Documentação do Dask: [https://www.dask.org/](https://www.dask.org/)

O Dask é uma biblioteca Python para trabalhar com conjuntos de dados que não cabem na memória do computador: ele divide os dados em partes (partições) e processa essas partes em paralelo, sem que você precise dividir os dados manualmente. O `dask.dataframe` imita a API do pandas, então o código fica muito parecido com o da [dica anterior](097-31-import-csv-pandas.md). Neste tutorial vamos ler o mesmo CSV de produtos com o Dask e gravar os dados no banco do Django.

Para uma comparação de desempenho entre pandas, Dask e datatable na leitura de CSV, a versão antiga desta página indicava o artigo "Pandas vs Dask vs Datatable: A Performance Comparison for Processing CSV Files", do Towards Data Science (o link não está mais no ar).

## Pré-requisitos

* O projeto das dicas anteriores, com o model `Product` (campos `title`, `unique=True`, e `price`).
* O arquivo `/tmp/products.csv` com 100 produtos (colunas `title` e `price`), gerado com o faker-commerce (dicas [28](094-28-faker-commerce.md) e [29](095-29-import-csv.md)).
* O Jupyter Notebook rodando com o shell do Django, como na [dica 31](097-31-import-csv-pandas.md):

```bash
python manage.py shell_plus --notebook
```

## Instalação

O Dask é dividido em "extras"; para usar o `dask.dataframe` instale com o extra `dataframe` (ele traz o pandas junto):

```bash
python -m pip install "dask[dataframe]"
pip freeze | grep dask >> requirements.txt
```

No `requirements.txt` do projeto ficou `dask==2023.3.1`.

Depois de instalar, no Jupyter clique em **New** e escolha o kernel **Django Shell-Plus**, para abrir um notebook novo com o Django carregado (os models, como `Product`, já vêm importados).

## Lendo o CSV com o Dask

No notebook, digite (cada bloco é uma célula):

```python
import dask.dataframe as dd
```

```python
df = dd.read_csv('/tmp/products.csv')
```

Diferente do pandas, o `dd.read_csv` é **preguiçoso** (*lazy*): ele não carrega o arquivo na hora, só monta o plano de leitura. Se você digitar só `df`, o notebook mostra apenas a estrutura do DataFrame (colunas, tipos e número de partições), e não os dados. Para ver os dados, usamos `head()` e `tail()`, que leem só o pedaço necessário:

```python
df.head()
```

```
                             title  price
0                   Table 95d9d2f9  99.73
1                  Gloves 511bae99  89.01
2          Gorgeous Shoes eeb71af3  51.24
3      Generic Cotton Car 38dbcb9c  83.57
4           Cotton Towels 4d6326c3  32.99
```

```python
df.tail()
```

```
                             title  price
95               Computer f338a397  62.97
96                    Car 40ddaeab  74.68
97  Ergonomic Wooden Soap fde2ecb5  58.15
98       For repair Bacon 1e9d3dca   3.55
99          Gorgeous Ball e51b0ec6  44.38
```

## Salvando no banco

Garantimos que a tabela está vazia (no vídeo ainda havia os 100 produtos importados com o pandas na dica anterior):

```python
Product.objects.all().delete()
```

```
(100, {'product.Product': 100})
```

A função `save_data` é a mesma das dicas anteriores:

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

Montamos a lista de dicionários. Aqui usamos `df.iterrows()`, que devolve, para cada linha, o índice e a linha (uma `Series` do pandas, cujas colunas também podem ser lidas como atributos):

```python
data = []

for index, row in df.iterrows():
    _dict = dict(title=row.title, price=row.price)
    data.append(_dict)
```

Ao percorrer as linhas, o Dask lê as partições do arquivo uma a uma.

Por fim, salvamos e conferimos a quantidade:

```python
save_data(data)
```

```python
Product.objects.all().count()
```

```
100
```

Os 100 produtos foram cadastrados com o Dask.

## Conclusão

O código com o Dask é praticamente igual ao do pandas: `dd.read_csv` no lugar de `pd.read_csv`, e `head()`/`tail()` para espiar os dados, já que o DataFrame do Dask só é calculado quando necessário. Para um CSV de 100 linhas não faz diferença, mas para arquivos muito grandes, que não cabem na memória, o Dask é a ferramenta indicada.
