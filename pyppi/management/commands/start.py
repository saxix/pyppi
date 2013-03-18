import os
import sys
from optparse import make_option

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Starts PyPPi server'

    option_list = BaseCommand.option_list + (
        make_option('--debug',
            action='store_true',
            dest='debug',
            default=False),
        make_option('--init',
            action='store_true',
            dest='init',
            default=False),
        make_option('--noupgrade',
            action='store_false',
            dest='upgrade',
            default=True),
        make_option('-D', '--daemon',
            action='store_true',
            dest='daemon',
            default=False),
        make_option('-b', '--bind',
            action='store',
            dest='bind',
            default=settings.LISTEN),
        make_option('-p', '--pid',
            action='store',
            dest='pidfile',
            default=os.path.join(settings.CONF_ROOT, 'pyppi.pid')),
    )

    def handle(self, upgrade=True, init=False, **options):
        if upgrade:
            print "Performing upgrade before service startup..."
            call_command('upgrade', verbosity=0)
        if init:
            call_command('ppadd', 'django-concurrency', owner='sax')

        options.setdefault('pid', os.path.join(settings.CONF_ROOT, 'pyppi.pid'))

        sys.argv = sys.argv[:1]

        call_command('run_gunicorn', **options)
