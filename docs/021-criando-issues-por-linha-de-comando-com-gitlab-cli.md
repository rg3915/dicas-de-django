# Dica 21 - Criando issues por linha de comando com gitlab cli

**Versões usadas no vídeo:** esta dica não usa Django; Python 3.8, python-gitlab 2.4.0, click 7.1.2 e python-decouple 3.3.
{: .versoes }

<a href="https://youtu.be/mZezRjHv4Xg">
    <img src="../.gitbook/assets/youtube.png">
</a>

Doc: [https://python-gitlab.readthedocs.io/en/stable/](https://python-gitlab.readthedocs.io/en/stable/)

Continuando a série de criar issues pela linha de comando (veja as dicas [19](019-criando-issues-por-linha-de-comando-com-a-api-do-github.md) e [20](020-api-github-e-click.md), com o GitHub), agora vamos fazer o mesmo no **GitLab**. Em vez de montar as requisições à mão com `requests`, vamos usar a biblioteca [python-gitlab](https://python-gitlab.readthedocs.io/en/stable/), que já encapsula a API do GitLab. Primeiro testamos no shell do Python e depois criamos um script com Click.


## Configuração

A python-gitlab lê os dados de conexão (endereço do servidor e token) de um arquivo de configuração. Primeiro precisamos criar um arquivo `/etc/myfile.cfg`

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

* `[global]`: opções gerais. `default` é a seção usada quando nenhuma é informada, `ssl_verify = true` verifica o certificado HTTPS e `timeout = 5` é o tempo máximo, em segundos, de cada requisição.
* `[somewhere]`: uma seção com os dados de um servidor. O nome é livre; é ele que vamos passar para o `from_config`. `url` é o endereço do GitLab, `private_token` é o seu token de acesso e `api_version = 4` é a versão da API.

### Gerando o token

No GitLab, vá em **User Settings > Access Tokens** (clique no seu avatar, **Settings**, e depois **Access Tokens** no menu lateral):

1. Em **Name**, digite um nome para o token.
2. Em **Scopes**, marque **api** (acesso completo de leitura e escrita à API).
3. Clique em **Create personal access token** e copie o token gerado para o `private_token` do arquivo acima.

### O ID do projeto

Para criar issues, precisamos do ID do projeto no GitLab. Ele aparece na página inicial do projeto, logo abaixo do nome (**Project ID: ...**), e também em **Settings > General**. No vídeo, o projeto é `gitlab.com/rg3915/dicas`.

Guarde esse ID no arquivo `.env` do projeto, que será lido pelo `python-decouple`:

```
# .env
GITLAB_PROJECT_ID=xxxxxxxx
```

## Instalação

`pip install python-gitlab`

Para o script com Click, também:

```bash
pip install click python-decouple
```


## Fazendo um teste no Python

Abra o shell do Python (`python`) e liste as issues:

```python
import gitlab

gl = gitlab.Gitlab.from_config('somewhere', ['/etc/myfile.cfg'])

issues = gl.issues.list()
for issue in issues:
    print(issue.iid, issue.title)
```

* `gitlab.Gitlab.from_config('somewhere', ['/etc/myfile.cfg'])` cria a conexão usando a seção `somewhere` do arquivo de configuração.
* `gl.issues.list()` traz as issues do usuário autenticado.
* `issue.iid` é o número da issue **dentro do projeto** (o `#5` que aparece no GitLab); `issue.id` seria o identificador global.

## Criando issues

Para criar uma issue, pegamos o projeto pelo ID e usamos `project.issues.create`, passando um dicionário com o título e a descrição:

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

Troque `ID-DO-PROJETO` pelo ID do seu projeto. Atualizando a página **Issues** do projeto no GitLab, aparece a issue **I have a bug** (no vídeo, a #5), com a descrição "Lorem ipsum...".

## gitlab + click

Agora vamos juntar tudo num script com Click, como fizemos com o GitHub na [Dica 20](020-api-github-e-click.md). Crie o arquivo `gitlab_cli.py`:

```python
# gitlab_cli.py
import click
import gitlab
from decouple import config

'''
Usage: python gitlab_cli.py --title='Your title' --description='Your description'
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

* A conexão (`gl`) e o projeto (`project`) são criados uma vez, no início. O ID do projeto vem do `.env` com `config('GITLAB_PROJECT_ID')`.
* `@click.command()` e os dois `@click.option` transformam `create_issue` num comando com as opções `--title` e `--description`. Se alguma não for informada, o Click pergunta (`prompt`).
* `project.issues.create(...)` devolve a issue criada; com `click.echo` mostramos o número (`iid`) e o título dela.

Rodando:

```bash
python gitlab_cli.py --title='Your title' --description='Your description'
```

A saída é o número e o título da issue criada (no vídeo, a issue #6, **Your title**, com a descrição "Your description"). Sem as opções, o Click pergunta `Title:` e `Description:`.

No vídeo, as primeiras execuções deram dois erros de digitação:

* `SyntaxError: invalid syntax` em `@click.option('--title', prompt='Title', help'Type the title.')`: faltou o `=` em `help=`.
* `SyntaxError: closing parenthesis ')' does not match opening parenthesis '{'`: faltou fechar a chave `}` do dicionário antes do `)`.

## Conclusão

Com a python-gitlab, criar issues no GitLab pelo terminal fica ainda mais simples do que com o `requests`: um arquivo de configuração com o token, o ID do projeto e `project.issues.create`. Na próxima dica fazemos o mesmo com o [Bitbucket](022-criando-issues-por-linha-de-comando-com-bitbucket-cli.md).
