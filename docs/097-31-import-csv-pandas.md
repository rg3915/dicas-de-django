# Dica 31 - Importando CSV com Pandas

VIDEO EM BREVE.

[https://towardsdatascience.com/pandas-vs-dask-vs-datatable-a-performance-comparison-for-processing-csv-files-3b0e0e98215e](https://towardsdatascience.com/pandas-vs-dask-vs-datatable-a-performance-comparison-for-processing-csv-files-3b0e0e98215e)


```
pip install pandas
pip freeze | grep pandas >> requirements.txt

python manage.py shell_plus --notebook
```

```python
import pandas as pd

df = pd.read_csv('/tmp/products.csv')

df

df.max()

df.min()

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

for row in df.itertuples():
    _dict = dict(title=row.title, price=row.price)
    data.append(_dict)

data

save_data(data)

Product.objects.all().count()
```


