import click


@click.command()
@click.option('-ids', prompt='Ids', help='Digite uma sequência de números separado por vírgula.')
def get_numbers(ids):
    print('>>>', ids)
    for id in ids.split(','):
        print(id)


if __name__ == '__main__':
    get_numbers()
