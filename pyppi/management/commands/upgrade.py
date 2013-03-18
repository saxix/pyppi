from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from optparse import make_option
from pyppi.util import mktree


class Command(BaseCommand):
    help = 'Performs any pending database migrations and upgrades'

    option_list = BaseCommand.option_list + (
        make_option('--noinput',
                    action='store_true',
                    dest='noinput',
                    default=False,
                    help='Tells Django to NOT prompt the user for input of any kind.'),
    )

    def handle(self, **options):
        if not settings.STATIC_ROOT.strip():
            raise ValueError('please set a valid value for settings.STATIC_ROOT')
        if not settings.MEDIA_ROOT.strip():
            raise ValueError('please set a valid value for settings.MEDIA_ROOT')
        if not settings.PYPPI_LOG_DIR.strip():
            raise ValueError('please set a valid value for settings.PYPPI_LOG_DIR')
        mktree(settings.STATIC_ROOT)
        mktree(settings.MEDIA_ROOT)
        mktree(settings.PYPPI_LOG_DIR)

        call_command('syncdb', migrate=True, interactive=(not options['noinput']))
        call_command('loaddata', 'pyppi_initial.json', verbosity=0)
        call_command('collectstatic', interactive=False, verbosity=0)
