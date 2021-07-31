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
