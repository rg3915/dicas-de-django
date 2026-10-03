# Comandos do terminal Linux para devs Django

Publicado em 11/02/2026.

<a href="https://youtu.be/LKwDAQDrCRo">
    <img src="../.gitbook/assets/youtube.png">
</a>

Os comandos Linux que eu mais uso no dia a dia como desenvolvedor Python/Django: navegação, Git, Docker Compose, `manage.py`, ambiente virtual, processos e Makefile.

Todos os comandos: [https://gist.github.com/rg3915/2877df94d56b89ccc799238ec62670bf](https://gist.github.com/rg3915/2877df94d56b89ccc799238ec62670bf)

Este guia organiza esses comandos por categoria, com exemplos de uso e os atalhos (aliases) que deixam o trabalho mais rápido. No Windows, dá para seguir tudo pelo WSL.

## Pré-requisitos

* Um terminal Bash (Linux, macOS ou WSL).
* Git, Docker com Docker Compose e Python 3 instalados.
* Opcional: o [Bash-it](https://github.com/Bash-it/bash-it), que eu uso para personalizar o prompt, e o [bat](https://github.com/sharkdp/bat), um `cat` com destaque de sintaxe.

Uma dica antes de começar: no terminal, tudo que vem depois de `#` é comentário e não é executado. Os exemplos abaixo usam isso para explicar cada linha.

## 1. Onde ficam os atalhos

Os aliases ficam num arquivo de configuração do shell. Eu uso o `~/.bash_profile` e o carrego a partir do `~/.bashrc`:

```bash
# ~/.bashrc
source ~/.bash_profile
```

Depois de editar, feche e abra o terminal (ou rode `source ~/.bashrc`) para os aliases valerem. Se você usa Zsh, o arquivo é o `~/.zshrc`.

O conteúdo completo de aliases deste guia está no fim da página.

## 2. Navegação e manipulação de arquivos

```bash
cd <diretório>              # Mudar de diretório
cd ..                       # Voltar um nível
cd                          # Ir para o diretório home
pwd                         # Mostrar diretório atual
ls                          # Listar arquivos
ll                          # Listar com detalhes (alias de ls -lha)
tree                        # Mostrar estrutura de diretórios em árvore
mkdir <nome>                # Criar diretório
mkdir -p <path>             # Criar diretório com subdiretórios
cat <arquivo>               # Exibir conteúdo do arquivo
subl .                      # Abrir Sublime Text no diretório atual
```

* `pwd` mostra onde você está. Use sempre que se perder.
* `Ctrl+L` limpa a tela, o mesmo que `clear`.
* `tree` não vem instalado em todas as distribuições: `sudo apt install tree`.
* `mkdir -p a/b/c` cria as três pastas de uma vez, sem reclamar se alguma já existir.

Exemplo:

```bash
mkdir -p projeto/apps/core
tree projeto
cat requirements.txt
```

## 3. Git

### Aliases do próprio Git

```bash
git config --global alias.st status
git config --global alias.br branch
git config --global alias.ch checkout
git config --global alias.co commit
git config --global alias.df diff
```

Esses comandos gravam no `~/.gitconfig`. Você também pode editar o arquivo direto:

```ini
# ~/.gitconfig
[alias]
    st = status
    br = branch
    ch = checkout
    co = commit
    df = diff
```

### Aliases do shell

```bash
# ~/.bash_profile
alias g='git'
alias gp='git push'
alias gd='git diff'
alias gadd='git add . && git commit -m'
```

Combinando os dois, `g st` vira `git status`.

### Comandos do dia a dia

```bash
g clone <url>               # Clonar repositório
g st                        # git status
g br                        # git branch (listar branches)
g br -a                     # git branch -a (listar todas, incluindo remotas)
g ch <branch>               # git checkout <branch>
g ch -b <branch>            # git checkout -b (criar e mudar para nova branch)
g log                       # git log
g log --grep "#228"         # Buscar commits por mensagem
g pull                      # git pull
gp                          # git push
gd                          # git diff
gadd 'mensagem'             # git add . && git commit -m 'mensagem'
g merge <branch>            # git merge
g stash                     # git stash (guardar mudanças temporariamente)
g stash pop                 # Aplicar mudanças guardadas
```

### Fluxo completo com uma branch

```bash
g ch -b feat-git                    # cria a branch e muda para ela
# edite o README.md
gd                                  # veja o que mudou
g add README.md                     # o arquivo sai do vermelho para o verde no status
g st
g co -m 'Adiciona comentário no README'
gp --set-upstream origin feat-git   # no primeiro push da branch o Git pede este comando
g ch main                           # volta para a main
g merge feat-git                    # traz o código da feat-git para a main
```

Use o `Tab` para completar nomes de branches e arquivos: além de ser mais rápido, evita erro de digitação. Muitas empresas pedem que a branch tenha o número da tarefa no nome, por exemplo `feat-228`; aí o `g log --grep "#228"` encontra os commits dela.

## 4. Docker e Docker Compose

```bash
docker compose up -d                    # Subir containers em background
docker compose up --build -d            # Rebuild e subir containers
docker compose down                     # Parar e remover containers
docker compose logs -f                  # Ver logs em tempo real
docker compose logs -f <service>        # Logs de um serviço específico
docker compose exec <service> <cmd>     # Executar comando dentro do container
docker compose exec django_app bash     # Abrir um bash no serviço django_app
docker compose -f docker-compose.yml up -d     # Usar arquivo docker-compose específico
```

* `-d` (detached) roda em segundo plano e libera o terminal.
* Se algo der errado ao subir, recrie a imagem com `--build`.
* `-f` permite ter vários arquivos (por exemplo, um de desenvolvimento e outro de produção) e escolher qual usar.

Aliases para os comandos do `docker`:

```bash
# ~/.bash_profile
alias d='docker'
alias dcols='docker container ls'
```

```bash
dcols                                   # docker container ls (listar containers)
d container logs -f <id>                # Logs de um container pelo ID
d volume ls                             # Listar volumes
d volume ls | grep postgres             # Só os volumes com "postgres" no nome
d volume rm <volume>                    # Remover volume
d image ls                              # Listar imagens
d image rm <image>                      # Remover imagem
```

Se o `docker compose logs -f <service>` disser que o serviço não existe, pegue o ID com `dcols` e use `docker container logs -f <id>`.

Para acessar o banco PostgreSQL que roda no container:

```bash
docker container exec -it django_db psql -d django_db
```

Aqui `django_db` é o nome do container (primeiro) e o nome do banco (segundo). Troque pelos do seu projeto.

## 5. Ambiente virtual Python

```bash
python -m venv .venv                # Criar virtualenv
source .venv/bin/activate           # Ativar ambiente virtual
deactivate                          # Desativar ambiente virtual
pip install <pacote>                # Instalar pacote
pip install -r requirements.txt     # Instalar dependências
pip freeze > requirements.txt       # Gravar as versões instaladas
```

Se o `manage.py` reclamar `No module named 'django'`, quase sempre é porque a virtualenv não está ativa.

Eu crio aliases para criar e ativar a virtualenv:

```bash
# ~/.bash_profile
alias venv='python -m venv .venv'
alias sa='source .venv/bin/activate'
alias pf='pip freeze'
```

```bash
venv        # cria a .venv
sa          # ativa
pf | grep -i django   # mostra só os pacotes com "django" no nome
```

## 6. Django (manage.py)

```bash
python manage.py makemigrations             # Criar migrations
python manage.py migrate                    # Aplicar migrations
python manage.py runserver                  # Rodar servidor
python manage.py runserver 8001             # Rodar em porta específica
python manage.py createsuperuser            # Criar superusuário
python manage.py shell_plus                 # Shell interativo com models carregados
python manage.py show_urls                  # Mostrar todas urls do projeto
python manage.py                            # Listar todos os comandos disponíveis
```

O alias mais útil de todos:

```bash
# ~/.bash_profile
alias r='python manage.py runserver'
```

```bash
r           # sobe o servidor na porta 8000
r 8001      # o alias aceita argumentos: sobe na porta 8001
```

O `shell_plus` e o `show_urls` vêm do **django-extensions**. Instale e registre no `settings.py`:

```bash
pip install django-extensions
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'django_extensions',
]
```

O `show_urls` lista cada rota, a view que a atende e o nome da rota. Em um projeto que você acabou de pegar, é o primeiro comando a rodar.

## 7. Busca e filtros

```bash
grep <pattern> <arquivo>                # Buscar padrão em arquivo
ps aux | grep <processo>                # Buscar processo específico
ps aux | grep :8000                     # Buscar processo na porta 8000
lsof -i :8000                           # Ver o que está usando a porta 8000
pf | grep <pacote>                      # Buscar pacote instalado
```

O `|` (pipe) manda a saída de um comando para o próximo. Caso clássico: o `runserver` diz que a porta 8000 já está em uso.

```bash
lsof -i :8000      # mostra o PID do processo que ocupa a porta
kill <PID>         # encerra o processo
```

## 8. Processos e sistema

```bash
crontab -l                  # Listar cron jobs
crontab -e                  # Editar cron jobs
```

O cron executa comandos em horários agendados, por exemplo um backup do banco toda madrugada.

## 9. Makefile

O `make` transforma sequências de comandos em atalhos do projeto. Este é o `Makefile` do projeto [django-experience](https://github.com/rg3915/django-experience):

```makefile
# Makefile
indenter:
	find backend -name "*.html" | xargs djhtml -t 2 -i

autopep8:
	find backend -name "*.py" | xargs autopep8 --max-line-length 120 --in-place

isort:
	isort -m 3 *

lint: autopep8 isort indenter
```

```bash
make lint       # roda autopep8, isort e djhtml, nessa ordem
```

Atenção: a indentação das linhas de comando no Makefile tem que ser com **Tab**, não com espaços.

Nos projetos mais novos eu uso o Ruff no lugar do autopep8 e do isort, com um alvo `make ruff`. Um exemplo de alvo:

```makefile
ruff:
	ruff check --fix .
	ruff format .
```

## 10. Arquivo de aliases completo

```bash
# ~/.bash_profile
alias ll='ls -lha'

# Git
alias g='git'
alias gp='git push'
alias gd='git diff'
alias gadd='git add . && git commit -m'

# Docker
alias d='docker'
alias dcols='docker container ls'

# Python
alias venv='python -m venv .venv'
alias sa='source .venv/bin/activate'
alias pf='pip freeze'

# Django
alias r='python manage.py runserver'
```

## Testando

Abra um terminal novo e confira:

```bash
alias          # lista todos os aliases carregados
type r         # mostra para o que o "r" aponta
```

Comece pelos aliases de que você mais precisa (`r`, `sa`, `g`) e vá acrescentando os outros conforme a necessidade.
