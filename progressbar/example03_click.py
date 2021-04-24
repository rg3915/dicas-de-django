from time import sleep

import click

# Fill character is # by default, you can change it
# for any other char you want, or even change the color.
fill_char = click.style('=', fg='yellow')
with click.progressbar(range(100), label='Loading...', fill_char=fill_char) as bar:
    for i in bar:
        sleep(0.02)
