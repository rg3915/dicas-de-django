# Dica 01 - Criando Issues com API do Github (Linux)

<a href="https://youtu.be/P0PCq3dF3cs">
    <img src="../.gitbook/assets/youtube.png">
</a>

```
mkdir cli
touch cli/create_issue.py

touch .env.sample
touch requirements.txt
```

## Instalação

```
python -m venv .venv
source .venv/bin/activate

pip install click python-decouple requests
pip freeze | grep -E 'click|python-decouple|requests' > requirements.txt
```

## Variáveis de Ambiente

Pegue o token no Github, e defina

```
# .env
REPO_OWNER=rg3915
REPO_NAME=dicas-de-django
TOKEN=********************
```

O conteúdo de `create_issue.py` é

```python
# create_issue.py
import click
import requests
from decouple import config

'''
https://docs.github.com/en/rest/reference/issues#create-an-issue

python cli/create_issue.py \
--title='' \
--body='' \
--labels='feature'
'''

# O repositório para adicionar a issue
REPO_OWNER = config('REPO_OWNER')
REPO_NAME = config('REPO_NAME')
TOKEN = config('TOKEN')


def write_file(filename, number, title, description, labels):
    labels = ', '.join(labels).strip()
    with open(filename, 'a') as f:
        f.write(f'\n---\n\n')
        f.write(f'[ ] {number} - {title}\n')
        f.write(f'    {labels}\n\n')

        if description:
            f.write(f'    {description}\n\n')

        f.write(f"    make lint; g add . ; g co -m '{title}. close #{number}'; g push\n")


@click.command()
@click.option('--title', prompt='Title', help='Digite o título.')
@click.option('--body', prompt='Description', help='Digite a descrição.')
# @click.option('--assignee', prompt='Assignee', help='Digite o nome da pessoa a ser associada.')
@click.option('--labels', prompt='Labels', help='Digite as labels.')
def make_github_issue(title, body=None, assignee=None, milestone=None, labels=None):
    '''
    Cria issue no github.com.
    '''
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'
    headers = {
        "Authorization": f"token {TOKEN}",
    }
    labels = labels.split(',')

    # Cria a issue
    issue = {
        "title": title,
        "body": body,
        "labels": labels
    }
    if assignee:
        issue['assignees'] = [assignee]

    # Adiciona a issue no repositório
    req = requests.post(url, headers=headers, json=issue)

    if req.status_code == 201:
        print(f'Successfully created Issue "{title}"')
        number = req.json()['number']
        description = body

        filename = '/home/seu-usuario/tarefas.txt'
        write_file(filename, number, title, description, labels)

    else:
        print(f'Could not create Issue "{title}"')


if __name__ == '__main__':
    make_github_issue()
```

Então digite

```
python cli/create_issue.py \
--title='' \
--body='' \
--labels='feature'
```