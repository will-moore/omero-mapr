.. image:: https://travis-ci.org/ome/omero-mapr.svg?branch=master
    :target: https://travis-ci.org/ome/omero-mapr

.. image:: https://badge.fury.io/py/omero-mapr.svg
    :target: https://badge.fury.io/py/omero-mapr


MAPR
====

OMERO.map is an OMERO.web app that enables browsing of data through attributes linked to images
in the form of Map Annotations.

It is used extensively by the `Image Data Resource <http://idr.openmicroscopy.org/>`_,
allowing users to find data by various categories such as Genes, Phenotypes, Organism etc.

In OMERO, Map Annotations are lists of named attributes that can be used to
annotate many types of data. Annotations can be assigned a ``namespace``
to indicate the origin and purpose of the annotation.

In OMERO.mapr we can configure different categories of attributes using
different namespaces, such as ``openmicroscopy.org/mapr/gene``.
Within Map Annotations with this namespace, attributes named
by specified keys will be searchable. For example,
``Gene Symbol`` and ``Gene Identifier``.


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
hierarchy. This uses the OMERO `Python API <https://docs.openmicroscopy.org/latest/omero/developers/Python.html>`_ to
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

.. image:: https://user-images.githubusercontent.com/900055/36256919-d8a19fb6-124c-11e8-8628-d792ff29bd22.png


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
