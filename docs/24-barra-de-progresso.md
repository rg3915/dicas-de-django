# 24 - Barra de progresso

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


### [progress](https://pypi.org/project/progress/)

`pip install progress`


```python
# example01_progress.py
from time import sleep

from progress.bar import Bar

with Bar('Processing...') as bar:
    for i in range(100):
        sleep(0.02)
        bar.next()
```

```
$ python example01_progress.py
```




### [tqdm](https://tqdm.github.io/)

```
pip install tqdm
```

```python
from time import sleep

# example02_tqdm.py
from tqdm import tqdm

for i in tqdm(range(100)):
    sleep(0.02)
    # Do something
```

```
python example02_tqdm.py
```



### [click](https://click.palletsprojects.com/en/7.x/)

[click progressbar](https://click.palletsprojects.com/en/7.x/utils/#showing-progress-bars)


```
pip install click
```

```python
from time import sleep

# example03_click.py
import click

# Fill character is # by default, you can change it
# for any other char you want, or even change the color.
fill_char = click.style('=', fg='yellow')
with click.progressbar(range(100), label='Loading...', fill_char=fill_char) as bar:
    for i in bar:
        sleep(0.02)
```

```
python example03_click.py
```



### [progressbar 2](https://progressbar-2.readthedocs.io/en/latest/index.html)

```
pip install progressbar2
```

```python
# example04_progressbar2.py
from time import sleep

from progressbar import progressbar

for i in progressbar(range(100)):
    sleep(0.02)
```

```
python example04_progressbar2.py
```



### [clint](https://github.com/kennethreitz-archive/clint)

```
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

```
python example05_clint.py
```



### [with sys](https://stackoverflow.com/a/3160819)

```python
import sys
# example06_sys.py
import time

toolbar_width = 40

# setup toolbar
sys.stdout.write("[%s]" % (" " * toolbar_width))
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

for i in range(toolbar_width):
    time.sleep(0.1) # do real work here
    # update the bar
    sys.stdout.write("-")
    sys.stdout.flush()

sys.stdout.write("]\n") # this ends the progress bar
```

```
python example06_sys.py
```


### [gist rg3915](https://gist.github.com/rg3915/b6368374f74d00d9ea045470718a8ddd)

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


```
python example07_sys.py
```


### [progressbar on Jupyter notebook](https://opensource.com/article/20/12/tqdm-python)

```
$ jupyter notebook
```


```python
# progressbar_jupyter.ipynb
import sys

if hasattr(sys.modules["__main__"], "get_ipython"):
    from tqdm import notebook as tqdm
else:
    import tqdm

from time import sleep

n = 0
for i in tqdm.trange(100):
    n += 1
    sleep(0.01)

url = "https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tgz"
import httpx

with httpx.stream("GET", url) as response:
    total = int(response.headers["Content-Length"])
    with tqdm.tqdm(total=total) as progress:
        for chunk in response.iter_bytes():
            progress.update(len(chunk))
```
