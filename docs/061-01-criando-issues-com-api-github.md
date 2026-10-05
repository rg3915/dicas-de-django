# Dica 01 - Criando Issues com API do Github (Linux)

**Versões usadas no vídeo:** não usa Django; Python 3.10.6, click 8.1.3, python-decouple 3.6 e requests 2.28.1.
{: .versoes }

<a href="https://youtu.be/P0PCq3dF3cs">
    <img src="../.gitbook/assets/youtube.png">
</a>

Github: [https://github.com/rg3915/dicas-de-django](https://github.com/rg3915/dicas-de-django) (branch `aula01`)

Documentação: [https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#create-an-issue](https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#create-an-issue)

Este é o primeiro vídeo do **Projeto Dicas de Django**, uma série em que cada dica continua o projeto da anterior. Antes de começar a programar o projeto, vamos criar uma ferramenta de linha de comando, em Python, que cria issues no GitHub direto do terminal do Linux, usando a API REST do GitHub.

O script faz duas coisas:

1. Cria a issue no repositório (título, descrição e labels).
2. Anota a issue criada num arquivo de tarefas local (`~/tarefas.txt`), já com o comando do commit que vai fechar a issue (`close #número`).

## Estrutura de pastas

Na pasta do projeto, crie a pasta `cli`, o script e os arquivos de apoio:

```bash
mkdir cli
touch cli/create_issue.py

touch .env.sample
touch requirements.txt
```

## Instalação

Crie e ative o ambiente virtual, e instale as três bibliotecas que vamos usar:

* [click](https://click.palletsprojects.com/): para criar a interface de linha de comando (as opções `--title`, `--body` e `--labels`).
* [python-decouple](https://github.com/HBNetwork/python-decouple): para ler o token e o nome do repositório do arquivo `.env`.
* [requests](https://requests.readthedocs.io/): para fazer a requisição `POST` na API do GitHub.

```bash
python -m venv .venv
source .venv/bin/activate

pip install click python-decouple requests
pip freeze | grep -E 'click|python-decouple|requests' > requirements.txt
```

No vídeo, o `pip freeze` mostrou também as dependências do requests (`certifi`, `charset-normalizer`, `idna`, `urllib3`). Só as três que usamos diretamente vão para o `requirements.txt`:

```
click==8.1.3
python-decouple==3.6
requests==2.28.1
```

## Pegando o token no GitHub

Para usar a API você precisa de um **personal access token**:

1. No GitHub, clique na sua foto e vá em **Settings**.
2. No fim do menu lateral, clique em **Developer settings**.
3. Clique em **Personal access tokens** e depois em **Tokens (classic)**.
4. Clique em **Generate new token** e escolha **Generate new token (classic)**.
5. Dê um nome ao token (no vídeo, `dicas 2023`) e escolha a expiração (30 dias, por exemplo, ou sem expiração).
6. Marque os escopos. Para criar issues, o essencial é o **repo**. No vídeo também foram marcados **gist** e **user**.
7. Clique em **Generate token** e copie o token, porque ele só aparece uma vez.

## Variáveis de ambiente

O arquivo `.env.sample` é só um modelo, e vai para o repositório **sem** o token:

```
# .env.sample
REPO_OWNER=rg3915
REPO_NAME=dicas-de-django
TOKEN=
```

Copie para `.env` e coloque o seu token nele:

```bash
cp .env.sample .env
```

```
# .env
REPO_OWNER=rg3915
REPO_NAME=dicas-de-django
TOKEN=********************
```

Troque `REPO_OWNER` e `REPO_NAME` pelo seu usuário e pelo seu repositório. Nunca deixe o token no `.env.sample`.

## O script `create_issue.py`

Os trechos principais de `create_issue.py` (o arquivo completo está no link logo abaixo):

```python
# create_issue.py
import click
import requests
from decouple import config

# ... (veja o arquivo completo no GitHub)

# O repositório para adicionar a issue
REPO_OWNER = config('REPO_OWNER')
REPO_NAME = config('REPO_NAME')
TOKEN = config('TOKEN')


# ... (write_file: veja o arquivo completo no GitHub)


@click.command()
@click.option('--title', prompt='Title', help='Digite o título.')
@click.option('--body', prompt='Description', help='Digite a descrição.')
# @click.option('--assignee', prompt='Assignee', help='Digite o nome da pessoa a ser associada.')
@click.option('--labels', prompt='Labels', help='Digite as labels.')
def make_github_issue(title, body=None, assignee=None, milestone=None, labels=None):
    '''
    Cria issue no github.com
    '''
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues'
    headers = {
        "Authorization": f"token {TOKEN}"
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

Código completo: [cli/create_issue.py](https://github.com/rg3915/dicas-de-django/blob/606e52221d13e7f61c6bc454d6340f35e27106c1/cli/create_issue.py)

Explicando por partes:

* **Configuração**: `config('REPO_OWNER')`, `config('REPO_NAME')` e `config('TOKEN')` leem os valores do `.env`.
* **Opções do click**: cada `@click.option` vira um parâmetro de linha de comando. O `prompt` faz o click perguntar o valor se você não passar a opção, e o `help` aparece no `--help`. A opção `--assignee` (a pessoa associada à issue) ficou comentada no vídeo, mas a função já está pronta para recebê-la.
* **URL e cabeçalho**: a issue é criada com um `POST` em `https://api.github.com/repos/{dono}/{repositório}/issues`, autenticado com o cabeçalho `Authorization: token SEU_TOKEN`.
* **Labels**: `labels.split(',')` transforma `'feature,bug'` na lista `['feature', 'bug']`, que é o formato que a API espera.
* **Resposta**: a API devolve o status `201` quando a issue é criada. Do JSON da resposta pegamos o `number`, o número da issue.
* **`write_file`**: abre o arquivo de tarefas no modo `'a'` (append, acrescenta no fim) e escreve a issue com uma caixinha `[ ]`, as labels, a descrição e, por fim, o comando que será usado para fechar a issue. Troque `/home/seu-usuario/tarefas.txt` pelo caminho da sua pasta pessoal (no vídeo é `/home/regis/tarefas.txt`).

No comando escrito no arquivo, `g` é um alias do git (no Linux, `alias g=git` no seu `~/.bashrc`) e `g co` é um alias do git para `commit`. O `make lint` será explicado num vídeo seguinte, na dica do Makefile. Ao fazer o commit com `close #número` na mensagem, o GitHub fecha a issue automaticamente.

## Usando o script

Veja as opções com `--help`:

```bash
python cli/create_issue.py --help
```

```
Usage: create_issue.py [OPTIONS]

  Cria issue no github.com

Options:
  --title TEXT   Digite o título.
  --body TEXT    Digite a descrição.
  --labels TEXT  Digite as labels.
  --help         Show this message and exit.
```

Como o script grava no arquivo de tarefas, crie-o antes, na sua pasta pessoal:

```bash
touch ~/tarefas.txt
```

Então digite:

```bash
python cli/create_issue.py \
--title='' \
--body='' \
--labels='feature'
```

No vídeo, o teste foi este:

```bash
python cli/create_issue.py --title='Teste' \
--body='Lorem ipsum' \
--labels='test'
```

```
Successfully created Issue "Teste"
```

E o arquivo de tarefas ficou assim:

```bash
cat ~/tarefas.txt
```

```

---

[ ] 92 - Teste
    test

    Lorem ipsum

    make lint; g add . ; g co -m 'Teste. close #92'; g push
```

No GitHub, a issue **#92 Teste** aparece na aba **Issues** do repositório, com a label `test` e a descrição `Lorem ipsum`.

Se você não passar as opções, o click pergunta cada uma (`Title:`, `Description:`, `Labels:`).

## Versionando sem o token

O `.env` (com o token) e a pasta `.venv` não podem ir para o repositório. Crie o `.gitignore`:

```
# .gitignore
.env
.venv
```

Confira com `git status` que o `.env` não aparece mais na lista, e faça o commit:

```bash
git status
git add .
git commit -m 'Criando Issues com API do Github. close #91'
git push --set-upstream origin aula01
```

No vídeo, o trabalho foi feito na branch `aula01`. Como ela ainda não existia no GitHub, o primeiro `git push` deu o erro `fatal: The current branch aula01 has no upstream branch.`, e por isso foi preciso usar `--set-upstream origin aula01`. O commit com `close #91` fechou a issue **#91 Criando Issues com API do Github**.

## Conclusão

Com cerca de 70 linhas de Python você cria issues no GitHub sem sair do terminal e ainda mantém uma lista de tarefas local com o comando de commit pronto. Nas próximas dicas, cada passo do projeto vai começar com uma issue criada por este script.

Observação: hoje o GitHub recomenda os tokens *fine-grained* e o cabeçalho `Authorization: Bearer SEU_TOKEN`; o token clássico com `token SEU_TOKEN`, usado no vídeo, continua funcionando.
