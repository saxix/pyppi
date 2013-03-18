.. include:: globals.rst

=========
Migration
=========


From chishop
-------------

    cd <chishop>
    ./bin/django dumpdata auth.user auth.group -n > /tmp/auth.json

    cd pyppi
    ./bin/pyppi loaddata /tmp/auth.json
    ./bin/pyppi loadclassifier
    ./bin/pyppi import http://<chishopurl>

From djangopypi
---------------



From djangopypi2
----------------

    cd ~/.djangopypi2
    manage-pypi-site dumpdata auth.user auth.group -n > /tmp/auth.json

    cd pyppi
    ./bin/pyppi loaddata /tmp/auth.json
    ./bin/pyppi loadclassifier
    ./bin/pyppi import http://<chishopurl>

From other Pypi xmlrpc compliant
--------------------------------
