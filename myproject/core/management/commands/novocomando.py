from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('sample', nargs='+')

    def handle(self, *args, **options):
        raise NotImplementedError()
