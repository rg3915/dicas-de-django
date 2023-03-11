# Dica 27 - Signals

Doc: [https://docs.djangoproject.com/en/4.1/topics/signals/](https://docs.djangoproject.com/en/4.1/topics/signals/)

[https://docs.djangoproject.com/en/4.1/ref/signals/](https://docs.djangoproject.com/en/4.1/ref/signals/)

## Problema

Suponha que você queira enviar um e-mail de boas-vindas para um novo usuário.

Onde você faria isso? Na views?

E se você usasse mais views para fazer esse cadastro?

Você criaria uma função! Hum... pode ser.

Mas e se você cadastra-se um usuário pelo Admin?

**Outra situação:**

Suponha que você não tenha acesso ao model `User`.

Neste projeto nós temos acesso, mas no Django padrão nós não teríamos acesso.

Como você faria para, tanto na views, como no Admin, e até no shell do Django, saber se um model do `User` foi criado ou modificado?

Para isso nós temos o signals.


## O que é um Signal?

No Django, os "signals" são uma forma de enviar sinais ou notificações quando ocorre uma determinada ação no banco de dados ou em algum modelo específico. Esses sinais podem ser usados para executar ações adicionais ou enviar notificações quando determinadas mudanças ocorrem no modelo.

Toda vez que um model é criado, ou alterado, é enviado um sinal para a aplicação. E este sinal pode fazer alguma coisa.

### Exemplos

* Ao criar um novo **usuário**, criar um `Profile` pra ele.
* Ao criar um novo **usuário**, enviar um e-mail pra ele.
* Ao criar um novo **produto**, definir um slug automaticamente.


## Model Profile

Considere o model `Profile`.

```python
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        verbose_name='usuário'
    )
    birthday = models.DateField('data de nascimento', null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    rg = models.CharField(max_length=10, null=True, blank=True)
    cpf = models.CharField(max_length=11, null=True, blank=True)
```

Agora vamos considerar o seguinte:

Toda vez que eu criar um **novo usuário**, eu quero automaticamente criar um `Profile` pra ele.

```python
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
```

### Detalhando um pouco mais

No terminal digite

```
python manage.py shell_plus
```

Depois

```python
from django.contrib.auth import get_user_model

User = get_user_model()

User  # aqui nós vemos que o nosso User está em backend.accounts.models.User
```

#### Exemplo 1

Se fizermos

```python
instance = User.objects.create()
```

Podemos ter os signals `pre_save` e `post_save`.

A diferença é que o `pre_save` tem o `instance`, e o `post_save` tem o `instance` e o `created`.

```python
# pre_save -> instance
instance = User.objects.create()
# post_save -> instance, created=True
```

Note também que no `pre_save` você ainda não tem o id do objeto.

#### Exemplo 2

Neste outro exemplo, usando o comando `save()`

```python
# pre_save -> instance
instance.save()
# post_save -> instance, created=False
```

A diferença aqui é que em `post_save` o `created=False`.

#### Exemplo 3

Ao deletar temos os signals `pre_delete` e `post_delete`.

#### Exemplo 4

Agora vamos ao código

```python
# accounts/models.py

from django.db.models.signals import post_save
from django.dispatch import receiver

def user_created_handler(*args, **kwargs):
    print('Usuário criado com sucesso.')

post_save.connect(user_created_handler, sender=User)
```

Ou podemos usar o decorator `receiver`.

```python
@receiver(post_save, sender=User)
def user_created_handler(*args, **kwargs):
    print('Usuário criado com sucesso.')
    print(args, kwargs)
```

Quando adicionarmos um novo usuário...

```python
from django.contrib.auth import get_user_model

User = get_user_model()

User.objects.create_user(email='user01@email.com')

() {'signal': <django.db.models.signals.ModelSignal object at 0x7fa6a116b490>, 'sender': <class 'backend.accounts.models.User'>, 'instance': <User: user01@email.com>, 'created': True, 'update_fields': None, 'raw': False, 'using': 'default'}
```

Veja o

```python
'instance': <User: user01@email.com>, 'created': True
```

#### Exemplo 5

Podemos acrescentar mais parâmetros como

```python
@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, *args, **kwargs):
    print('Usuário criado com sucesso.')
    # print(args, kwargs)
    if created:
        print('Envia e-mail para', instance.email)
    else:
        print(instance.email, 'foi salvo.')
```

Salve alguns usuários no Admin e veja o resultado no terminal.

#### Exemplo 6

Agora veremos o `pre_save`.

```python
@receiver(pre_save, sender=User)
def user_pre_save_handler(sender, instance, *args, **kwargs):
    print(instance.email, instance.id)  # None
    # NÃO FAÇA ISSO -> instance.save()  # Loop infinito
```

Teste pelo Admin.

#### Exemplo 7 - Profile

Agora já conseguimos entender o signal do `Profile`.

```python
# accounts/models.py
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
```

#### Exemplo 8 - Envio de e-mail

```python
# accounts/models.py
@receiver(post_save, sender=User)
def send_email_on_user_creation(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'New user created',
            f'A new user with email {instance.email} has been created.',
            'from@example.com',
            ['to@example.com'],
            fail_silently=False,
        )
```

## Model Product

Em `Product` vamos adicionar um `slug`.

```python
# product/models.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify


class Product(TimeStampedModel):
    ...
    slug = models.SlugField(blank=True, null=True)


@receiver(pre_save, sender=Product)
def product_pre_save(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)
```

## Bonus: colocando o Signals num arquivo separado

```
touch backend/product/signals.py
```

```python
# product/signals.py
from django.utils.text import slugify


def product_pre_save(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)
```

Agora precisamos editar o arquivo `apps.py`.

```python
# product/apps.py
class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myproject.product'

    def ready(self):
        from django.db.models.signals import pre_save

        from .models import Product
        from .signals import product_pre_save

        pre_save.connect(product_pre_save, sender=Product)
```

Para finalizar vamos colocar o `slug` como `read_only` no Admin.

```python
# product/admin.py

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    ...
    list_display = ('__str__', 'slug', 'category')
    readonly_fields = ('slug',)
    ...
```
