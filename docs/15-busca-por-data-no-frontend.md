# 15 - Busca por data no frontend

<a href="https://youtu.be/sqhQM5KUFHE">
    <img src="../.gitbook/assets/youtube.png">
</a>


Considere um template com os campos:

```html
<input class="form-control" name='start_date' type="date">
<input class="form-control" name='end_date' type="date">
```

Em `views.py` basta fazer:

```python
def article_list(request):
    template_name = 'core/article_list.html'
    object_list = Article.objects.all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        # Converte em data e adiciona um dia.
        end_date = parse(end_date) + timedelta(1)
        object_list = object_list.filter(
            published_date__range=[start_date, end_date]
        )

    context = {'object_list': object_list}
    return render(request, template_name, context)
```

Pra não precisar fazer o

```python
end_date = parse(end_date) + timedelta(1)
```

basta acrescentar `date` antes do `range`, dai fica assim:

```python
object_list = object_list.filter(
    published_date__date__range=[start_date, end_date]
)
```

Agradecimentos a [@walisonfilipe](https://twitter.com/walisonfilipe)
