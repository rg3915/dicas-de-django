from time import sleep

from progressbar import progressbar

for i in progressbar(range(100)):
    sleep(0.02)
