from time import sleep

from clint.textui import progress

print('Clint - Regular Progress Bar')
for i in progress.bar(range(100)):
    sleep(0.02)

print('Clint - Mill Progress Bar')
for i in progress.mill(range(100)):
    sleep(0.02)
