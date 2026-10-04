# Dica 33 - Github cli

**Versões usadas no vídeo:** esta dica não usa Django; GitHub CLI (`gh`) 1.x, de abril de 2021, no Linux.
{: .versoes }

<a href="https://youtu.be/Y5VO3u2hp10">
    <img src="../.gitbook/assets/youtube.png">
</a>

O [GitHub CLI](https://cli.github.com/) é a ferramenta oficial do GitHub para a linha de comando. Com o comando `gh` você clona repositórios, vê o README, cria e lista issues, abre e acompanha pull requests, tudo sem sair do terminal.

Nas dicas [19](019-criando-issues-por-linha-de-comando-com-a-api-do-github.md) e [20](020-api-github-e-click.md) criamos issues pelo terminal com um script Python que chamava a API do GitHub. O `gh` faz isso (e muito mais) pronto.

## Instalação

No site [https://cli.github.com/](https://cli.github.com/) estão as instruções de instalação para Linux (várias distribuições), macOS e Windows. Depois de instalar, confira:

```bash
gh --version
```

## Os principais comandos

```bash
gh auth login
gh repo clone rg3915/dicas-de-django
gh repo view
gh pr checks
gh pr create
gh pr status
gh pr merge
gh issue list
```

* `gh auth login`: faz login na sua conta do GitHub.
* `gh repo clone`: clona um repositório (equivale a `git clone https://github.com/rg3915/dicas-de-django.git`).
* `gh repo view`: mostra a descrição e o README do repositório da pasta atual.
* `gh pr checks`: mostra o resultado dos testes (CI) do pull request da branch atual.
* `gh pr create`: cria um pull request da branch atual.
* `gh pr status`: mostra a situação dos seus pull requests.
* `gh pr merge`: faz o merge de um pull request.
* `gh issue list`: lista as issues abertas do repositório.

## Fazendo login

```bash
gh auth login
```

O `gh` faz algumas perguntas no terminal (use as setas para escolher):

```
? What account do you want to log into?  [Use arrows to move, type to filter]
> GitHub.com
  GitHub Enterprise Server
```

No vídeo foram escolhidos **GitHub.com**, o protocolo **HTTPS** e o login **pelo navegador** (*Login with a web browser*). O `gh` mostra um código de uso único; ao apertar Enter, abre o navegador na página **Device Activation** do GitHub, onde você digita o código, autoriza o **GitHub CLI** (*Authorize GitHub CLI*) e confirma com a sua senha. No fim aparece "Congratulations, you're all set!" e o terminal já está logado.

## Repositório e pull requests

Para clonar um repositório:

```bash
gh repo clone rg3915/dicas-de-django
```

(No vídeo o comando não foi executado, porque o repositório já estava clonado.)

Dentro da pasta do repositório:

```bash
gh repo view
```

mostra o nome, a descrição e o README do projeto direto no terminal.

```bash
gh pr checks
```

Como não havia nenhum pull request aberto, a saída foi:

```
no pull requests found for branch "master"
```

## Listando issues

```bash
gh issue list
```

Mostra as issues abertas, com número, título, labels e há quanto tempo foram criadas. Por exemplo, depois de criar as issues da próxima seção, a saída no vídeo foi:

```
Showing 7 of 7 open issues in rg3915/dicas-de-django

#36  Github cli                                     (enhancement)  less than a minute ago
#35  Github cli                                     (enhancement)  about 1 minute ago
#34  Github cli                                                    about 1 minute ago
#29  Django: Paginação + filtros                                   about 1 month ago
#28  Django: Visualizando seus modelos com graph mo...             about 1 month ago
#27  Django: Passando usuário logado no formulário                 about 1 month ago
#26  Django: Custom template tags                                  about 1 month ago
```

## Criando issues

Para criar uma issue, use `gh issue create` com as opções:

* `--title`: o título;
* `--body`: a descrição;
* `--label`: as labels (separe várias com vírgula, por exemplo `"bug,enhancement"`; as labels precisam existir no repositório);
* `--assignee`: o responsável. `"@me"` é você mesmo.

```bash
gh issue create --title "Github cli" --body "Experimentar Github cli https://cli.github.com" \
--label "enhancement" \
--assignee "@me"
```

A `\` no fim da linha quebra o comando em várias linhas no terminal. Atenção: se você apertar Enter sem a `\`, o comando já roda com o que foi digitado até ali. Foi o que aconteceu no vídeo na primeira tentativa: a issue #34 foi criada só com título e descrição.

(No vídeo foi usado `--title="Github cli"`, com `=`; as duas formas funcionam.)

O `gh` mostra `Creating issue in rg3915/dicas-de-django` e, em seguida, o endereço da issue criada. Abrindo o link, a issue #35 está lá, com a descrição, a label `enhancement` e atribuída ao próprio usuário.

As mesmas opções têm versões abreviadas: `-t` (title), `-b` (body), `-l` (label) e `-a` (assignee). Dá também para quebrar a linha dentro das aspas da descrição:

```bash
gh issue create -t "Github cli" -b "Experimentar Github cli
https://cli.github.com" \
-l "enhancement" \
-a "@me"
```

Isso criou a issue #36.

## Fechando issues pelo commit

Para fechar issues não é preciso o `gh`: basta escrever `close #número` na mensagem de commit. Quando o commit chega na branch principal do GitHub, a issue é fechada e ganha um link para o commit.

```bash
git add .
git commit -m 'Usando o github cli. close #34'
git push
```

Para fechar várias de uma vez, repita o `close` para cada uma. No vídeo, as três issues criadas foram fechadas assim:

```bash
git add .
git commit -m 'Usando o github cli. close #34 close #35 close #36'
git push
```

Atualizando a página de issues do repositório, as issues #34, #35 e #36 aparecem fechadas.

## Conclusão

Com o `gh` você resolve pelo terminal boa parte do que faria no site do GitHub: login, clone, README, issues e pull requests. Veja todos os comandos com `gh help` ou em [https://cli.github.com/](https://cli.github.com/).
