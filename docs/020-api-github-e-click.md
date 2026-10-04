# Dica 20 - api github e click

**Versões usadas no vídeo:** esta dica não usa Django; Python 3.8, click 7.1.2, requests 2.24 e python-decouple 3.3.
{: .versoes }

<a href="https://youtu.be/gwYpMKDAqBM">
    <img src="../.gitbook/assets/youtube.png">
</a>

Na [Dica 19](019-criando-issues-por-linha-de-comando-com-a-api-do-github.md) criamos uma issue no GitHub pelo terminal, mas o título, a descrição e as labels estavam fixos no código. Agora vamos usar o [Click](https://click.palletsprojects.com/) para transformar o script num comando de verdade: ele aceita opções (`--title`, `--body` etc.) e, se você não passar alguma, pergunta o valor no terminal.

No fim, de bônus, veremos como fechar várias issues de uma vez pela mensagem de commit.

## Pré-requisitos

* O script `github_cli.py` e o arquivo `.env` da [Dica 19](019-criando-issues-por-linha-de-comando-com-a-api-do-github.md), com `REPO_USERNAME`, `REPO_PASSWORD`, `REPO_OWNER` e `REPO_NAME`.
* O Click:

```bash
pip install click
```

(no vídeo, `click==7.1.2`.)

## Copiando o script

Partimos de uma cópia do script anterior:

```bash
cp github_cli.py github_cli2.py
```

## O script com Click

```python
# github_cli2.py
import json

import click
import requests
from decouple import config

'''
https://docs.github.com/en/rest/reference/issues#create-an-issue

Usage: python github_cli2.py --title='Your title' \
            --body='Your description' \
            --assignee='Assignee name' \
            --labels='enhancement'
'''

# Autenticação
REPO_USERNAME = config('REPO_USERNAME')
REPO_PASSWORD = config('REPO_PASSWORD')

# O repositório para adicionar a issue
REPO_OWNER = config('REPO_OWNER')
REPO_NAME = config('REPO_NAME')


@click.command()
@click.option('--title', prompt='Title', help='Type the title.')
@click.option('--body', prompt='Description', help='Type the description.')
@click.option('--assignee', prompt='Assignee', help='Type the assignee name.')
@click.option('--labels', prompt='Labels', help='Type the labels.')
def make_github_issue(title, body=None, assignee=None, milestone=None, labels=None):
    '''
    Create an issue on github.com using the given parameters.
    '''
    url = 'https://api.github.com/repos/%s/%s/issues' % (REPO_OWNER, REPO_NAME)
    session = requests.Session()
    session.auth = (REPO_USERNAME, REPO_PASSWORD)
    # Create our issue
    issue = {
        'title': title,
        'body': body,
        'assignee': assignee,
        'milestone': milestone,
        'labels': [labels]
    }
    # Add the issue to our repository
    r = session.post(url, json.dumps(issue))
    if r.status_code == 201:
        print('Successfully created Issue "%s"' % title)
    else:
        print('Could not create Issue "%s"' % title)
        print('Response:', r.content)


if __name__ == '__main__':
    make_github_issue()
```

O que mudou em relação à Dica 19:

* **`import click`** no topo.
* **`@click.command()`** transforma a função `make_github_issue` num comando de linha de comando.
* **`@click.option(...)`**, um para cada campo. O primeiro argumento é o nome da opção (`--title`), que o Click passa para o parâmetro de mesmo nome da função. `prompt='Title'` faz o Click perguntar o valor quando a opção não for informada, e `help` é o texto que aparece no `--help`.
* **`'labels': [labels]`**: o Click entrega `labels` como uma string (por exemplo `'enhancement'`), mas a API espera uma lista, então colocamos o valor dentro de uma lista.
* **`milestone`** não ganhou opção; continua `None`.
* No `if __name__ == '__main__':` sai o título e a descrição fixos; agora só chamamos `make_github_issue()`, sem argumentos. Quem preenche os argumentos é o Click.

O Click também gera a ajuda automaticamente:

```
$ python github_cli2.py --help
Usage: github_cli2.py [OPTIONS]

  Create an issue on github.com using the given parameters.

Options:
  --title TEXT     Type the title.
  --body TEXT      Type the description.
  --assignee TEXT  Type the assignee name.
  --labels TEXT    Type the labels.
  --help           Show this message and exit.
```

## Usando com perguntas (prompt)

Rodando sem nenhuma opção, o Click pergunta cada valor:

```
$ python github_cli2.py
Title: Titulo
Description: Descrição
Assignee: rg3915
Labels: enhancement
Successfully created Issue "Titulo"
```

No GitHub aparece a issue **Titulo** (no vídeo, a #14), com a descrição, a label `enhancement` e atribuída ao `rg3915`.

## Usando com opções

Como usar

```
python github_cli2.py --title='Your title' \
    --body='Your description' \
    --assignee='username' \
    --labels='enhancement'
```

Com todas as opções informadas, o Click não pergunta nada e a issue **Your title** (no vídeo, a #15) é criada direto. Assim fica fácil criar várias issues diferentes, ou chamar o comando a partir de outro script.

## Bônus: fechando issues pela mensagem de commit

As issues #13, #14 e #15 criadas nos testes eram todas sobre o mesmo assunto, então o vídeo fecha as três de uma vez pelo commit. Basta escrever `close #número` na mensagem:

```bash
git status
git add github_cli2.py
git commit -m 'Adicionar github_cli2.py. Close #13 close #14 close #15'
git push
```

```
[master fffd965] Adicionar github_cli2.py. Close #13 close #14 close #15
 1 file changed, 2 insertions(+), 10 deletions(-)
```

Quando o commit chega na branch padrão do repositório (aqui, a `master`) com o `git push`, o GitHub fecha automaticamente as issues citadas. Também funcionam as palavras `closes`, `fix`, `fixes`, `resolve` e `resolves`.

## Conclusão

Com meia dúzia de decoradores do Click, o script virou um comando com opções, ajuda e perguntas interativas, e criar uma issue nova não exige mais editar o código. Nas próximas dicas fazemos o mesmo com o [GitLab](021-criando-issues-por-linha-de-comando-com-gitlab-cli.md) e com o [Bitbucket](022-criando-issues-por-linha-de-comando-com-bitbucket-cli.md).

Observação: assim como na Dica 19, hoje a API do GitHub não aceita a senha da conta; use um *personal access token* em `REPO_PASSWORD`.
