# Dica 26 - Rodando Python dentro do Shell script

**Versões usadas no vídeo:** esta dica não usa Django; Python 3.8, click 7.1.2 e Bash no Linux.
{: .versoes }

<a href="https://youtu.be/WjvVTqfUNMI">
    <img src="../.gitbook/assets/youtube.png">
</a>


Na [dica 25](025-rodando-shell-script-dentro-do-python.md) rodamos comandos de shell dentro do Python. Agora é o caminho inverso: chamar o Python de dentro de um Shell script. Isso é útil quando o seu script de automação é em Bash, mas uma parte do trabalho (um cálculo, uma conversão de lista, um programa com interface de linha de comando) é mais fácil de fazer em Python.

Vamos ver três exemplos, do mais simples ao mais completo:

1. Rodar um comando Python com `python -c`.
2. Usar `if`, `elif` e `else` do shell com argumentos e chamar o Python em cada caso.
3. Gerar uma sequência de números no shell, manipulá-la com Python e passá-la para um script Python com o Click.

No fim há um quarto exemplo, que não está no vídeo: como guardar o resultado do Python numa variável do shell.

Leia mais em:

[Grande Portal - Shell script 1](http://grandeportal.github.io/shell/2016/shell-script1/)

[Grande Portal - Shell script 2](http://grandeportal.github.io/shell/2016/shell-script2/)

[Grande Portal - Shell script 3](http://grandeportal.github.io/shell/2016/shell-script3/)

São três artigos do blog Grande Portal com o básico de Shell script e o uso de `seq`, `while` e `for`.

Assista também:

<a href="https://www.youtube.com/watch?v=NoQW5CGAGNA">
    <img src="../.gitbook/assets/youtube.png">
</a>

[Mini-curso Shell script 1](https://www.youtube.com/watch?v=NoQW5CGAGNA)

<a href="https://www.youtube.com/watch?v=aspwrDLSrPI">
    <img src="../.gitbook/assets/youtube.png">
</a>

[Mini-curso Shell script 2](https://www.youtube.com/watch?v=aspwrDLSrPI)

## Pré-requisitos

* Linux (ou macOS) com Bash.
* Python 3 disponível no terminal como `python` (no vídeo, um ambiente virtual com Python 3.8 está ativado; fora de um ambiente virtual, talvez o comando seja `python3`).
* Para o exemplo 3, o [Click](https://click.palletsprojects.com/en/7.x/): `pip install click` (no vídeo, a versão 7.1.2).

## Exemplo 1: python -c

A opção `-c` do Python executa o código que vem a seguir, entre aspas, sem precisar de um arquivo `.py`.

```sh
# running_python01.sh
python -c "print('Rodando Python dentro do Shell script')"
```

Repare nas aspas: as aspas duplas delimitam o código para o shell, e as aspas simples ficam para a string do Python.

Para rodar, você pode usar o `source`:

```
$ source running_python01.sh
Rodando Python dentro do Shell script
```

Ou dar permissão de execução ao arquivo e rodá-lo diretamente:

```
$ chmod +x running_python01.sh
$ ./running_python01.sh
Rodando Python dentro do Shell script
```

## Exemplo 2: if, elif e else com argumentos

Agora o script recebe dois números como argumentos, compara os dois no shell e usa o Python para escrever o resultado.

```sh
# running_python02.sh
# ./running_python02.sh 1 2
# ./running_python02.sh 2 1
# ./running_python02.sh 2 2

a=${1}
b=${2}

if [[ $a -eq $b ]]; then
    python -c "print('${a} é igual a ${b}')"
elif [[ $a -lt $b ]]; then
    python -c "print('${a} é menor que ${b}')"
else
    python -c "print('${a} é maior que ${b}')"
fi
```

* `${1}` e `${2}` são o primeiro e o segundo argumento passados ao script.
* No shell, a comparação numérica usa operadores próprios: `-eq` (igual), `-lt` (menor que, *less than*) e `-gt` (maior que, *greater than*).
* Como o código Python está entre aspas duplas, o shell substitui `${a}` e `${b}` pelos valores antes de entregar o código ao Python. É assim que passamos valores do shell para o Python.

```
$ chmod +x running_python02.sh
$ ./running_python02.sh 1 2
1 é menor que 2
$ ./running_python02.sh 2 1
2 é maior que 1
$ ./running_python02.sh 2 2
2 é igual a 2
```

## Exemplo 3: uma sequência de números, do shell para o Python

Este script recebe um valor inicial e um valor final, gera a sequência de números entre eles e brinca com ela de vários jeitos. No fim, passa a sequência para um programa Python feito com o Click.

```sh
# running_python03.sh
# ./running_python03.sh 1 10
# ./running_python03.sh 35 42

start_value=${1}
end_value=${2}

function join { local IFS="$1"; shift; echo "$*"; }

if [[ $start_value -gt $end_value ]]; then
    python -c "print('O valor inicial não pode ser maior que o valor final.')"
else
    IDS=$(seq -s ' ' $start_value $end_value)

    for id in $IDS; do
        python -c "print('$id')"
    done

    python -c "print('$IDS')"
    python -c "print('$IDS'.split())"
    python -c "print([int(i) for i in '$IDS'.split()])"
    python -c "print(sum([int(i) for i in '$IDS'.split()]))"
    python -c "ids=[int(i) for i in '$IDS'.split()]; print(ids)"
    # Não dá pra usar o laço for do Python na mesma linha, então façamos
    echo "IDS:" $IDS
    result=$(join , ${IDS[@]})
    echo "result:" $result
    python running_python03.py -ids $result
fi
```

Vamos por partes.

### A função join

```sh
function join { local IFS="$1"; shift; echo "$*"; }
```

É uma função do shell que junta os argumentos usando o separador que você passar. `IFS` é a variável que o Bash usa como separador; `local` faz a mudança valer só dentro da função. `shift` descarta o primeiro argumento (o separador) e `"$*"` junta os argumentos restantes usando o primeiro caractere de `IFS`. Assim, `join , 1 2 3` devolve `1,2,3`.

### Validando os valores

Se o valor inicial for maior que o final (`-gt`), o script só avisa:

```
$ ./running_python03.sh 5 1
O valor inicial não pode ser maior que o valor final.
```

### Gerando a sequência com seq

```sh
IDS=$(seq -s ' ' $start_value $end_value)
```

`seq 1 10` gera os números de 1 a 10; `-s ' '` usa espaço como separador, então tudo fica numa linha só: `1 2 3 4 5 6 7 8 9 10`. O `$( ... )` guarda a saída do comando na variável `IDS`.

### Usando a sequência no Python

* O `for id in $IDS` é o laço **do shell**: para cada número, chamamos `python -c "print('$id')"`.
* `print('$IDS')` mostra a sequência como texto.
* `'$IDS'.split()` transforma o texto numa lista de strings do Python.
* `[int(i) for i in '$IDS'.split()]` é uma *list comprehension* que converte cada item para inteiro.
* `sum(...)` soma os números: de 1 a 10, o resultado é 55.
* `ids=[...]; print(ids)` mostra que dá para escrever mais de um comando Python na mesma linha, separando com ponto e vírgula.

O que não dá é usar um bloco, como o laço `for` do Python, nessa mesma linha (`python -c "ids=[...]; for i in ids: print(i)"` dá erro de sintaxe). Por isso a última parte junta os números com vírgula e entrega a lista para um script Python de verdade.

### Passando a lista para um script com o Click

```sh
echo "IDS:" $IDS
result=$(join , ${IDS[@]})
echo "result:" $result
python running_python03.py -ids $result
```

`join , ${IDS[@]}` junta os números com vírgula (`1,2,3,4,5,6,7,8,9,10`) e o resultado vai como valor da opção `-ids` do script Python:

```python
# running_python03.py
import click


@click.command()
@click.option('-ids', prompt='Ids', help='Digite uma sequência de números separado por vírgula.')
def get_numbers(ids):
    print('>>>', ids)
    for id in ids.split(','):
        print(id)


if __name__ == '__main__':
    get_numbers()
```

* `@click.command()` transforma a função `get_numbers` num comando de terminal.
* `@click.option('-ids', ...)` cria a opção `-ids`. Com `prompt='Ids'`, se você rodar o script sem a opção, ele pergunta o valor; `help` é o texto que aparece em `python running_python03.py --help`.
* Dentro da função, agora sim usamos o `for` do Python para percorrer os números separados por vírgula.

Rodando:

```
$ chmod +x running_python03.sh
$ ./running_python03.sh 1 10
1
2
3
4
5
6
7
8
9
10
1 2 3 4 5 6 7 8 9 10
['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
55
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
IDS: 1 2 3 4 5 6 7 8 9 10
result: 1,2,3,4,5,6,7,8,9,10
>>> 1,2,3,4,5,6,7,8,9,10
1
2
3
4
5
6
7
8
9
10
```

E com outro intervalo:

```
$ ./running_python03.sh 35 42
```

### Cuidado com o espaço depois do join

No vídeo, a linha foi digitada primeiro como `result=$(join, ${IDS[@]})`, sem espaço entre `join` e a vírgula. O shell então procura um comando chamado `join,`, que não existe, `result` fica vazio e o Click reclama que a opção ficou sem valor:

```
./running_python03.sh: linha 21: join,: comando não encontrado
result:
Error: -ids option requires an argument
```

A correção é colocar o espaço: `result=$(join , ${IDS[@]})`.

## Exemplo 4: guardando o resultado do Python numa variável do shell

Este exemplo **não está no vídeo**; foi acrescentado depois, no repositório. Ele mostra o caminho de volta: como pegar o que o Python imprimiu e usar no shell.

```sh
# running_python04.sh
# Como pegar o resultado do Python e usar numa variável no Shell script.

result=$(python -c "result = 42; print(result)" | xargs echo $var1)
echo 'Resultado:' $result
echo 'Dobro:' $(( $result*2 ))

result2=$(python -c "result = sum([i for i in range(11)]); print(result)" | xargs echo $var2)
echo 'Resultado:' $result2
echo 'Dobro:' $(( $result2*2 ))


# Como usar comandos multilinha.

result=$(python << EOF
aux = []
for i in range(1, 11):
    aux.append(i)
print(sum(aux))
EOF
)
echo 'Resultado:' $result

python << EOF
aux = []
for i in range(1, 11):
    print(i)
    aux.append(i)
print(f'Total: {sum(aux)}')
EOF

result=$(python fibonacci.py | xargs echo $f)
echo 'Fibonacci'
echo $result
```

* `$( ... )` captura o que o Python imprime e guarda na variável do shell. Com o valor na variável, o shell pode fazer contas com ele, como `$(( $result*2 ))`.
* O `| xargs echo` repassa a saída e remove espaços e quebras de linha extras.
* Para código Python com várias linhas (um `for`, por exemplo), use um *here document*: tudo entre `<< EOF` e `EOF` é enviado para o Python como se fosse um arquivo. Isso resolve a limitação do `python -c` vista no exemplo 3.
* A última parte roda um arquivo `.py` inteiro e guarda o resultado.

```python
# fibonacci.py
# Function for nth Fibonacci number

def Fibonacci(n):
    if n < 0:
        print("Incorrect input")
    # First Fibonacci number is 0
    elif n == 0:
        return 0
    # Second Fibonacci number is 1
    elif n == 1:
        return 1
    else:
        return Fibonacci(n - 1) + Fibonacci(n - 2)


print(Fibonacci(9))
# This code is contributed by Saket Modi
```

Fonte do `fibonacci.py`: https://www.geeksforgeeks.org/program-for-nth-fibonacci-number/

```
$ bash running_python04.sh
Resultado: 42
Dobro: 84
Resultado: 55
Dobro: 110
Resultado: 55
1
2
3
4
5
6
7
8
9
10
Total: 55
Fibonacci
34
```

## Resumo

* `python -c "..."` roda uma ou mais instruções Python (separadas por `;`) de dentro do shell.
* Variáveis do shell entram no código Python porque o shell as substitui dentro das aspas duplas.
* Para blocos (`for`, `if` com várias linhas), use um arquivo `.py` ou um *here document* (`python << EOF`).
* Para passar listas, junte os valores com um separador (a função `join`) e leia no Python com `split`.
