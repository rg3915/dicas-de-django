# Dica 24 - Barra de progresso

**Versões usadas no vídeo:** esta dica não usa Django; Python 3.8, progress 1.5, tqdm 4.56, click 7.1.2, progressbar2 3.53.1, clint 0.5.1 e httpx 0.16.1 (no Jupyter Notebook).
{: .versoes }

<a href="https://youtu.be/YQlwWn48eTw">
    <img src="../.gitbook/assets/youtube.png">
</a>


* [progress](https://pypi.org/project/progress/)
* [tqdm](https://tqdm.github.io/)
* [click](https://click.palletsprojects.com/en/7.x/) - [click progressbar](https://click.palletsprojects.com/en/7.x/utils/#showing-progress-bars)
* [progressbar 2](https://progressbar-2.readthedocs.io/en/latest/index.html)
* [clint](https://github.com/kennethreitz-archive/clint)
* [with sys](https://stackoverflow.com/a/3160819)
* [gist rg3915](https://gist.github.com/rg3915/b6368374f74d00d9ea045470718a8ddd)
* [progressbar on Jupyter notebook](https://opensource.com/article/20/12/tqdm-python)

Leia mais em [How to Easily Use a Progress Bar in Python](https://codingdose.info/posts/how-to-use-a-progress-bar-in-python/)

Quando um script demora (importar uma planilha, processar milhares de registros, baixar um arquivo), uma barra de progresso mostra ao usuário que o programa não travou e quanto ainda falta. Neste tutorial vamos ver **oito jeitos** de fazer uma barra de progresso em Python: cinco bibliotecas prontas (progress, tqdm, click, progressbar2 e clint), dois jeitos só com a biblioteca padrão (`sys`) e, por fim, a barra dentro do Jupyter Notebook, inclusive acompanhando o download de um arquivo.

Todos os exemplos seguem a mesma ideia: um laço `for` de 100 voltas com um `sleep` curto, que faz o papel do "trabalho de verdade" (no lugar do `sleep` entraria, por exemplo, o processamento de cada linha de um arquivo).

## Pré-requisitos

* Python 3 (no vídeo, Python 3.8) com um ambiente virtual ativado.
* Uma pasta para os exemplos. No vídeo ela se chama `progressbar`, dentro do repositório [dicas-de-django](https://github.com/rg3915/dicas-de-django):

```bash
python -m venv .venv
source .venv/bin/activate
mkdir progressbar
cd progressbar
```

Cada biblioteca é instalada na hora em que for usada. Se preferir instalar tudo de uma vez, com as versões do vídeo:

```bash
pip install progress==1.5 tqdm==4.56.0 click==7.1.2 progressbar2==3.53.1 clint==0.5.1
```

## 1. progress

A biblioteca [progress](https://pypi.org/project/progress/) é a mais simples: você cria uma `Bar` com um texto e chama `bar.next()` a cada passo.

```bash
pip install progress
```

```python
# example01_progress.py
from time import sleep
from progress.bar import Bar

with Bar('Processing...') as bar:
    for i in range(100):
        sleep(0.02)
        bar.next()
```

* `Bar('Processing...')` cria a barra com o rótulo que aparece à esquerda. Por padrão, o total é 100 (parâmetro `max`).
* Usar `with` garante que a barra seja finalizada (`bar.finish()`) no fim do bloco.
* `bar.next()` avança um passo.

```bash
$ python example01_progress.py
Processing... |################################| 100/100
```

## 2. tqdm

O [tqdm](https://tqdm.github.io/) é provavelmente a biblioteca de barra de progresso mais usada em Python. Basta "embrulhar" qualquer iterável com `tqdm()`.

```bash
pip install tqdm
```

No vídeo foi instalado o `tqdm-4.56.0`.

```python
# example02_tqdm.py
from tqdm import tqdm
from time import sleep

for i in tqdm(range(100)):
    sleep(0.02)
    # Do something
```

```bash
$ python example02_tqdm.py
100%|██████████| 100/100 [00:02<00:00, 36.78it/s]
```

Além da porcentagem e da barra, o tqdm mostra o tempo decorrido, o tempo estimado que falta e a velocidade (iterações por segundo).

## 3. click

O [click](https://click.palletsprojects.com/en/7.x/) é uma biblioteca para criar interfaces de linha de comando (usamos ele na [dica 20](020-api-github-e-click.md)), e ele tem a sua própria [barra de progresso](https://click.palletsprojects.com/en/7.x/utils/#showing-progress-bars).

```bash
pip install click
```

```python
# example03_click.py
import click
from time import sleep

# Fill character is # by default, you can change it
# for any other char you want, or even change the color.
fill_char = click.style('=', fg='yellow')
with click.progressbar(range(100), label='Loading...', fill_char=fill_char) as bar:
    for i in bar:
        sleep(0.02)
```

* `click.style('=', fg='yellow')` cria o caractere de preenchimento: um sinal de igual em amarelo (`fg` é a cor do texto, *foreground*). O padrão seria `#`.
* `click.progressbar()` recebe o iterável, o rótulo (`label`) e o caractere de preenchimento (`fill_char`), e é usado com `with`. Dentro do bloco, você percorre `bar` em vez do `range`.

```bash
$ python example03_click.py
Loading...  [====================================]  100%
```

## 4. progressbar2

```bash
pip install progressbar2
```

Atenção: o pacote se chama `progressbar2` no `pip`, mas o módulo importado é `progressbar`.

```python
# example04_progressbar2.py
from time import sleep
from progressbar import progressbar

for i in progressbar(range(100)):
    sleep(0.02)
```

```bash
$ python example04_progressbar2.py
100% (100 of 100) |######################| Elapsed Time: 0:00:02 Time:  0:00:02
```

## 5. clint

O [clint](https://github.com/kennethreitz-archive/clint) é um conjunto de ferramentas para aplicações de terminal. O módulo `clint.textui.progress` tem dois estilos: a barra normal (`progress.bar`) e o `progress.mill`, um indicador que fica girando na tela (`| / - \`) ao lado do contador.

```bash
pip install clint
```

```python
# example05_clint.py
from time import sleep
from clint.textui import progress

print('Clint - Regular Progress Bar')
for i in progress.bar(range(100)):
    sleep(0.02)

print('Clint - Mill Progress Bar')
for i in progress.mill(range(100)):
    sleep(0.02)
```

```bash
$ python example05_clint.py
Clint - Regular Progress Bar
[################################] 100/100 - 00:00:02
Clint - Mill Progress Bar
   100/100
```

Durante a execução do segundo laço, o caractere antes do contador vai girando.

## 6. Só com Python, usando sys

Dá para fazer uma barra de progresso sem instalar nada, só com a biblioteca padrão. Esta versão é baseada [nesta resposta do Stack Overflow](https://stackoverflow.com/a/3160819):

```python
# example06_sys.py
import time
import sys

toolbar_width = 40

# setup toolbar
sys.stdout.write("[%s]" % (" " * toolbar_width))
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width + 1))  # return to start of line, after '['

for i in range(toolbar_width):
    time.sleep(0.1)  # do real work here
    # update the bar
    sys.stdout.write("-")
    sys.stdout.flush()

sys.stdout.write("]\n")  # this ends the progress bar
```

Como funciona:

* Primeiro escrevemos a "moldura" vazia: `[` + 40 espaços + `]`.
* `sys.stdout.flush()` força o texto a aparecer na tela na hora (sem ele, o Python guarda a saída num buffer).
* `"\b"` é o caractere de *backspace*: escrevê-lo 41 vezes volta o cursor para logo depois do `[`.
* A cada volta do laço escrevemos um `-`, que vai preenchendo a moldura por cima dos espaços.
* No fim, `"]\n"` fecha a barra e pula a linha.

```bash
$ python example06_sys.py
[----------------------------------------]
```

Cuidado com a digitação: no vídeo, a variável foi declarada primeiro como `toolbar_with` (sem o "d"), e a execução deu erro:

```
Traceback (most recent call last):
  File "example06_sys.py", line 7, in <module>
    sys.stdout.write("[%s]" % (" " * toolbar_width))
NameError: name 'toolbar_width' is not defined
```

O erro aponta a linha 7, mas o problema está na linha 4, onde a variável foi criada com o nome errado. Corrigindo para `toolbar_width`, funciona.

## 7. Uma função de barra de progresso reutilizável (gist)

Esta é a versão que está no [gist do Regis](https://gist.github.com/rg3915/b6368374f74d00d9ea045470718a8ddd): uma função geradora `progressbar()` que você usa em volta de qualquer lista ou `range`, como o `tqdm`, só que sem dependências.

```python
# example07_sys.py
import sys
import time


def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)

    def show(j):
        x = int(size * j / count)
        file.write("%s[%s%s] %i/%i\r" %
                   (prefix, "#" * x, "." * (size - x), j, count))
        file.flush()
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i + 1)
    file.write("\n")
    file.flush()


users = ['Regis', 'Abel', 'Eduardo', 'Elaine']


for user in progressbar(users, "Processing: "):
    time.sleep(0.1)
    # Do something.


for i in progressbar(range(42), "Processing: "):
    time.sleep(0.05)
    # Do something.
```

Explicando a função:

* `it` é o iterável (precisa ter tamanho, por causa do `len(it)`); `prefix` é o texto antes da barra; `size` é a largura da barra em caracteres; `file` é onde escrever (a saída padrão).
* `show(j)` desenha a barra no passo `j`: calcula quantos `#` cabem (`x = int(size * j / count)`), completa o resto com `.` e mostra o contador `j/count`. O `\r` (*carriage return*) volta o cursor para o início da linha, então cada desenho sobrescreve o anterior.
* `show(0)` desenha a barra vazia; depois, para cada item, a função faz `yield item` (devolve o item para o seu `for`) e redesenha a barra com `show(i + 1)`.
* No fim, `\n` pula a linha para a barra não ser sobrescrita pelo próximo texto.

No exemplo, a primeira barra percorre a lista de nomes (4 itens) e a segunda percorre um `range` de 0 a 42:

```bash
$ python example07_sys.py
Processing: [############################################################] 4/4
Processing: [############################################################] 42/42
```

## 8. Barra de progresso no Jupyter Notebook

O tqdm também funciona dentro do [Jupyter Notebook](https://opensource.com/article/20/12/tqdm-python), com uma barra gráfica (verde quando termina).

```bash
$ jupyter notebook
```

No navegador, clique em **New > Python 3** para criar um notebook. Na primeira célula, importe o tqdm de um jeito que funciona tanto no notebook quanto num script comum:

```python
# progressbar_jupyter.ipynb (célula 1)
import sys
if hasattr(sys.modules["__main__"], "get_ipython"):
    from tqdm import notebook as tqdm
else:
    import tqdm
from time import sleep
```

Se o código estiver rodando dentro do IPython/Jupyter (o módulo `__main__` tem a função `get_ipython`), usamos `tqdm.notebook`, que desenha a barra como um *widget*; senão, o `tqdm` normal, de texto. Rode a célula com **Shift + Enter**.

```python
# célula 2
n = 0
for i in tqdm.trange(100):
    n += 1
    sleep(0.01)
```

`tqdm.trange(100)` é um atalho para `tqdm.tqdm(range(100))`. A saída é uma barra verde:

```
100% ████████████████████ 100/100 [00:01<00:00, 92.26it/s]
```

### Acompanhando um download

Um uso bem prático: mostrar o progresso do download de um arquivo. Vamos baixar o código-fonte do Python 3.9.0 com o [httpx](https://www.python-httpx.org/):

```python
# célula 3
url = "https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tgz"
```

```python
# célula 4
import httpx
```

Se o httpx não estiver instalado, essa célula dá `ModuleNotFoundError: No module named 'httpx'`. Dá para instalar sem sair do notebook, numa célula nova:

```python
%pip install httpx
```

No vídeo foi instalado o `httpx-0.16.1`. Depois da instalação, reinicie o kernel (menu **Kernel > Restart & Run All**) para que o pacote novo seja reconhecido, apague a célula do `%pip` e rode tudo de novo.

```python
# célula 5
with httpx.stream("GET", url) as response:
    total = int(response.headers["Content-Length"])
    with tqdm.tqdm(total=total) as progress:
        for chunk in response.iter_bytes():
            progress.update(len(chunk))
```

* `httpx.stream()` faz a requisição sem baixar tudo para a memória de uma vez.
* O cabeçalho `Content-Length` diz o tamanho total do arquivo em bytes; ele vira o `total` da barra.
* `response.iter_bytes()` entrega o arquivo em pedaços (*chunks*); a cada pedaço, `progress.update(len(chunk))` avança a barra pelo número de bytes recebidos.

Enquanto o arquivo baixa, a barra mostra algo como `63% ... 16752028/26724009 [00:04<00:02, ...]` e chega a 100% no fim.

Aqui o exemplo só mostra o progresso; para salvar o arquivo, você escreveria cada `chunk` num arquivo aberto em modo `wb`.

## Resumo

| Jeito | Instalação | Uso |
|---|---|---|
| progress | `pip install progress` | `with Bar('...') as bar:` + `bar.next()` |
| tqdm | `pip install tqdm` | `for i in tqdm(iteravel):` |
| click | `pip install click` | `with click.progressbar(iteravel) as bar:` |
| progressbar2 | `pip install progressbar2` | `for i in progressbar(iteravel):` |
| clint | `pip install clint` | `progress.bar(iteravel)` ou `progress.mill(iteravel)` |
| sys | nada | `sys.stdout.write` + `flush` |
| função do gist | nada | `for item in progressbar(iteravel, "Processing: "):` |
| Jupyter | `pip install tqdm` | `from tqdm import notebook as tqdm` |

Observação: o clint foi arquivado pelo autor e não recebe mais atualizações; para projetos novos, o tqdm é a escolha mais comum.
