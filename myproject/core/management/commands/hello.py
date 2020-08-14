from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Print hello world.'

    def add_arguments(self, parser):
        # Argumento nomeado (opcional)
        parser.add_argument(
            '--awards', '-a',
            action='store_true',
            help='Print awards.'
        )

    def handle(self, *args, **options):
        self.stdout.write('Hello world.')
        if options['awards']:
            self.stdout.write('Awards')
