# 7 - Rodando o ORM do Django no Jupyter Notebook

<a href="https://youtu.be/bXtmvu_O_sk">
    <img src="../.gitbook/assets/youtube.png">
</a>


Instale

```
pip install ipython[notebook]
```

Rode

```
python manage.py shell_plus --notebook
```

**Obs**: No Django 3.x talvez você precise dessa configuração [async-safety](https://docs.djangoproject.com/en/3.0/topics/async/#async-safety).

`os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"`
