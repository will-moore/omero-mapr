.. image:: https://github.com/ome/omero-mapr/workflows/OMERO/badge.svg
    :target: https://github.com/ome/omero-mapr/actions

.. image:: https://badge.fury.io/py/omero-mapr.svg
    :target: https://badge.fury.io/py/omero-mapr


MAPR
====

OMERO.mapr is an OMERO.web app that enables browsing of data through attributes linked to images
in the form of Map Annotations.

It is used extensively by the `Image Data Resource <https://idr.openmicroscopy.org/>`_,
allowing users to find data by various categories such as Genes, Phenotypes, Organism etc.

In OMERO, Map Annotations are lists of named attributes or "Key-Value Pairs" that can be used to
annotate many types of data. Annotations can be assigned a ``namespace``
to indicate the origin and purpose of the annotation.

Map Annotations created by users via the Insight client or webclient all have the
namespace ``openmicroscopy.org/omero/client/mapAnnotation``, whereas other
Map Annotations created via the OMERO API by other tools should have their own distinct
namespace.

We can configure OMERO.mapr to search for Map Annotations of specified ``namespace``,
looking for ``Values`` under specifed ``Keys``.
For example, seach for values under key ``Gene Symbol`` or ``Gene Identifier``
and namespace ``openmicroscopy.org/mapr/gene``.

.. image:: https://user-images.githubusercontent.com/900055/36256919-d8a19fb6-124c-11e8-8628-d792ff29bd22.png


Requirements
============

* OMERO.web 5.6 or newer.

Installing from Pypi
====================

This section assumes that an OMERO.web is already installed.
NB: Configuration of the settings (see below) is not optional
and is required for the app to work.

Install the app using `pip <https://pip.pypa.io/en/stable/>`_:

::

    $ pip install omero-mapr

Add the app to the list of installed apps:

::

    $ omero config append omero.web.apps '"omero_mapr"'


Config Settings
===============

You need to configure the namespaces and keys that you want users to be able to search for.
A general config is structured like this:

::

$ omero config append omero.web.mapr.config '{"menu": "gene", "config": {"default": ["Gene Symbol"], "all": ["Gene Symbol", "Gene Identifier"], "ns": ["openmicroscopy.org/mapr/gene"], "wildcard": {"enabled": true}, "case_sensitive": "true", "label": "Gene"}}'

With the following meanings:

* "menu":
    Gives a name to this OMERO.mapr entry by which it can be referenced in other config settings, e.g. ``omero.web.ui.top_links``.
* "default":
    Sets the name of the Key that is used as default in the search field if you have it configured in ``omero.web.ui.top_links``.
    
.. image:: https://user-images.githubusercontent.com/92271654/246146982-97aef32b-6732-4caa-bbe0-260c73bf3576.PNG

* "all":
    Lists all keys for which you can utilize the additional OMERO.mapr functionalities, namely searching for their values and adding URL links to them. One can create other keys with the Namespace set in "ns" which will appear under the same label, but other than being immutable have no additional functionalities.
    
.. image:: https://user-images.githubusercontent.com/92271654/246147020-a72d44cd-84a1-4a11-a1b8-a06fb038bcf5.PNG

* "ns":
    The Namespace that must be used when creating new Map Annotations associated with this OMERO.mapr entry. The prefix "openmicroscopy.org/mapr" is optional, just simply "gene" would also be acceptable.
* "wildcard":
    If true, all the values for this key will be automatically loaded in the left panel of the webclient, without the user needing to type anything in the search field. This is useful if the number of possible values is not too high, such as in the mid to low hundreds, so that the user can easily browse the list. The IDR `Phenotype search <https://idr.openmicroscopy.org/mapr/phenotype/?experimenter=-1>`_ serves as an example for this behaviour.
* "case_sensitive":
    Enables you to check the box for "Match case" in the search function.
* "label":
    Sets the label for a set of Map Annotations with the same Namespace.

In general, the IDR config (`here <https://github.com/IDR/deployment/blob/master/ansible/group_vars/omero-hosts.yml>`_ as a yaml representation) serves as a great example containing an extensive ``omero.web.mapr.config``.




User-edited Map Annotations
---------------------------

Map Annotations that are added using the webclient or Insight in the Key-Value panel
use a specific "client" namespace. We can therefore configure OMERO.mapr to search
for these annotations using the namespace ``openmicroscopy.org/omero/client/mapAnnotation``.
For example, to search for "Primary Antibody" or "Secondary Antibody" values, we can add:

