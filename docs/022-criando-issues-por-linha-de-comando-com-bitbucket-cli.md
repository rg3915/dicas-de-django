# Dica 22 - Criando issues por linha de comando com bitbucket cli

**Versões usadas no vídeo:** esta dica não usa Django; Python 3.8, bitbucket-python 0.2.2, click 7.1.2 e python-decouple 3.3.
{: .versoes }

<a href="https://youtu.be/N2oYZxixcSU">
    <img src="../.gitbook/assets/youtube.png">
</a>

**OBSOLETO:** esta dica está marcada como obsoleta. O texto abaixo descreve o que o vídeo mostra, em 2020; veja a observação no fim antes de tentar rodar hoje.

Esta é a última parte da série sobre criar issues pela linha de comando: já vimos o GitHub ([Dica 19](019-criando-issues-por-linha-de-comando-com-a-api-do-github.md) e [Dica 20](020-api-github-e-click.md)) e o GitLab ([Dica 21](021-criando-issues-por-linha-de-comando-com-gitlab-cli.md)). Agora é a vez do **Bitbucket**, usando a biblioteca [bitbucket-python](https://pypi.org/project/bitbucket-python/0.2.2/), um *wrapper* em Python da [API do Bitbucket](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-issue-tracker/#api-repositories-workspace-repo-slug-issues-post). Primeiro testamos no shell do Python e depois criamos um script com Click.


## Instalação

`pip install bitbucket-python`

Para o script com Click, também:

```bash
pip install click python-decouple
```


## Usando com Python

> Lembre-se de habilitar a criação de issues no repositório.

No Bitbucket, o repositório novo vem **sem** issue tracker. No vídeo o repositório é `bitbucket.org/rg3915/dicas`. Para habilitar:

1. Abra o repositório e vá em **Repository settings**.
2. Em **Issues > Issue tracker**, troque **No issue tracker** por **Private issue tracker** (só quem tem acesso ao repositório vê) ou **Public issue tracker** (qualquer um pode ver, criar e comentar). No vídeo foi escolhido o público.
3. Clique em **Save**. A partir daí aparece o item **Issues** no menu do repositório.

Depois, no arquivo `.env` do projeto, coloque o e-mail e a senha da conta do Bitbucket e o nome do repositório no formato de *slug* (no vídeo, apenas `dicas`):

```
# .env
BITBUCKET_EMAIL=seu-email@exemplo.com
BITBUCKET_PASSWORD=xxxxxxxxxxxxxxxxxxxxxxxx
REPOSITORY_SLUG=dicas
```

Agora, no shell do Python (`python`):

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

* `Client(email, password)` cria o cliente autenticado. Ele já consulta a API na criação, para descobrir o seu nome de usuário, que é o dono (*workspace*) dos repositórios.
* `client.get_repository(repository_slug)` traz os dados do repositório; serve para conferir que a conexão e o slug estão certos.
* `data` é o corpo da issue, no formato da API do Bitbucket: `title` é o título, `content` é a descrição (o texto vai na chave `raw`) e `kind` é o tipo. A documentação da API lista os tipos aceitos: `bug`, `enhancement`, `proposal` e `task`; os mais usados são `task` e `bug`.
* `client.create_issue(repository_slug, data)` faz o `POST` e devolve a issue criada, como um dicionário.

Na página **Issues** do repositório aparece a issue **#1 Your title**, do tipo *task*, com a descrição "Your description" (a prioridade fica como *major*, o padrão).

## Usando com click

Agora o script `bitbucket_cli.py`, com as opções `--title`, `--description` e `--kind`:

```python
# bitbucket_cli.py
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

* Diferente da versão do GitLab, aqui as configurações e o cliente são criados **dentro** da função, só quando o comando roda.
* Os três `@click.option` viram os parâmetros `title`, `description` e `kind` da função; o que não for passado na linha de comando, o Click pergunta.
* Como a resposta é um dicionário, mostramos o título com `response['title']`.

Rodando:

```bash
python bitbucket_cli.py --title='Your title' --description='Your description' --kind='task'
```

O comando mostra o título da issue criada, e no Bitbucket aparece a issue **#2**, agora criada pelo Click.

## Conclusão

Com isso fechamos os quatro vídeos sobre criar issues pelo terminal: GitHub com `requests`, GitHub com Click, GitLab com `python-gitlab` e Bitbucket com `bitbucket-python`. A ideia é sempre a mesma: autenticar, montar um dicionário com os dados da issue e enviar para a API do serviço.

Observação: esta dica está obsoleta. Hoje o Bitbucket não aceita mais a senha da conta para acessar a API (é preciso um token de acesso criado nas configurações da conta), e a bitbucket-python mudou a classe `Client` nas versões 0.3.x (ela passou a aceitar `token`, `client_id` e `client_secret`, além de usuário e senha).
