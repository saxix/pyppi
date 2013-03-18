import tempfile, os

DEBUG = False
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ('127.0.0.1', )

ADMINS = ()

TIME_ZONE = 'Asia/Bangkok'
USE_TZ = True
APPEND_SLASH = True

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

DATABASES = {
    'default': {
        'ENGINE': '',
        'NAME': '',
        'HOST': '',
        'PORT': ''}
}

SOUTH_DATABASE_ADAPTERS = {
    'default': "south.db.sqlite3"
}
WSGI_APPLICATION = 'pyppi.server.wsgi.application'

HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_SITECONF = 'pyppi.server.search_sites'
HAYSTACK_WHOOSH_PATH = '/tmp/whoosh/'

ROOT_URLCONF = 'pyppi.server.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',
    'guardian',
    'guardian.tests.testapp',
    'gunicorn',
    'haystack',
    'south',
    'pyppi',
    'pyppi.server',
    # 'django-admin-tools',
    # 'django-admintools-bootstrap'

)

MEDIA_ROOT = ''
MEDIA_URL = '/media/'
X_ACCEL_REDIRECT_PREFIX = MEDIA_URL

STATIC_ROOT = ''
STATIC_URL = '/static/'

SERVE_MEDIA = False
SITE_ID = 1

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    'django.core.context_processors.csrf',
    "django.core.context_processors.i18n",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages")

PYPPI_LOG_DIR = os.environ.setdefault("PYPPI_LOG_DIR", tempfile.mkdtemp(".log"))

file_handler = lambda name, level: {'level': level,
                                    'class': 'logging.handlers.RotatingFileHandler',
                                    'formatter': 'verbose',
                                    'filename': os.path.join(PYPPI_LOG_DIR, '%s.log' % name)}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'full': {
            'format': '%(levelname)-8s: %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'verbose': {
            'format': '%(levelname)-8s: %(asctime)s %(name)-25s %(message)s'
        },
        'simple': {
            'format': '%(levelname)-8s %(asctime)s %(name)-25s %(funcName)s %(message)s'
        },
        'debug': {
            'format': '%(levelno)s:%(levelname)-8s %(name)s %(funcName)s:%(lineno)s:: %(message)s'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler'
        },
        'root': file_handler('messages', 'DEBUG'),
        'requests': file_handler('requests', 'DEBUG'),
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'debug'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True
        }
    },
    'loggers': {
        '': {
            'handlers': ['root'],
            'propagate': False,
            'level': 'ERROR'
        },
        'django': {
            'handlers': ['root'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'pyppi': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

# DJANGOPYPI_ALLOW_VERSION_OVERWRITE = True

ANONYMOUS_USER_ID = 2
# DJANGOPYPI_PROXY_BASE_URL=None
# DJANGOPYPI_PROXY_MISSING=False

