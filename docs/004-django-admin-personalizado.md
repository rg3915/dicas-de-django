# Dica 4 - Django Admin personalizado

**Versões usadas no vídeo:** Django 2.2.13 e Python 3.8.2.
{: .versoes }

<a href="https://youtu.be/jogkxIkCzI8">
    <img src="../.gitbook/assets/youtube.png">
</a>

Documentação: [https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#modeladmin-options](https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#modeladmin-options)

O admin do Django já é útil só registrando o model, mas com poucas linhas de `ModelAdmin` ele fica muito melhor: colunas extras na listagem, busca, filtros, navegação por datas, campos somente leitura, colunas calculadas e controle do que o usuário pode adicionar ou apagar.

Esta dica é uma continuação da [Dica 3](003-django-bulk_create-e-django-autoslug.md): vamos personalizar o admin dos models `Article` e `Category` criados lá.

## Pré-requisitos

O projeto da Dica 3 (`myproject`, app `core`), com os artigos e categorias já inseridos com o `bulk_create` e um superusuário (o boilerplate cria o usuário `admin`). Os models, para referência:

```python
# myproject/core/models.py
from django.db import models
from autoslug import AutoSlugField


class Article(models.Model):
    title = models.CharField('título', max_length=200)
    subtitle = models.CharField('sub-título', max_length=200)
    slug = AutoSlugField(populate_from='title')
    category = models.ForeignKey(
        'Category',
        related_name='categories',
        verbose_name='categoria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    published_date = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'artigo'
        verbose_name_plural = 'artigos'

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField('título', max_length=50, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.title
```

Suba o servidor e deixe-o rodando:

```bash
python manage.py runserver
```

## O mais simples: admin.site.register

O jeito mais básico de colocar um model no admin é registrá-lo:

```python
# myproject/core/admin.py
from django.contrib import admin
from .models import Article

admin.site.register(Article)
```

Entre em [http://localhost:8000/admin/](http://localhost:8000/admin/) com o usuário `admin` e clique em **Artigos**. (No vídeo o admin está em inglês, porque o `LANGUAGE_CODE` do projeto é `en-us`; os nomes dos models aparecem em português por causa do `verbose_name`.) Aparecem os 4 artigos da dica anterior, mas de forma bem simples: uma única coluna com o `__str__` de cada objeto (o título), sem busca e sem filtros.

## Registrando com o decorator e um ModelAdmin

Para personalizar, criamos uma classe que herda de `admin.ModelAdmin` e a registramos com o decorator `@admin.register`, que faz o mesmo que o `admin.site.register`, mas fica junto da classe. Já vamos importar o `Category` também:

```python
# myproject/core/admin.py
from django.contrib import admin
from .models import Article, Category


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    search_fields = ('title',)
    list_filter = (
        'category',
    )
    readonly_fields = ('slug',)
    date_hierarchy = 'published_date'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass
```

Cada opção:

* `list_display`: as colunas da listagem. Agora aparecem o título e o slug.
* `search_fields`: os campos usados pela caixa de busca, que só aparece quando essa opção existe. A busca procura o texto digitado em qualquer parte do título.
* `list_filter`: cria a barra lateral **Filter**, aqui "By categoria" (em português, "Por categoria"), com as categorias `dicas`, `django` e `python`.
* `readonly_fields`: campos que aparecem no formulário, mas não podem ser editados. O slug é gerado pelo `AutoSlugField`, então não faz sentido editá-lo à mão.
* `date_hierarchy`: a navegação por datas acima da listagem (ano, mês, dia), usando o campo `published_date`.

### Cuidado com a vírgula da tupla

Essas opções esperam uma lista ou tupla. Se você escrever o `list_filter` assim, sem a vírgula:

```python
    list_filter = (
        'category'
    )
```

os parênteses não criam uma tupla, só uma string `'category'`, e o `runserver` para com este erro:

```
ERRORS:
<class 'myproject.core.admin.ArticleAdmin'>: (admin.E112) The value of 'list_filter' must be a list or tuple.

System check identified 1 issue (0 silenced).
```

Por isso escrevemos `('title',)` e `('category',)`, com a vírgula.

Recarregue a página dos artigos: agora há a caixa de busca, a navegação de datas, o filtro por categoria e a coluna **Slug**. Abra um artigo: a **Categoria** pode ser escolhida, e o **Slug** aparece só como texto, sem campo para editar.

## Uma coluna calculada: a data no formato brasileiro

Podemos colocar `'published_date'` direto no `list_display`, mas ele aparece no formato padrão do Django em inglês, como "June 14, 2020, 6:42 a.m.". Para mostrar dia/mês/ano, criamos um método no `ModelAdmin` e usamos o nome dele no `list_display`:

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'get_published_date')
    ...

    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')
```

O método recebe o objeto da linha (`obj`) e devolve o que deve aparecer na coluna. O `if` protege o caso de o campo estar vazio, e o `strftime('%d/%m/%Y')` formata como `14/06/2020` (`%Y` é o ano com quatro dígitos).

O título da coluna fica "Get published date", gerado a partir do nome do método. Para trocar, use o atributo `short_description`:

```python
    get_published_date.short_description = 'Data de Publicação'
```

## Um formulário personalizado (opcional)

O `ModelAdmin` também aceita um formulário próprio, com a opção `form`, para quando você quer campos a mais, campos a menos ou validações diferentes. No vídeo isso fica só indicado, comentado, porque o `ArticleAdminForm` não é criado:

```python
# from .forms import ArticleAdminForm
...
    # form = ArticleAdminForm
```

## Restringindo ações e permissões da categoria

Na listagem do admin existe o menu **Action** (Ação), que por padrão traz "Delete selected ..." (remover os selecionados). Para tirar todas as ações de um model:

```python
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    actions = None
```

Com isso somem o menu de ações e as caixas de seleção da listagem de categorias.

Para impedir que alguém **adicione** categorias pelo admin, sobrescreva o `has_add_permission` e retorne `False`:

```python
    def has_add_permission(self, request, obj=None):
        return False
```

O botão **Add categoria** some da listagem, e o link **Add** some da página inicial do admin. Mesmo acessando a URL `/admin/core/category/add/` direto, o Django responde `403 Forbidden`.

Do mesmo jeito, o `has_delete_permission` controla o botão **Delete** (apagar). Como esses métodos recebem o `request`, dá para decidir por usuário (`request.user`) quem pode fazer o quê.

E dá para ir além: liberar em desenvolvimento e bloquear em produção, usando o `DEBUG` do `settings`. Para isso, importe o `settings`:

```python
from django.conf import settings
```

e defina o método dentro de um `if`, no corpo da classe:

```python
    if not settings.DEBUG:
        def has_delete_permission(self, request, obj=None):
            return False
```

O `if` é avaliado uma vez, quando a classe é criada. Com `DEBUG=True` (desenvolvimento) o método nem existe, e o botão **Delete** continua aparecendo, como no vídeo. Com `DEBUG=False` (produção), apagar categorias fica bloqueado.

## O admin.py completo

```python
# myproject/core/admin.py
from django.conf import settings
from django.contrib import admin

from .models import Article, Category

# from .forms import ArticleAdminForm


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'get_published_date')
    search_fields = ('title',)
    list_filter = (
        'category',
    )
    readonly_fields = ('slug',)
    date_hierarchy = 'published_date'
    # form = ArticleAdminForm

    def get_published_date(self, obj):
        if obj.published_date:
            return obj.published_date.strftime('%d/%m/%Y')

    get_published_date.short_description = 'Data de Publicação'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request, obj=None):
        return False

    if not settings.DEBUG:
        def has_delete_permission(self, request, obj=None):
            return False
```

Resultado na listagem de artigos:

| Título | Slug | Data de Publicação |
| --- | --- | --- |
| Django Admin | django-admin | 14/06/2020 |
| Django Autoslug | django-autoslug | 14/06/2020 |
| Django Boilerplate | django-boilerplate | 14/06/2020 |
| Django extensions | django-extensions | 14/06/2020 |

Com busca, navegação por data e filtro por categoria. E na listagem de categorias, sem ações e sem o botão de adicionar.

Há muitas outras opções (`list_display_links`, `list_editable`, `ordering`, `inlines`, `fieldsets`...). A lista completa está na [documentação do ModelAdmin](https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#modeladmin-options).

Observação: no Django 3.2 e superiores, em vez do atributo `short_description`, também dá para usar o decorator `@admin.display(description='Data de Publicação')` no método.
