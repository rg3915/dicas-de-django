# Dica 32 - Importando CSV com Dask

VIDEO EM BREVE.

[https://towardsdatascience.com/pandas-vs-dask-vs-datatable-a-performance-comparison-for-processing-csv-files-3b0e0e98215e](https://towardsdatascience.com/pandas-vs-dask-vs-datatable-a-performance-comparison-for-processing-csv-files-3b0e0e98215e)

```
python -m pip install "dask[dataframe]"
pip freeze | grep dask >> requirements.txt
```

No Notebook digite

```python
import dask.dataframe as dd

df = dd.read_csv('/tmp/products.csv')

df.head()

df.tail()

Product.objects.all().delete()

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

data = []

for index, row in df.iterrows():
    _dict = dict(title=row.title, price=row.price)
    data.append(_dict)

save_data(data)

Product.objects.all().count()
```
