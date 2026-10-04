# Dica 27 - Signals

**Versões usadas no vídeo:** Django 4.1.3, Python 3.10 e MailHog (via Docker).
{: .versoes }

<a href="https://youtu.be/CZ7vUBLpoZc">
    <img src="../.gitbook/assets/youtube.png">
</a>

Doc: [https://docs.djangoproject.com/en/4.1/topics/signals/](https://docs.djangoproject.com/en/4.1/topics/signals/)

[https://docs.djangoproject.com/en/4.1/ref/signals/](https://docs.djangoproject.com/en/4.1/ref/signals/)

Github: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

Neste tutorial vamos entender para que servem os **signals** do Django e usá-los em três situações reais: criar um `Profile` para cada novo usuário, enviar um e-mail quando um usuário é criado e preencher o `slug` de um produto automaticamente. No fim, vamos mover o signal para um arquivo `signals.py` separado.

## Problema

Suponha que você queira enviar um e-mail de boas-vindas para um novo usuário.

Onde você faria isso? Na views?

E se você usasse mais views para fazer esse cadastro?

Você criaria uma função! Hum... pode ser.

Mas e se você cadastrasse um usuário pelo Admin?

**Outra situação:**

Suponha que você não tenha acesso ao model `User`.

Neste projeto nós temos acesso, mas no Django padrão nós não teríamos acesso.

Como você faria para, tanto na views, como no Admin, e até no shell do Django, saber se um model do `User` foi criado ou modificado?

Para isso nós temos os signals.

## O que é um Signal?

No Django, os "signals" são uma forma de enviar sinais ou notificações quando ocorre uma determinada ação no banco de dados ou em algum modelo específico. Esses sinais podem ser usados para executar ações adicionais ou enviar notificações quando determinadas mudanças ocorrem no modelo.

Toda vez que um model é criado, ou alterado, é enviado um sinal para a aplicação. E este sinal pode fazer alguma coisa.

### Exemplos

* Ao criar um novo **usuário**, criar um `Profile` pra ele.
* Ao criar um novo **usuário**, enviar um e-mail pra ele.
* Ao criar um novo **produto**, definir um slug automaticamente.

### Os signals de model

Na [referência de signals](https://docs.djangoproject.com/en/4.1/ref/signals/) há vários: `pre_init`, `post_init`, `pre_save`, `post_save`, `pre_delete`, `post_delete`, `m2m_changed` e outros. Vamos nos concentrar no `pre_save` e no `post_save`, que são os mais usados.

**Use signals com moderação.** A própria documentação recomenda isso: o código que roda no signal fica "escondido", longe de onde a ação acontece, e fica difícil saber o que está acontecendo no projeto. Use apenas em casos especiais, como os deste tutorial.

## Pré-requisitos

Usamos o projeto do repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django), que tem:

* um `User` personalizado em `backend/accounts/models.py` (login por e-mail);
* o model `Profile`, com um `OneToOneField` para o `User`;
* a app `backend.product` com o model `Product`;
* o MailHog rodando no Docker, para receber os e-mails de teste.

## Model Profile

Considere o model `Profile`.

```python
# backend/accounts/models.py
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

    class Meta:
        ordering = ('user__first_name',)
        verbose_name = 'perfil'
        verbose_name_plural = 'perfis'

    @property
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name or ""}'.strip()

    def __str__(self):
        return self.full_name
```

Agora vamos considerar o seguinte:

Toda vez que eu criar um **novo usuário**, eu quero automaticamente criar um `Profile` pra ele.

```python
# backend/accounts/models.py
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
```

* `@receiver(post_save, sender=User)`: "toda vez que um `User` for salvo, execute a função abaixo". O `sender` é o model que envia o sinal. A posição da função no arquivo não importa, desde que fique depois dos models que ela usa.
* A função recebe `sender`, `instance` (o objeto salvo), `created` e `**kwargs`.
* Se `created` for `True`, é uma criação: criamos um `Profile` novo para o usuário. Se não, é uma atualização: salvamos o profile que já existe (`instance.profile`).

O projeto já tinha isso, dividido em dois signals, `create_user_profile` e `save_user_profile`. Para os experimentos, comentamos os dois.

### Detalhando um pouco mais

No terminal digite

```bash
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

Note também que no `pre_save` você ainda não tem o id do objeto. O id só existe no `post_save`.

#### Exemplo 2

Neste outro exemplo, usando o comando `save()`

```python
# pre_save -> instance
instance.save()
# post_save -> instance, created=False
```

A diferença aqui é que em `post_save` o `created=False`. É exatamente isso que o `if created` do `Profile` usa: criação, `created=True`; só atualização, `created=False`.

#### Exemplo 3

Ao deletar temos os signals `pre_delete` e `post_delete`.

#### Exemplo 4

Agora vamos ao código. A forma mais explícita de ligar uma função a um signal é com o método `connect`:

```python
# backend/accounts/models.py
from django.db.models.signals import post_save
from django.dispatch import receiver


def user_created_handler(*args, **kwargs):
    print('Usuário criado com sucesso.')


post_save.connect(user_created_handler, sender=User)
```

Rode o servidor, abra o Admin e cadastre um novo usuário. No terminal aparece:

```
Usuário criado com sucesso.
```

Quem enviou o sinal foi o model `User` (o `sender`), e o signal `post_save` executou a função `user_created_handler`.

Ou podemos usar o decorator `receiver`, que faz a mesma coisa sem precisar do `connect`:

```python
@receiver(post_save, sender=User)
def user_created_handler(*args, **kwargs):
    print('Usuário criado com sucesso.')
    print(args, kwargs)
```

Quando adicionarmos um novo usuário (pelo Admin, ou pelo shell)...

```python
from django.contrib.auth import get_user_model

User = get_user_model()

User.objects.create_user(email='user01@email.com')

() {'signal': <django.db.models.signals.ModelSignal object at 0x7fa6a116b490>, 'sender': <class 'backend.accounts.models.User'>, 'instance': <User: user01@email.com>, 'created': True, 'update_fields': None, 'raw': False, 'using': 'default'}
```

Veja o

```python
'sender': <class 'backend.accounts.models.User'>, 'instance': <User: user01@email.com>, 'created': True
```

Essas são as informações mais importantes que vêm no `kwargs`: quem enviou, o objeto e se ele foi criado.

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

Salve alguns usuários no Admin e veja o resultado no terminal. Ao criar um usuário:

```
Envia e-mail para kixifih@mailinator.com
```

Ao editar um usuário existente:

```
regis@mailinator.com foi salvo.
```

#### Exemplo 6

Agora veremos o `pre_save`. Ele não tem o `created`, porque o objeto ainda não foi salvo. Acrescente o `pre_save` no import:

```python
from django.db.models.signals import post_save, pre_save


@receiver(pre_save, sender=User)
def user_pre_save_handler(sender, instance, *args, **kwargs):
    print(instance.email, instance.id)  # None
    # NÃO FAÇA ISSO -> instance.save()  # Loop infinito
```

Teste pelo Admin. Ao criar um usuário, o `id` aparece como `None`: no `pre_save` o objeto ainda não foi gravado, então ainda não tem id. Essa é a diferença.

**Importante:** não chame `instance.save()` dentro do signal de save. O `save()` dispara o signal de novo, que chama o `save()` de novo... e você entra num loop infinito.

#### Exemplo 7 - Profile

Agora já conseguimos entender o signal do `Profile`.

```python
# backend/accounts/models.py
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
```

No projeto, no fim, deixamos esse exemplo comentado e voltamos a usar os dois signals que já existiam, que fazem a mesma coisa em duas funções:

```python
# backend/accounts/models.py
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
```

#### Exemplo 8 - Envio de e-mail

Como o envio de e-mail tem a ver com o `User`, e não com o `Profile`, colocamos o signal logo depois da classe `User`:

```python
# backend/accounts/models.py
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractBaseUser, PermissionsMixin):
    ...


@receiver(post_save, sender=User)
def send_email_on_user_creation(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'Novo usuário criado',
            f'Um novo usuário com email {instance.email} foi criado.',
            'from@example.com',
            ['to@example.com'],
            fail_silently=False,
        )
```

O `send_mail` recebe o assunto, a mensagem, o remetente e uma **lista** de destinatários. Aqui usamos endereços de exemplo; numa aplicação real, o destinatário poderia ser `[instance.email]`.

As configurações de e-mail do `settings.py` apontam para o MailHog, que recebe na porta 1025:

```python
# backend/settings.py
# Email config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
EMAIL_HOST = config('EMAIL_HOST', 'localhost')
EMAIL_PORT = config('EMAIL_PORT', 1025, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
```

O MailHog roda num contêiner do `docker-compose.yml` do projeto:

```yaml
# docker-compose.yml
  mailhog:
    container_name: dicas_de_django_mailhog
    image: mailhog/mailhog
    restart: always
    logging:
      driver: 'none'
    ports:
      - 1025:1025
      - 8025:8025
    networks:
      - dicas-de-django-network
```

Crie um usuário pelo Admin e abra o MailHog em `http://localhost:8025`: lá está o e-mail de `from@example.com` para `to@example.com`, com o assunto "Novo usuário criado" e o texto "Um novo usuário com email ... foi criado.".

## Model Product: slug automático

Em `Product` vamos adicionar um `slug`, e preenchê-lo automaticamente com um `pre_save` a partir do título. Usamos o `pre_save` porque queremos alterar o objeto **antes** de ele ser gravado, sem precisar chamar `save()` de novo.

```python
# backend/product/models.py
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.utils.text import slugify

from backend.core.models import TimeStampedModel


class Product(TimeStampedModel):
    title = models.CharField('título', max_length=255, unique=True)
    description = models.TextField('descrição', null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='categoria',
        related_name='products',
        null=True,
        blank=True,
    )
    slug = models.SlugField(null=True, blank=True)
    ...


@receiver(pre_save, sender=Product)
def product_pre_save(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)
```

O `slug` é `null=True, blank=True` para não ser obrigatório no formulário. Se ele vier vazio, o signal preenche com o `slugify` do título.

Como acrescentamos um campo, crie e aplique a migração. O vídeo não mostra este passo; no repositório do projeto, a migração do `slug` aparece na [Dica 29](095-29-import-csv.md), junto com o campo `price`:

```bash
python manage.py makemigrations
python manage.py migrate
```

No Admin, cadastre um produto com o título "notebook 15 polegadas" e salve: o slug fica `notebook-15-polegadas`.

## Bonus: colocando o Signals num arquivo separado

Crie o arquivo `signals.py` na app `product`:

```bash
touch backend/product/signals.py
```

Recorte a função do `models.py` e cole no `signals.py`, sem o decorator. Do `models.py` também saem os imports de `pre_save`, `receiver` e `slugify`.

```python
# backend/product/signals.py
from django.utils.text import slugify


def product_pre_save(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)
```

Agora precisamos editar o arquivo `apps.py`. Para o Django reconhecer o signal, conectamos a função no método `ready()` da configuração da app, que roda quando a app está pronta:

```python
# backend/product/apps.py
from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.product'

    def ready(self):
        from django.db.models.signals import pre_save

        from .models import Product
        from .signals import product_pre_save

        pre_save.connect(product_pre_save, sender=Product)
```

Os imports ficam dentro do `ready()` porque os models só podem ser importados depois que as apps foram carregadas.

Para finalizar vamos mostrar o `slug` na lista do Admin e deixá-lo como somente leitura (`readonly_fields`) no formulário, já que ele é preenchido automaticamente:

```python
# backend/product/admin.py
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (PhotoInline,)
    list_display = ('__str__', 'slug', 'category')
    readonly_fields = ('slug',)
    search_fields = ('title',)
    list_filter = ('category',)
    # date_hierarchy = 'created'
```

Cadastre um novo produto: o slug é preenchido e aparece na lista do Admin.

Resumindo: `post_save` tem `instance` e `created`; `pre_save` tem só `instance`, ainda sem id. Conecte com `@receiver` ou com `signal.connect()`, de preferência num `signals.py` ligado no `ready()` da app. E, mais uma vez, use signals com moderação.
