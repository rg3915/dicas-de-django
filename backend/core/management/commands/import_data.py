import csv
import sys
from time import sleep

from django.core.management.base import BaseCommand

from backend.product.models import Product


def csv_to_list(filename: str) -> list:
    '''
    Lê um csv e retorna um OrderedDict.
    '''
    with open(filename) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        csv_data = [line for line in reader]
    return csv_data


def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)

    def show(j):
        x = int(size * j / count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#" * x, "." * (size - x), j, count))  # noqa E501
        file.flush()
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i + 1)
    file.write("\n")
    file.flush()


def save_data(data, slow_motion=None):
    '''
    Salva os dados no banco.
    '''
    aux = []
    for item in progressbar(data, 'Importando dados'):
        title = item.get('title')
        price = item.get('price')
        obj = Product(
            title=title,
            price=price,
        )
        if slow_motion:  # <---
            obj.save()
            sleep(.02)
        else:
            aux.append(obj)

    if not slow_motion:
        Product.objects.bulk_create(aux)


def import_csv(filename, slow_motion=None):
    data = csv_to_list(filename)
    save_data(data, slow_motion)  # <---


class Command(BaseCommand):
    help = "Importa dados de um CSV."

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename_csv',
            '-fcsv',
            dest='filename_csv',
            help='Importa arquivo CSV.'
        )
        parser.add_argument(
            '--slow_motion',
            '-slow',
            action='store_true',
            help='Simula camera lenta.'
        )

    def handle(self, *args, **options):
        filename = options['filename_csv']
        slow_motion = options['slow_motion']

        Product.objects.all().delete()
        import_csv(filename, slow_motion)
