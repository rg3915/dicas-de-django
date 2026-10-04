# Dica 08 - Aplicando isort e autopep8

**Versões usadas no vídeo:** isort 5.10.1, autopep8 2.0.0 (com pycodestyle 2.10.0) e Python 3.10, no projeto da Dica 07 (Django 4.1.3).
{: .versoes }

<a href="https://youtu.be/A3RRHIJ0514">
    <img src="../.gitbook/assets/youtube.png">
</a>

Hoje vamos deixar o código do projeto mais organizado com duas ferramentas de linha de comando:

* O [isort](https://pycqa.github.io/isort/#installing-isort) serve para ordenar os imports.
* O [autopep8](https://pypi.org/project/autopep8/) serve para ajustar os arquivos segundo a [PEP8](https://peps.python.org/pep-0008/), o guia de estilo do Python.

Código da aula: [https://github.com/rg3915/dicas-de-django/tree/aula08](https://github.com/rg3915/dicas-de-django/tree/aula08)

## Instalação

Continuando o projeto da [Dica 07](067-07-docker-compose.md):

```bash
git checkout -b aula08

pip install isort autopep8
```

```
Collecting isort
  Using cached isort-5.10.1-py3-none-any.whl (103 kB)
Collecting autopep8
  Using cached autopep8-2.0.0-py2.py3-none-any.whl (45 kB)
Collecting tomli
  Using cached tomli-2.0.1-py3-none-any.whl (12 kB)
Collecting pycodestyle>=2.9.1
  Using cached pycodestyle-2.10.0-py2.py3-none-any.whl (41 kB)
Installing collected packages: tomli, pycodestyle, isort, autopep8
Successfully installed autopep8-2.0.0 isort-5.10.1 pycodestyle-2.10.0 tomli-2.0.1
```

Um comando bacana para guardar os dois no `requirements.txt` de uma vez: o `grep -E` aceita uma expressão regular, e o `|` significa "ou".

```bash
pip freeze | grep -E 'isort|autopep8'
```

```
autopep8==2.0.0
isort==5.10.1
```

```bash
pip freeze | grep -E 'isort|autopep8' >> requirements.txt
```

## Um arquivo para testar

Para perceber o efeito, vamos criar um arquivo bagunçado de propósito, na raiz do projeto:

```bash
touch lorem.py
```

```python
# lorem.py
import requests
import json
import click


def long_function_name(var_one, var_two, var_three, var_four, var_five, var_six, var_seven, var_eight):
    return
```

Ele tem dois problemas: os imports estão fora de ordem e a linha do `def` passa de 79 caracteres, o limite da PEP8.

## autopep8

```bash
autopep8 --in-place --aggressive --aggressive lorem.py
```

* `--in-place`: altera o próprio arquivo, em vez de só mostrar o resultado na tela.
* `--aggressive`: habilita correções mais "invasivas", como quebrar linhas longas. Repetido duas vezes, o nível de agressividade aumenta.

Resultado: os argumentos foram quebrados um por linha, para caber no limite de caracteres. Os imports continuam como estavam.

```python
# lorem.py
import requests
import json
import click


def long_function_name(
        var_one,
        var_two,
        var_three,
        var_four,
        var_five,
        var_six,
        var_seven,
        var_eight):
    return
```

Para aplicar o autopep8 em todos os arquivos Python do projeto, aceitando linhas de até 120 caracteres:

```bash
find backend -name "*.py" | xargs autopep8 --max-line-length 120 --in-place
```

O `find` lista os arquivos `.py` dentro de `backend` e o `xargs` passa essa lista como argumentos para o `autopep8`.

## isort

```bash
isort -m 3 *
```

* `*`: todos os arquivos e pastas da raiz do projeto (o isort entra nas pastas e só mexe nos `.py`).
* `-m 3`: o modo de saída 3, *vertical hanging indent*, usado quando um `from ... import` tem muitos nomes e precisa quebrar a linha:

```python
from django.urls import (
    include,
    path,
)
```

O isort separa os imports em grupos (biblioteca padrão, bibliotecas de terceiros e o código do próprio projeto), com uma linha em branco entre eles, e ordena alfabeticamente dentro de cada grupo. O resultado:

```python
# lorem.py
import json

import click
import requests


def long_function_name(
        var_one,
        var_two,
        var_three,
        var_four,
        var_five,
        var_six,
        var_seven,
        var_eight):
    return
```

Antes estava `requests`, `json`, `click`. Agora o `json` (biblioteca padrão) vem primeiro, e depois `click` e `requests` (terceiros), em ordem alfabética.

Como rodamos com `*`, ele também arrumou dois arquivos do projeto:

```
Fixing .../backend/settings.py
Fixing .../backend/core/urls.py
```

```python
# backend/settings.py (trecho)
from pathlib import Path

from decouple import Csv, config
```

```python
# backend/core/urls.py (trecho)
from django.urls import path

from backend.core import views as v
```

No `settings.py`, os nomes importados ficaram em ordem (`Csv, config`); no `urls.py`, o import do projeto (`backend.core`) foi separado do import do Django por uma linha em branco.

## Conclusão

Com o isort e o autopep8 o código fica padronizado sem esforço: imports em ordem e formatação dentro da PEP8. Vamos usar os dois daqui em diante, e na [Dica 10](070-10-makefile.md) eles viram um comando só no Makefile.
