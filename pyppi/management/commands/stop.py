import os
from django.conf import settings
from django.core.management.base import BaseCommand

from optparse import make_option
import signal


class Command(BaseCommand):
    help = 'Stop PyPPi server'

    option_list = BaseCommand.option_list + (
        make_option('--debug',
            action='store_true',
            dest='debug',
            default=False),
        make_option('-p', '--pid',
            action='store',
            dest='pid',
            default=os.path.join(settings.CONF_ROOT, 'pyppi.pid')),
    )

    def handle(self, **options):
        options.setdefault('pid', os.path.join(settings.CONF_ROOT, 'pyppi.pid'))
        try:
            pid = open(options['pid'], 'r').read()
            os.kill(int(pid), signal.SIGTERM)
        except IOError as e:
            print "Cannot stop PyPPi server", e
