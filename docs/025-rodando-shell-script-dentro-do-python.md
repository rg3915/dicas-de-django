# Dica 25 - Rodando Shell script dentro do Python

**Versões usadas no vídeo:** esta dica não usa Django; Python 3.8 (só a biblioteca padrão) no Linux.
{: .versoes }

<a href="https://youtu.be/r3MIUX2QTEI">
    <img src="../.gitbook/assets/youtube.png">
</a>


Para rodar Shell script dentro do Python só precisamos do [subprocess](https://docs.python.org/3/library/subprocess.html).

O módulo `subprocess` faz parte da biblioteca padrão, então não há nada para instalar. Com ele, o Python executa comandos do terminal (`echo`, `cat`, `wc`, `notify-send` ou qualquer outro programa) como se você os digitasse no shell. Neste tutorial vamos escrever um script que imprime textos, mostra uma notificação na área de trabalho, grava uma sequência de números gerada pelo Python num arquivo, lê esse arquivo e conta as suas linhas, tudo com comandos de shell.

## Pré-requisitos

* Python 3.6 ou superior (o script usa f-strings).
* Linux. O comando `notify-send`, que mostra a notificação, existe nas distribuições com GNOME e similares (no Ubuntu, vem no pacote `libnotify-bin`). Os outros comandos (`echo`, `cat`, `wc`) funcionam também no macOS.

## O script completo

Crie o arquivo `subprocess01.py`:

```python
# subprocess01.py
import subprocess
from datetime import datetime


subprocess.call('echo "Hello"', shell=True)

subprocess.run('echo "Running"', shell=True)

now = datetime.now()

subprocess.run(f'notify-send --urgency=LOW "{now}"', shell=True)


def write_numbers(n):
    return ' '.join([str(i) for i in range(n)])


# print(write_numbers(5))

subprocess.run(f'echo {write_numbers(10)} > /tmp/numbers.txt', shell=True)
subprocess.run('cat /tmp/numbers.txt', shell=True)

subprocess.run('wc -l /tmp/numbers.txt', shell=True)
```

## Explicando cada parte

### `subprocess.call` e `subprocess.run`

```python
subprocess.call('echo "Hello"', shell=True)

subprocess.run('echo "Running"', shell=True)
```

São as duas opções mostradas no vídeo, e as duas executam o comando e esperam ele terminar:

* `subprocess.call()` é a forma antiga; devolve só o código de saída do comando (`0` quando deu certo).
* `subprocess.run()` é a forma recomendada desde o Python 3.5; devolve um objeto `CompletedProcess`, com o código de saída (`returncode`) e, se você pedir com `capture_output=True`, a saída do comando (`stdout`).

O parâmetro `shell=True` faz o comando ser interpretado por um shell (`/bin/sh`), por isso podemos passar tudo numa string só e usar recursos do shell como o redirecionamento `>`. Sem `shell=True`, o comando teria que ser passado como lista: `subprocess.run(['echo', 'Running'])`.

### Uma notificação na área de trabalho

```python
now = datetime.now()

subprocess.run(f'notify-send --urgency=LOW "{now}"', shell=True)
```

Aqui juntamos Python e shell: pegamos a data e hora atual com o `datetime` e passamos o valor para o comando `notify-send`, usando uma f-string. `--urgency=LOW` define a notificação como de baixa prioridade. Ao rodar, aparece um aviso na área de trabalho com a data e a hora, por exemplo `2021-01-16 05:57:54.777901`.

### Passando o resultado de uma função Python para o shell

```python
def write_numbers(n):
    return ' '.join([str(i) for i in range(n)])
```

A função `write_numbers(n)` usa uma *list comprehension* para gerar os números de `0` a `n - 1`, converte cada um para texto e junta tudo separado por espaço. `write_numbers(5)` devolve `'0 1 2 3 4'` (a linha comentada `# print(write_numbers(5))` serve para testar isso).

```python
subprocess.run(f'echo {write_numbers(10)} > /tmp/numbers.txt', shell=True)
subprocess.run('cat /tmp/numbers.txt', shell=True)
```

* O primeiro comando vira `echo 0 1 2 3 4 5 6 7 8 9 > /tmp/numbers.txt`: o `echo` escreve a sequência e o `>` grava o resultado no arquivo `/tmp/numbers.txt`.
* O segundo lê o arquivo com `cat` e mostra o conteúdo na tela.

### Contando as linhas do arquivo

```python
subprocess.run('wc -l /tmp/numbers.txt', shell=True)
```

O `wc -l` conta as linhas do arquivo. Como o `echo` escreveu tudo numa linha só, o resultado é `1`.

## Rodando

```bash
$ python subprocess01.py
Hello
Running
0 1 2 3 4 5 6 7 8 9
1 /tmp/numbers.txt
```

Além dessa saída no terminal, aparece a notificação com a data e hora na área de trabalho.

## Cuidados

* Use `shell=True` só com comandos que você mesmo escreveu. Se parte do comando vier do usuário (um formulário, um argumento), alguém pode injetar outro comando, por exemplo com `;`. Nesses casos, passe o comando como lista e sem `shell=True`.
* Se precisar usar a saída do comando no Python, em vez de só mostrá-la, use `subprocess.run('...', shell=True, capture_output=True, text=True).stdout`.

O caminho inverso, rodar Python dentro de um Shell script, está na [dica 26](026-rodando-python-dentro-do-shell-script.md).
