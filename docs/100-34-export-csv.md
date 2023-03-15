# Exportando CSV

## Exportando CSV

```python
import csv

with open('/tmp/products_out.csv', 'w') as f:
    csv_writer = csv.writer(f)

    csv_writer.writerow(['title', 'price'])
    for product in Product.objects.all():
        csv_writer.writerow([product.title, product.price])
```

## Exportando CSV pelo Admin

Use o [django-import-export](https://django-import-export.readthedocs.io/en/latest/)
# Exportando CSV
