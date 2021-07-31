# 21 - Criando issues por linha de comando com gitlab cli

<a href="https://youtu.be/mZezRjHv4Xg">
    <img src="../.gitbook/assets/youtube.png">
</a>


## Configuração

Primeiro precisamos criar um arquivo `/etc/myfile.cfg`

`sudo vim /etc/myfile.cfg  # precisa do sudo`

```
[global]
default = somewhere
ssl_verify = true
timeout = 5

[somewhere]
url = https://gitlab.com
private_token = your-token
api_version = 4
```

## Instalação

`pip install python-gitlab`


## Fazendo um teste no Python

```python
import gitlab

gl = gitlab.Gitlab.from_config('somewhere', ['/etc/myfile.cfg'])

issues = gl.issues.list()
for issue in issues:
    print(issue.iid, issue.title)
```

## Criando issues

```python
import gitlab

gl = gitlab.Gitlab.from_config('somewhere', ['/etc/myfile.cfg'])

issues = gl.issues.list()

project = gl.projects.get(ID-DO-PROJETO)

project.issues.create(
    {'title': 'I have a bug',
   'description': 'Lorem ipsum...'})

for issue in project.issues.list():
    print(issue.iid, issue.title)
```

## gitlab + click

```python
import click
import gitlab
from decouple import config

'''
Usage: python glab-cli.py --title='Your title' --description='Your description'
'''


gl = gitlab.Gitlab.from_config('somewhere', ['/etc/myfile.cfg'])
project = gl.projects.get(config('GITLAB_PROJECT_ID'))


@click.command()
@click.option('--title', prompt='Title', help='Type the title.')
@click.option('--description', prompt='Description', help='Type the description.')
def create_issue(title, description):
    response = project.issues.create(
        {"title": f"{title}",
         "description": f"{description}"})

    click.echo(response.iid)
    click.echo(response.title)


if __name__ == '__main__':
    create_issue()
```
