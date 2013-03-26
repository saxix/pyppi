.. include:: globals.rst


Users: How to use this server
=============================

Installing a package with pip
-----------------------------

To install your package with pip::

 $ pip install -i http://my.pypiserver.com/simple/ <PACKAGE>

If you want to fall back to PyPi or another repository in the event the
package is not on your new server, or in particular if you are installing a number
of packages, some on your private server and some on another, you can use
pip in the following manner::

 $ pip install -i http://pyppiserver/simple/ \
   --extra-index-url=http://pypi.python.org/simple/ \
   -r requirements.txt


The downside is that each install of a package hosted on the repository in
``--extra-index-url`` will start with a call to the first repository which
will fail before pip falls back to the alternative.
