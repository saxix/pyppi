import base64
import os

KEY_LENGTH = 40

CONFIG_TEMPLATE = """
import os.path

CONF_ROOT = os.path.dirname(__file__)
SECRET_KEY='%(default_key)s'

DATABASES = {
'default': {
# You can swap out the engine for MySQL easily by changing this value
# to ``django.db.backends.mysql`` or to PostgreSQL with
# ``django.db.backends.postgresql_psycopg2``

# If you change this, you'll also need to install the appropriate python
# package: psycopg2 (Postgres) or mysql-python
'ENGINE': 'django.db.backends.sqlite3',

'NAME': os.path.join(CONF_ROOT, 'pyppi.db'),
'USER': 'postgres',
'PASSWORD': '',
'HOST': '',
'PORT': '',
}
}

# Mail server configuration

# For more information check Django's documentation:
# https://docs.djangoproject.com/en/1.3/topics/email/?from=olddocs#e-mail-backends

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False
SERVER_EMAIL='pippi@localhost'

LISTEN='127.0.0.1:8000'

STATIC_ROOT= os.path.join(CONF_ROOT, 'static')
MEDIA_ROOT = os.path.join(CONF_ROOT, 'media')

PYPPI_LOG_DIR= os.path.join(CONF_ROOT, 'logs')
HAYSTACK_WHOOSH_PATH=os.path.join(CONF_ROOT, 'whoosh')

"""


def initializer(params):
    """
    params: {'project': project,'config_path': config_path,'settings': settings}
    """
    pass


def generate_settings():
    """
This command is run when ``default_path`` doesn't exist, or ``init`` is
run and returns a string representing the default data to put into their
settings file.
"""
    output = CONFIG_TEMPLATE % dict(
        default_key=base64.b64encode(os.urandom(KEY_LENGTH)),
    )
    return output
