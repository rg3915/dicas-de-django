# Dica 19 - Criando Issues por linha de comando com a api do github

**Versões usadas no vídeo:** esta dica não usa Django; Python 3.8, requests 2.24 e python-decouple 3.3.
{: .versoes }

<a href="https://youtu.be/XwT2CMrGfiE">
    <img src="../.gitbook/assets/youtube.png">
</a>


## [github cli](https://docs.github.com/en/rest/reference/issues#create-an-issue)

Neste tutorial vamos criar uma issue no GitHub direto do terminal, sem abrir o navegador, usando a API REST do GitHub com a biblioteca `requests`. É um script Python pequeno, que serve de base para automatizar a criação de issues (no [próximo vídeo](020-api-github-e-click.md) ele ganha uma interface de linha de comando com o Click).

## Como funciona a API

Na documentação (link no título acima), em **Issues > Create an issue**, vemos que para criar uma issue basta fazer um `POST` neste endereço:

```
POST /repos/{owner}/{repo}/issues
```

onde `{owner}` é o dono do repositório e `{repo}` é o nome do repositório. No caso do vídeo: `https://api.github.com/repos/rg3915/dicas-de-django/issues`. O corpo da requisição é um JSON com o título (obrigatório) e, opcionalmente, o texto (`body`), o responsável (`assignee`), o marco (`milestone`) e as etiquetas (`labels`). Se der certo, a API responde com o status **201 Created**.

## Pré-requisitos

Instale o `requests` e o `python-decouple` (que lê as configurações do arquivo `.env`):

```bash
pip install requests==2.24.0 python-decouple==3.3
```

Crie um arquivo `.env` (arquivo oculto) na mesma pasta do script, com os seus dados:

```
# .env
REPO_USERNAME=rg3915
REPO_PASSWORD=xxxxxxxxxxxxx
REPO_OWNER=rg3915
REPO_NAME=dicas-de-django
```

* `REPO_USERNAME` e `REPO_PASSWORD`: o usuário e a senha (veja a observação no fim) usados para autenticar na API.
* `REPO_OWNER` e `REPO_NAME`: o dono e o nome do repositório onde a issue será criada.

Não suba o `.env` para o repositório; coloque-o no `.gitignore`.

## O script

Crie o arquivo `github_cli.py`:

```python
# github_cli.py
import json

import requests
from decouple import config

# Autenticação
REPO_USERNAME = config('REPO_USERNAME')
REPO_PASSWORD = config('REPO_PASSWORD')

# O repositório para adicionar a issue
REPO_OWNER = config('REPO_OWNER')
REPO_NAME = config('REPO_NAME')


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
        'labels': labels
    }
    # Add the issue to our repository
    r = session.post(url, json.dumps(issue))
    if r.status_code == 201:
        print('Successfully created Issue "%s"' % title)
    else:
        print('Could not create Issue "%s"' % title)
        print('Response:', r.content)


if __name__ == '__main__':
    title = 'Criar github cli'
    body = 'API para criar issues por linha de comando.'
    make_github_issue(
        title=title,
        body=body,
        assignee='rg3915',
        milestone=None,
        labels=['enhancement']
    )
```

Explicando por partes:

* **Configurações**: `config('REPO_USERNAME')` etc. leem os valores do `.env`, assim usuário e senha não ficam escritos no código.
* **`make_github_issue`**: recebe o título (obrigatório) e os campos opcionais, todos com `None` como padrão.
* **`url`**: monta o endereço `https://api.github.com/repos/<dono>/<repositório>/issues`.
* **`requests.Session()`**: cria uma sessão e define `session.auth` com a tupla `(usuário, senha)`, que o `requests` envia como autenticação HTTP Basic.
* **`issue`**: o dicionário com os dados da issue, convertido para JSON com `json.dumps(issue)` e enviado no `session.post(url, ...)`.
* **`r.status_code == 201`**: 201 é o código de "criado". Se vier outro código, o script mostra a mensagem de erro e o conteúdo da resposta (`r.content`), que diz o que deu errado.
* **`if __name__ == '__main__'`**: quando o arquivo é executado direto, cria a issue "Criar github cli", atribuída ao usuário `rg3915` e com a label `enhancement`. Repare que `labels` é uma **lista**, porque uma issue pode ter várias labels.

## Rodando

```bash
python github_cli.py
```

No vídeo, as primeiras execuções deram dois erros de digitação, que valem como lembrete:

* `SyntaxError: invalid syntax` na linha `if __name__ = '__main__':` (faltou um `=`; o certo é `==`).
* `NameError: name 'request' is not defined` em `session = request.Session()` (o módulo é `requests`, no plural).

Corrigido, a saída é:

```
Successfully created Issue "Criar github cli"
```

Atualizando a página de issues do repositório no GitHub, aparece a issue **Criar github cli** (no vídeo, a #13), com a label `enhancement`, atribuída ao `rg3915` e com a descrição "API para criar issues por linha de comando.".

## Conclusão

Com poucas linhas de `requests` criamos uma issue pela API do GitHub direto do terminal. Para criar várias issues diferentes sem editar o código toda vez, veja a próxima dica, [API do GitHub e Click](020-api-github-e-click.md), que transforma este script num comando com opções.

Observação: desde novembro de 2020 a API do GitHub não aceita mais a senha da conta na autenticação. Hoje, em `REPO_PASSWORD` coloque um *personal access token* (criado em [github.com/settings/tokens](https://github.com/settings/tokens)) com permissão para escrever issues; o resto do script continua igual.
