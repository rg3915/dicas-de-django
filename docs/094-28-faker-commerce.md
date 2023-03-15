# Dica 28 - Gerando dados aleatórios com Faker - faker-commerce

VIDEO EM BREVE.

Crie um arquivo `gen_products.py` em `backend/product`.

```
touch backend/product/gen_products.py
```

E instale

```
pip install faker-commerce

pip freeze | grep faker-commerce >> requirements.txt
```

```python
# gen_products.py
'''
Gera 100 produtos (título e preço) randomicamente com faker-commerce.

pip install faker-commerce
'''

import csv
import random
import uuid

import faker_commerce
from faker import Faker

fake = Faker()
fake.add_provider(faker_commerce.Provider)


QUANTITY = 100


with open('/tmp/products.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['title', 'price'])
    for _ in range(QUANTITY):
        short_uuid = uuid.uuid4().hex[:8]
        title = f'{fake.ecommerce_name()} {short_uuid}'
        price = round(random.uniform(1, 100), 2)
        writer.writerow([title, price])

```

E finalmente rodamos

```
python backend/product/gen_products.py
```