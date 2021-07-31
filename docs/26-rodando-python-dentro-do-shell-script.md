# 26 - Rodando Python dentro do Shell script

<a href="https://youtu.be/WjvVTqfUNMI">
    <img src="../.gitbook/assets/youtube.png">
</a>


Leia mais em:

[Grande Portal - Shell script 1](http://grandeportal.github.io/shell/2016/shell-script1/)

[Grande Portal - Shell script 2](http://grandeportal.github.io/shell/2016/shell-script2/)

[Grande Portal - Shell script 3](http://grandeportal.github.io/shell/2016/shell-script3/)


Assista também:

<a href="https://www.youtube.com/watch?v=NoQW5CGAGNA">
    <img src="../.gitbook/assets/youtube.png">
</a>

[Mini-curso Shell script 1](https://www.youtube.com/watch?v=NoQW5CGAGNA)

<a href="https://www.youtube.com/watch?v=aspwrDLSrPI">
    <img src="../.gitbook/assets/youtube.png">
</a>

[Mini-curso Shell script 2](https://www.youtube.com/watch?v=aspwrDLSrPI)


**Exemplo 1:**


```sh
# running_python01.sh
python -c "print('Rodando Python dentro do Shell script')"
```

```
$ source running_python01.sh
```

Ou

```
$ chmod +x running_python01.sh
$ ./running_python01.sh
```


**Exemplo 2:**

```sh
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

```
chmod +x running_python02.sh
./running_python02.sh 1 2
./running_python02.sh 2 1
./running_python02.sh 2 2
```

**Exemplo 3:**

```sh
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


```
chmod +x running_python03.sh
./running_python03.sh 1 10
./running_python03.sh 35 42
```

**Exemplo 4:** Não está no video.

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

https://www.geeksforgeeks.org/program-for-nth-fibonacci-number/

