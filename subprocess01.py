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
