.. image:: https://travis-ci.org/ome/omero-mapr.svg?branch=master
    :target: https://travis-ci.org/ome/omero-mapr

.. image:: https://badge.fury.io/py/omero-mapr.svg
    :target: https://badge.fury.io/py/omero-mapr


MAPR
====

OMERO.mapr is an OMERO.web app that enables browsing of data through attributes linked to images
in the form of Map Annotations.

It is used extensively by the `Image Data Resource <https://idr.openmicroscopy.org/>`_,
allowing users to find data by various categories such as Genes, Phenotypes, Organism etc.

In OMERO, Map Annotations are lists of named attributes that can be used to
annotate many types of data. Annotations can be assigned a ``namespace``
to indicate the origin and purpose of the annotation.

In OMERO.mapr we can configure different categories of attributes using
different namespaces, such as ``openmicroscopy.org/mapr/gene``.
Within Map Annotations with this namespace, attributes named
by specified keys will be searchable. For example,
``Gene Symbol`` and ``Gene Identifier``.


.. image:: https://user-images.githubusercontent.com/900055/36256919-d8a19fb6-124c-11e8-8628-d792ff29bd22.png


Requirements
============

* OMERO 5.3 or newer.

Installing from Pypi
====================

This section assumes that an OMERO.web is already installed.

Install the app using `pip <https://pip.pypa.io/en/stable/>`_:

::

    $ pip install omero-mapr

Add the app to the list of installed apps:

::

    $ bin/omero config append omero.web.apps '"omero_mapr"'


Config Settings
===============

Configure the categories that we want to search for. In this example we want to search
for Map Annotations of namespace ``openmicroscopy.org/mapr/gene`` searching for
attributes under the ``Gene Symbol`` and ``Gene Identifier`` keys.

::

    $ bin/omero config append omero.web.mapr.config '{"menu": "gene","config": {"default": ["Gene Symbol"],"all": ["Gene Symbol", "Gene Identifier"],"ns": ["openmicroscopy.org/mapr/gene"],"label": "Gene"}}'

We can add a link to the top of the webclient page to take us to the mapr Genes search page.
The ``viewname`` should be in the form ``maprindex_{menu}`` where ``{menu}`` is the the ``menu`` value in the previous config.
In this example a link of ``Genes`` with tooltip ``Find Gene annotations`` will take us to the ``gene`` search page.

::

    $ bin/omero config append omero.web.ui.top_links '["Genes", {"viewname": "maprindex_gene", "query_string": {"experimenter": -1}}, {"title": "Find Gene annotations"}]'


Finally, we can add a map annotation to an Image that is in a Screen -> Plate -> Well
or Project -> Dataset -> Image hierarchy.
This code uses the OMERO `Python API <https://docs.openmicroscopy.org/latest/omero/developers/Python.html>`_ to
add a map annotation corresponding to the configuration above:

::

    key_value_data = [["Gene Identifier","ENSG00000117399"],
                      ["Gene Identifier URL", "http://www.ensembl.org/id/ENSG00000117399"],
                      ["Gene Symbol","CDC20"]]
    map_ann = omero.gateway.MapAnnotationWrapper(conn)
    map_ann.setValue(key_value_data)
    map_ann.setNs("openmicroscopy.org/mapr/gene")
    map_ann.save()
    i = conn.getObject('Image', 2917)
    i.linkAnnotation(map_ann)


Now restart OMERO.web as normal for the configuration above to take effect.
You should now be able to browse to a ``Genes`` page and search for
``CDC20`` or ``ENSG00000117399``.


User-edited Map Annotations
===========================

Map Annotations that are added using the webclient or Insight in the Key-Value panel
use a specific "client" namespace. We can therefore configure OMERO.mapr to search
for these annotations using the namespace ``openmicroscopy.org/omero/client/mapAnnotation``.
For example, to search for "Primary Antibody" or "Secondary Antibody" values, we can add:

::

    $ bin/omero config append omero.web.mapr.config '{"menu": "antibody", "config":{"default":["Primary Antibody"], "all":["Primary Antibody", "Secondary Antibody"], "ns":["openmicroscopy.org/omero/client/mapAnnotation"], "label":"Antibody"}}'

And to search for "siRNAi" targets we can add:

::

    $ bin/omero config append omero.web.mapr.config '{"menu": "sirnai", "config":{"default":["siRNAi"], "all":["siRNAi"], "ns":["openmicroscopy.org/omero/client/mapAnnotation"], "label":"siRNAi"}}'

After configuring appropriate ``top_links`` for each of these and restarting web, we
can now search for Antibodies or siRNAi Key-Value pairs added by users:


.. image:: https://user-images.githubusercontent.com/900055/36311352-f11be692-1322-11e8-990b-076e1e208f86.png

.. image:: https://user-images.githubusercontent.com/900055/36311363-f3ce8660-1322-11e8-92a5-a79b842eb133.png

Testing
=======

Testing MAPR requires OMERO.server running.
Run tests (includes self-contained OMERO.server, requires docker)::

    docker-compose -f docker/docker-compose.yml up --build --abort-on-container-exit
    docker-compose -f docker/docker-compose.yml rm -fv

License
-------

MAPR is released under the AGPL.


Copyright
---------

2016, The Open Microscopy Environment
