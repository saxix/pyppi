.. include:: globals.rst


Installation & Configuration
============================

Installation
------------

|app| is a self-contained Django project as a pluggable application.

Run integrated server
----------------------

The most simple way to install |app| is by::

    # Make sure we run with Bash, create a virtualenv and install packages
    $ bash
    $ virtualenv pyppi-site
    $ source pyppi-site/bin/activate
    $ pip install pyppi

    # Initialize our installation
    $ pyppi init
    # Run the server
    $ pyppi start

That's it, we're now ready to surf to http://localhost:8000/ .

Configuration
------------------
By default |app| installs and runs from ``~/.pippy`` where the default
configuration file ``pyppi.conf.py`` is created

You can use a different config file by setting the ``PYPPI_CONF`` environment variable or
passing ``--config`` to ``pyppi``. This must point to a valid Django settings file.

For advanced configuration please check :ref:`settings`


Supervisor
----------
For a permanent setup, simply create a `supervisor`_
configuration (you can omit the ``environment`` setting if you didn't specify a
different project root)::

    [program:pyppi]
    user = www-data
    directory = /path/to/virtualenv
    command = /path/to/virtualenv/bin/pyppi start -D
    environment = PYPPI_CONF='/path/to/pyppi.conf.py'


