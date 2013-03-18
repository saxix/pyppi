import os
from scripttest import TestFileEnvironment

env = TestFileEnvironment()
PYPPI_LOG_DIR = os.environ["PYPPI_LOG_DIR"] = env.base_path

from pyppi.server.settings import * # NOQA

LOGGING = {'version': 1, 'disable_existing_loggers': True, }

PYPPI_ALLOW_VERSION_OVERWRITE = ".*"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(env.base_path, '_pyppi.sqlite'),
        'HOST': '',
        'PORT': ''}
}
