# Dica 41 - django-seed

**Versões usadas no vídeo:** Django 2.2, django-seed 0.3.0 e Python 3.8.
{: .versoes }

<a href="https://youtu.be/9IVp4mLsrdc">
    <img src="../.gitbook/assets/youtube.png">
</a>

O [django-seed](https://github.com/Brobin/django-seed) é uma lib que gera dados aleatórios para os seus modelos de uma forma rápida e simples. Ele usa o [Faker](037-faker.md) por baixo dos panos e é um *fork* do antigo `django_faker`, feito para funcionar com as versões mais novas do Python e do Django.

A diferença para o que fizemos na [Dica 37 - Faker](037-faker.md) é que aqui não escrevemos nenhum código: o django-seed olha o nome e o tipo de cada campo do modelo e escolhe sozinho que tipo de dado falso gerar.

## Pré-requisitos

Vamos usar a app `travel` criada na [Dica 40 - Formulários: date, datetime, duration e templatetags de data](040-formularios-date-datetime-duration-e-templatetags-de-data.md), com o modelo `Travel`:

```python
# myproject/travel/models.py
from django.db import models


class Travel(models.Model):
    destination = models.CharField('destino', max_length=200)
    date_travel = models.DateField('data', null=True, blank=True)
    datetime_travel = models.DateTimeField('data/hora', null=True, blank=True)
    time_travel = models.TimeField('tempo', null=True, blank=True)
    duration_travel = models.DurationField('duração', null=True, blank=True)

    class Meta:
        ordering = ('destination',)
        verbose_name = 'viagem'
        verbose_name_plural = 'viagens'

    def __str__(self):
        return self.destination
```

A lista de viagens em `/travel/` é uma `ListView` com `paginate_by = 10`.

## Instalação

```bash
pip install django-seed
```

No vídeo, a versão instalada foi a 0.3.0, que era a mais recente na época.

Adicione `django_seed` em `INSTALLED_APPS`, em `settings.py`:

```python
# myproject/settings.py
INSTALLED_APPS = [
    ...
    'myproject.travel',
    'django_seed',
]
```

É isso que disponibiliza o comando `seed` no `manage.py`.

## Gerando os dados

Depois, simplesmente rode o comando:

```bash
python manage.py seed travel --number=15
```

onde `travel` é o nome (o *label*) da nossa app neste projeto, e `--number=15` é a quantidade de registros que serão criados **para cada modelo** da app (sem o `--number`, o padrão é 10). Você pode passar mais de uma app de uma vez: `python manage.py seed app1 app2 --number=15`.

A saída mostra cada registro criado:

```
Seeding 15 Travels
Model Travel generated record with primary key 1
Model Travel generated record with primary key 2
...
Model Travel generated record with primary key 15
```

A versão 0.3.0 também imprime, antes disso, um dicionário com as opções do comando (`{'verbosity': 1, ..., 'number': 15, 'seeder': None}`), que pode ser ignorado.

Rode o servidor e abra a lista de viagens:

```bash
python manage.py runserver
```

Em `/travel/` aparecem 10 viagens na primeira página e as outras 5 na página 2. Cada campo recebe um valor compatível com o seu tipo: datas no `DateField`, data e hora no `DateTimeField`, horários no `TimeField` e intervalos no `DurationField`. Como o django-seed não sabe que `destination` é um destino, ele preenche o `CharField` com um texto aleatório em inglês.

## Fixando o valor de um campo

Se precisar que um campo tenha sempre o mesmo valor, use a opção `--seeder`, no formato `"Modelo.campo" "valor"`:

```bash
python manage.py seed travel --number=15 --seeder "Travel.destination" "Japão"
```

Todos os registros criados terão `destination` igual a `Japão`; os outros campos continuam aleatórios.

Atenção à ordem quando houver chaves estrangeiras: se um modelo da app A tem uma `ForeignKey` para um modelo da app B, rode o `seed` da app B primeiro.

## Conclusão

Com uma instalação e um comando, o django-seed popula qualquer app com dados falsos, sem escrever código. Quando você precisa de dados mais realistas (um e-mail montado a partir do nome, um destino que seja um país), o caminho é escrever o seu próprio comando com o Faker, como na [Dica 37](037-faker.md).

Observação: ao testar a versão 0.3.0 com SQLite, o comando falhou com `ModuleNotFoundError: No module named 'psycopg2'`, porque essa versão importa o `ArrayField` do PostgreSQL. Se isso acontecer, instale também o `psycopg2-binary` (`pip install psycopg2-binary`).
