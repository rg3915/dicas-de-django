# 25 - Rodando Shell script dentro do Python

<a href="https://youtu.be/r3MIUX2QTEI">
    <img src="../.gitbook/assets/youtube.png">
</a>


Para rodar Shell script dentro do Python só precisamos do [subprocess](https://docs.python.org/3/library/subprocess.html).

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

subprocess.run('wc -l /tmp/out.log', shell=True)
```

```
$ python subprocess01.py
```


