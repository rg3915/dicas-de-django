# 22 - Criando issues por linha de comando com bitbucket cli

<a href="https://youtu.be/N2oYZxixcSU">
    <img src="../.gitbook/assets/youtube.png">
</a>


## Instalação

`pip install bitbucket-python`


## Usando com Python

> Lembre-se de habilitar a criação de issues no repositório.


```python
from bitbucket.client import Client
from decouple import config

email = config('BITBUCKET_EMAIL')
password = config('BITBUCKET_PASSWORD')
client = Client(email, password)

repository_slug = config('REPOSITORY_SLUG')

repo = client.get_repository(repository_slug)

data = {
    'title': 'Your title',
    'content': {'raw': 'Your description'},
    'kind': 'task'
}
# kind: task or bug

response = client.create_issue(repository_slug, data)
```

## Usando com click

```python
import click
from bitbucket.client import Client
from decouple import config

'''
Usage: python bitbucket_cli.py --title='Your title' --description='Your description' --kind='task'
'''


@click.command()
@click.option('--title', prompt='Title', help='Type the title.')
@click.option('--description', prompt='Description', help='Type the description.')
@click.option('--kind', prompt='Kind', help='Kind is task or bug.')
def create_issue(title, description, kind):
    email = config('BITBUCKET_EMAIL')
    password = config('BITBUCKET_PASSWORD')
    repository_slug = config('REPOSITORY_SLUG')

    client = Client(email, password)

    data = {
        'title': title,
        'content': {'raw': description},
        'kind': kind
    }
    response = client.create_issue(repository_slug, data)

    click.echo(response['title'])


if __name__ == '__main__':
    create_issue()
```
