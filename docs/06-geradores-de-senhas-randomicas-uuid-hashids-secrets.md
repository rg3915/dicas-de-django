# 6 - Geradores de senhas randômicas - uuid, hashids, secrets

<a href="https://youtu.be/-3znAePkMqY">
    <img src="../.gitbook/assets/youtube.png">
</a>

## 6.1 - uuid

https://docs.python.org/3/library/uuid.html

```python
import uuid

uuid.uuid4()

uuid.uuid4().hex
```

```python
# models.py
import uuid

from django.db import models


class UuidModel(models.Model):
    slug = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True

class Category(UuidModel):
    title = models.CharField('título', max_length=50, unique=True)
    ...
```

## 6.2 - shortuuid

<a href="https://youtu.be/qsRefchlXlo">
    <img src="../.gitbook/assets/youtube.png">
</a>


https://pypi.org/project/shortuuid/

```
pip install shortuuid
```

```python
>>> import shortuuid
>>> 
>>> shortuuid.uuid()
'823MMBZx7LNEnnPBtCAorG'
>>> 
>>> shortuuid.uuid(name='example.com')
'exu3DTbj2ncsn9tLdLWspw'
>>> 
>>> shortuuid.ShortUUID().random(length=22)
'4CHN7TshKtrVnW4KLgVMhY'
>>> 
>>> shortuuid.set_alphabet('regis')
>>> shortuuid.uuid()
'gerigigiesreissgisrsggrrseieereggierrgreriissreiiisiegrr'
>>> 
```

## 6.3 - hashids

https://gist.github.com/rg3915/4684721a603cf6d0dd3b9495744482fe

https://pypi.org/project/hashids/

```
pip install hashids
```

```python
from hashids import Hashids

hashids = Hashids()

>>> hashids.encode(42)
'9x'
>>> hashids.decode('9x')
(42,)
>>> hashids.encode(665190)
'k7qWJ'
>>> hashids.decode('k7qWJ')
(665190,)
>>> hashids.encode(1122, 4200, 32665)
'ELmhW0mFD7o'
>>> hashids.decode('ELmhW0mFD7o')
(1122, 4200, 32665)
>>> hashids = Hashids(alphabet='abcdefghijklmnopqrstuvwxyz1234567890', min_length=22)
>>> for i in range(10): hashids.encode(i)
... 
'9xkwnvoj3ejwgp6481y5mq'
'ml6kz731jdkoe524rxn0yq'
'kwp7yx456gl9g91lm23v8n'
'0qr6jxo9memje214w8zlvp'
'9poy2jq1xdn0e037nwv4zl'
'nz97pw01jgo5el24yrxv6m'
'q4pkmy631epjenrxv70w5l'
'n97kyw8q0dq9eo143z2x6v'
'x7n4zl0pkgr4d6o3vq92wy'
'6y27mjnzkev3d3549vq0xl'
>>> 
```

### django-hashid-field

https://pypi.org/project/django-hashid-field/

```
pip install django-hashid-field==3.1.3
```

```python
# models.py
from hashid_field import HashidAutoField


class Article(models.Model):
    id = HashidAutoField(primary_key=True)
    ...
```


```python
# python manage.py shell_plus
from hashid_field import Hashid

articles = Article.objects.all()
for article in articles:
    hashid = Hashid(article.id)
    print(article.id, hashid.id)
```

https://www.howtogeek.com/howto/30184/10-ways-to-generate-a-random-password-from-the-command-line/

### Gerando senhas no terminal Linux

```
date +%s | sha256sum | base64 | head -c 32 ; echo

openssl rand -base64 32

strings /dev/urandom | grep -o '[[:alnum:]]' | head -n 30 | tr -d '\n'; echo

date | md5sum
```


```
# apt install -y gpw

gpw

gpw 3 32

gpw 1 5
```

### Gerando senhas com Python

#### com random

```python
import random

chars = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
size = 8
secret_key = "".join(random.sample(chars,size))
print(secret_key)
```

#### com random e string

https://pynative.com/python-generate-random-string/

```python
# Generate a random string of specific letters only

import random
import string


def randString(length=5):
    # put your letters in the following string
    your_letters='abcdefghi'
    return ''.join((random.choice(your_letters) for i in range(length)))

print("Random String with specific letters ", randString())
print("Random String with specific letters ", randString(5))
```

#### com secrets

https://docs.python.org/3/library/secrets.html

*New in Python 3.6*

```python
import secrets

secrets.token_hex(16)

secrets.token_urlsafe(16)

url = 'https://mydomain.com/reset=' + secrets.token_urlsafe()
```

### Django

```
vim contrib/env_gen.py
```

```python
"""
Django SECRET_KEY generator.
"""
from django.utils.crypto import get_random_string

chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

CONFIG_STRING = """
DEBUG=True
SECRET_KEY=%s
ALLOWED_HOSTS=127.0.0.1, .localhost
""".strip() % get_random_string(50, chars)

print(CONFIG_STRING)

# Writing our configuration file to '.env'
with open('.env', 'w') as configfile:
    configfile.write(CONFIG_STRING)
```

```
python contrib/env_gen.py
```
