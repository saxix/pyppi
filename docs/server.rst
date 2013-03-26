.. include:: globals.rst
.. _server:

=========
Server
=========

.. contents::
    :local:
    :depth: 1


Start/Stop
----------

::

    $ pyppi start


::

    $ pyppi stop


Configuration
-------------

Here's a full list of the settings of the |app| integrated server.
To check the |app| applicatin settings refet to :ref:`settings`


.. setting:: CONF_ROOT

CONF_ROOT
~~~~~~~~~
Default ``~/.pyppi/``


.. setting:: EMAIL_BACKEND

EMAIL_BACKEND
~~~~~~~~~~~~~
Default ``django.core.mail.backends.smtp.EmailBackend``

.. setting:: EMAIL_HOST

EMAIL_HOST
~~~~~~~~~~
Default ``localhost``

EMAIL_HOST_PASSWORD
~~~~~~~~~~~~~~~~~~~
Default ``

EMAIL_HOST_USER
~~~~~~~~~~~~~~~~~~~
Default ``

EMAIL_HOST_PASSWORD
~~~~~~~~~~~~~~~~~~~
Default ``

EMAIL_PORT
~~~~~~~~~~
Default ``25``

EMAIL_USE_TLS
~~~~~~~~~~~~~~~
Default ``False``

LISTEN
~~~~~~~~~~
Default ``127.0.0.1:8000``

HAYSTACK_SEARCH_ENGINE
~~~~~~~~~~~~~~~~~~~~~~
Default  ``whoosh``

.. seealso:: `haystack`_, `whoosh`_

HAYSTACK_SITECONF
~~~~~~~~~~~~~~~~~~~~
Default  ``pyppi.server.search_sites``

.. seealso:: `haystack`_


HAYSTACK_WHOOSH_PATH
~~~~~~~~~~~~~~~~~~~~
Default :setting:`CONF_ROOT`/``whoosh``

.. seealso:: `haystack`_, `whoosh`_


.. setting:: `MEDIA_ROOT2`

MEDIA_ROOT
~~~~~~~~~~

Default :setting:`CONF_ROOT`/``media``

.. seealso:: Django :django:setting:`MEDIA_ROOT`


PYPPI_LOG_DIR
~~~~~~~~~~~~~
Default :setting:`CONF_ROOT`/``logs``


SERVER_EMAIL
~~~~~~~~~~~~~

Default ``pyppi@localhost``

.. seealso:: Django :django:setting:`SERVER_EMAIL`


STATIC_ROOT
~~~~~~~~~~~

Default :setting:`CONF_ROOT`/``static``



