.. image:: https://travis-ci.org/ome/omero-mapr.svg?branch=master
    :target: https://travis-ci.org/ome/omero-mapr

.. image:: https://badge.fury.io/py/omero-mapr.svg
    :target: https://badge.fury.io/py/omero-mapr


MAPR
====

An OMERO.web app allowing to browse the data through attributes lineked to the image

Requirements
============

* OMERO 5.3 or newer.

Installing from Pypi
====================

This section assumes that an OMERO.web is already installed.

Install the app using `pip <https://pip.pypa.io/en/stable/>`_:

::

    $ pip install omero-mapr

plug in the app to OMERO.web

::

    $ bin/omero config append omero.web.apps '"omero_mapr"'

    $ bin/omero config set omero.web.ui.top_links '[["IDR", {"viewname": "webindex", "query_string": {"experimenter": -1}}, {"title": "Image Data Repository"}], ["Genes", {"viewname": "maprindex_gene", "query_string": {"experimenter": -1}}, {"title": "Genes browser"}], ["Phenotypes", {"viewname": "maprindex_phenotype", "query_string": {"experimenter": -1}}, {"title": "Phenotypes browser"}], ["siRNA", {"viewname": "maprindex_sirna", "query_string": {"experimenter": -1}}, {"title": "siRNA browser"}], ["Compound", {"viewname": "maprindex_compound", "query_string": {"experimenter": -1}}, {"title": "Compound browser"}], ["Organism", {"viewname": "maprindex_organism", "query_string": {"experimenter": -1}}, {"title": "Organism browser"}]]'


Now restart OMERO.web as normal.


License
-------

MAPR is released under the AGPL.


Copyright
---------

2016, The Open Microscopy Environment