::

    $ omero config append omero.web.mapr.config '{"menu": "antibody", "config":{"default":["Primary Antibody"], "all":["Primary Antibody", "Secondary Antibody"], "ns":["openmicroscopy.org/omero/client/mapAnnotation"], "label":"Antibody"}}'

We can add an "Antibodies" link to the top of the webclient page to take us to the Antibodies search page.
The link tooltip is "Find Antibody values".
The ``viewname`` should be in the form ``maprindex_{menu}`` where ``{menu}`` is the the ``menu`` value in the previous config.

::

    $ omero config append omero.web.ui.top_links '["Antibodies", {"viewname": "maprindex_antibody"}, {"title": "Find Antibody values"}]'

After restarting web, we can now search for Antibodies:

.. image:: https://user-images.githubusercontent.com/900055/40605069-063ff29a-6259-11e8-9295-3887dde0441f.png


We can also specify an empty list of keys to search for *any* value.

::

    $ omero config append omero.web.mapr.config '{"menu": "anyvalue", "config":{"default":["Any Value"], "all":[], "ns":["openmicroscopy.org/omero/client/mapAnnotation"], "label":"Any"}}'

    # Top link
    $ omero config append omero.web.ui.top_links '["Any Value", {"viewname": "maprindex_anyvalue"}, {"title": "Find Any Value"}]'

After restarting web, we can now search for any Value, such as "INCENP":

.. image:: https://user-images.githubusercontent.com/900055/40605101-1cd1925c-6259-11e8-93a8-e72af2e570d3.png


Other Map Annotations
---------------------

In this example we want to search
for Map Annotations of namespace ``openmicroscopy.org/mapr/gene`` searching for
attributes under the ``Gene Symbol`` and ``Gene Identifier`` keys.

::

    $ omero config append omero.web.mapr.config '{"menu": "gene","config": {"default": ["Gene Symbol"],"all": ["Gene Symbol", "Gene Identifier"],"ns": ["openmicroscopy.org/mapr/gene"],"label": "Gene"}}'

Now add a top link of ``Genes`` with tooltip ``Find Gene annotations`` that will take us to the ``gene`` search page. The ``query_string`` parameters are added to the URL, with ``"experimenter": -1``
specifying that we want to search across all users.

::

    $ omero config append omero.web.ui.top_links '["Genes", {"viewname": "maprindex_gene", "query_string": {"experimenter": -1}}, {"title": "Find Gene annotations"}]'


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
    image = conn.getObject('Image', 2917)
    image.linkAnnotation(map_ann)


Now restart OMERO.web as normal for the configuration above to take effect.
You should now be able to browse to a ``Genes`` page and search for
``CDC20`` or ``ENSG00000117399``.

Note that if you create multiple Map Annotations with the same Namespace, this will result in a more verbose layout in the webclient UI. It is preferable to combine all Key-Value pairs for a particular Namespace into a single Map Annotation.


External URL Favicons
^^^^^^^^^^^^^^^^^^^^^

Mapr can automatically convert URLs into favicon links.
To use this feature the key such as `Gene Identifier` must be in the "all" list of a config
as shown above and the `Gene Identifier` key-value pair must be followed by a key-value pair
called `Gene Identifier URL`.
A favicon linked to the external URL will be appended to the `Gene Identifier` row, and the
`Gene Identifier URL` key-value pair will be hidden.
OMERO.web must be configured with the Django redis cache
https://docs.openmicroscopy.org/omero/5/sysadmins/unix/install-web/walkthrough/omeroweb-install-centos7-ice3.6.html?highlight=redis#configuring-omero-web
which is used to cache the favicons that are obtained using a Google service.
If your IT structure utilizes a proxy and you are unwilling to set the proxy on a system level for the OMERO(.web) server you can set one directly in the ``requests.get()`` `method <https://github.com/ome/omero-mapr/blob/99dfb1a17418dbc996b9cb402e35db9d8e4b79f8/omero_mapr/views.py#L669>`_ like this

::

    proxies = {'http':'http://wwwproxy.<youproxy>.de:80','https':'http://wwwproxy.<yourproxy>.de:80'}
        r = requests.get(
            "%s%s" % (mapr_settings.FAVICON_WEBSERVICE, favdomain),
            stream=True, proxies = proxies)


Map Annotations on Wells/Images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For Plates the same Map Annotation that is on an Image has to also be on its corresponding Well for the Values to be correctly findable in the search function.
The reasons for this rather unintuitive behaviour are partly historical, as in the past no Annotations were shown for Images when browsing Screen-Plate-Well data, and partly performance related, as the query runs quicker by saving a JOIN when you're trying to find matching Plates if you only need to query Wells instead of Images.



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

2016-2021, The Open Microscopy Environment
