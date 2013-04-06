.. include:: globals.rst

Developers: How to upload packages
==================================

Uploading to your PyPPI
----------------------

Assuming you are running your PyPPI site locally for now, add the following to
your ``~/.pypirc`` file::

    [distutils]
    index-servers =
        pypi
        local

    [pypi]
    username:user
    password:secret

    [local]
    username:user
    password:secret
    repository:http://localhost:8000/pypi/

Uploading a package: Python >=2.6
_________________________________

To push the package to the local pypi::

    $ python setup.py register -r local sdist upload -r local


Uploading a package: Python <2.6
________________________________

If you don't have Python 2.6 please run the command below to install the
backport of the extension for multiple repositories::

     $ easy_install -U collective.dist

Instead of using register and dist command, you can use ``mregister`` and
``mupload`` which are a backport of python 2.6 register and upload commands
that supports multiple servers.

To push the package to the local pypi::

    $ python setup.py mregister -r local sdist mupload -r local
