.. image:: https://travis-ci.org/aleksandra-tarkowska/mapr.svg?branch=master
    :target: https://travis-ci.org/aleksandra-tarkowska/mapr

.. image:: https://badge.fury.io/py/omero-mapr.svg
    :target: https://badge.fury.io/py/omero-mapr


MAPR
====

An OMERO.web app allowing to browse the data through attributes lineked to the image


Installation
------------

Install OMERO.web

This app installs into the OMERO.web framework.

To install:

::

    $ pip install omero-mapr

plug in the app to OMERO.web

::

    $ bin/omero config append omero.web.apps '"mapr"'

Restart webclient

Browse to https://yourserver/mapr/


License
-------

MAPR is released under the AGPL.


Copyright
---------

2016, The Open Microscopy Environment
