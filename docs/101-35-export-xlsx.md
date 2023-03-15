# Exportando XLSX mais rápido com pyexcelerate

[https://pypi.org/project/PyExcelerate/](https://pypi.org/project/PyExcelerate/)

```
pip install pyexcelerate
pip freeze | grep pyexcelerate >> requirements.txt
```

```python
from pyexcelerate import Workbook

data = [(product.title, product.price) for product in Product.objects.all()]
data.insert(0, ('title', 'price'))  # Insere uma tupla no começo da lista.

data

wb = Workbook()
wb.new_sheet("sheet name", data=data)
wb.save("/tmp/products_out.xlsx")
```
