from django.core.management.base import BaseCommand

from myproject.core.models import Article


class Command(BaseCommand):
    help = 'Localiza um artigo pelo título ou sub-título.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--title', '-t',
            dest='title',
            default=None,
            help='Localiza um artigo pelo título.'
        )
        parser.add_argument(
            '--subtitle', '-sub',
            dest='subtitle',
            default=None,
            help='Localiza um artigo pelo sub-título.'
        )

    def handle(self, title=None, subtitle=None, **options):
        """ dicionário de filtros """
        self.verbosity = int(options.get('verbosity'))

        filters = {
            'title__icontains': title,
            'subtitle__icontains': subtitle,
        }

        filter_by = {
            key: value for key,
            value in filters.items() if value is not None
        }
        queryset = Article.objects.filter(**filter_by)

        if self.verbosity > 0:
            for article in queryset:
                self.stdout.write(f"{article.title} {article.subtitle}")
            self.stdout.write(f'\n{queryset.count()} artigos localizados.')
