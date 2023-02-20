import os

from rich.console import Console

os.system("clear")

console = Console()
console.print("")
console.print("To run commands: [bold]make command[/bold]")

with open("./Makefile") as file:
    for line in file.readlines():
        if line.find("##") >= 0:
            if line.find("@") >= 0:
                to_print = line.split("@")[-1].strip().capitalize()
                console.print(f"\n{to_print}", style="bold green")
            else:
                values = line.split("##")
                target = values[0]
                description = values[-1].strip().capitalize()
                target = target.split(":")[0].strip()

                console.print(f" - [bold]{target}:[/bold] {description}")
