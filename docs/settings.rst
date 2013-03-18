.. include:: globals.rst
.. _settings:

=========
Settings
=========

Here's a full list of all available settings, in alphabetical order, and their
default values.

.. warning:: To configure the integrated server refer to :ref:`server`

.. note:: Each entry must be prefixed with ``PYPPI_``


.. contents::
    :local:
    :depth: 1



.. setting:: ALLOW_VERSION_OVERWRITE

ALLOW_VERSION_OVERWRITE
-----------------------
Defaut ``None``

Allows you to selectively allow user with :ref:`overwrite_file` permission to overwrite
package distributions based on the version number. This is a regular
expression, with the default empty string meaning 'deny all'. A common use-case
example of this is to allow development versions to be overwritten, but not released
versions::

    "ALLOW_VERSION_OVERWRITE": "\\.dev.*$"

This will match ``1.0.0.dev``, ``1.0.0.dev3``, but not ``1.0.0``. Note the escaping
of the backslash character - this is required to conform to the json format.

.. setting:: RELEASE_UPLOAD_TO


RELEASE_UPLOAD_TO
-----------------
Defaut ``dists``


.. setting:: RELEASE_STORAGE_PATH

RELEASE_STORAGE_PATH
---------------------
Defaut ``None``

Full path to the distribution upload directory. ``None`` means :django:setting:`MEDIA_ROOT`,
if you are running the integrated |app| server chek :setting:`MEDIA_ROOT2`
The final full pathname of uploaded file will be:

    <:setting:`RELEASE_STORAGE_PATH`> / <:setting:`RELEASE_UPLOAD_TO`> / <filename>



.. setting:: XMLRPC_COMMANDS


XMLRPC_COMMANDS
---------------


