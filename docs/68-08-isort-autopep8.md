# Dica 8 - Aplicando isort e autopep8

VIDEO EM BREVE.

O [isort](https://pycqa.github.io/isort/#installing-isort) serve para ordenar os imports.

O [autopep8](https://pypi.org/project/autopep8/) serve para ajustar os arquivos segundo a [PEP8](https://peps.python.org/pep-0008/).

```
pip install isort autopep8
pip freeze | grep -E 'isort|autopep8' >> requirements.txt
```

Para perceber o efeito vamos editar

```
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

Então rode

```
autopep8 --in-place --aggressive --aggressive lorem.py

find backend -name "*.py" | xargs autopep8 --max-line-length 120 --in-place

isort -m 3 *
```

O resultado será:

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

