# Dica 54 - django-extensions - mais comandos

<a href="https://youtu.be/pguupq-s70M">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django)

Doc: [https://django-extensions.readthedocs.io/en/latest/](https://django-extensions.readthedocs.io/en/latest/)

# [Command Extensions](https://django-extensions.readthedocs.io/en/latest/command_extensions.html)


Veremos mais comandos do django-extensions.

```
pip install -U django-extensions
```

```python
# settings.py
INSTALLED_APPS = (
    ...
    'django_extensions',
)
```


## shell_plus

Roda o shell do Django importando todos os pacotes essenciais.

```
python manage.py shell_plus
```



## admin_generator

Gera uma classe no Admin para a app selecionada.

```
python manage.py admin_generator product
python manage.py admin_generator product >> myproject/product/admin.py
```



## clean_pyc

Remove todos os arquivos `*.pyc`

```
python manage.py clean_pyc
```



## create_command

Cria um novo comando do Django.

```
python manage.py create_command core -n novocomando
```



## create_template_tags

Cria um novo `template_tags`.

```
python manage.py create_template_tags core
python manage.py create_template_tags core -n lorem_tags
```


## show_template_tags

Lista todos os `template_tags`.

```
python manage.py show_template_tags
```



## generate_password

Gera uma senha randômica.

```
python manage.py generate_password
python manage.py generate_password --length 32
```



## generate_secret_key

Gera uma chave secreta.

```
python manage.py generate_secret_key
```



## graph_models

Link na descrição do video

https://youtu.be/99dOVsDBUxg


## list_model_info

Lista as informações de um modelo.

```
python manage.py list_model_info --model product.Product
python manage.py list_model_info --model product.Product --field-class
```



## list_signals

Lista os sinais do projeto.

```
python manage.py list_signals
```



## print_settings

Retorna as informações do `settings`.

```
python manage.py print_settings
```



## show_urls

Lista todas as urls do projeto.

```
python manage.py show_urls
```

