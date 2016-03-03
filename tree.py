import time
import omero

from omero.rtypes import rlong, rstring, rlist, unwrap, wrap
from django.conf import settings
from django.http import Http404
from datetime import datetime
from copy import deepcopy

from omeroweb.webclient.tree import parse_permissions_css, build_clause
from omeroweb.webclient.tree import _marshal_tag
from omeroweb.webclient.tree import _marshal_screen
from omeroweb.webclient.tree import _marshal_image


def marshal_mapannotations(conn, mapann_names=None,
                           group_id=-1, experimenter_id=-1,
                           page=1, limit=settings.PAGE):
    ''' Marshals genes

        @param conn OMERO gateway.
        @type conn L{omero.gateway.BlitzGateway}
        @param mapann_names The Map annotation name to filter by.
        @type mapann_names L{string}
        @param group_id The Group ID to filter by or -1 for all groups,
        defaults to -1
        @type group_id L{long}
        @param experimenter_id The Experimenter (user) ID to filter by
        or -1 for all experimenters
        @type experimenter_id L{long}
        @param page Page number of results to get. `None` or 0 for no paging
        defaults to 1
        @type page L{long}
        @param limit The limit of results per page to get
        defaults to the value set in settings.PAGE
        @type page L{long}
    '''
    mapannotations = []
    params = omero.sys.ParametersI()
    params.addString("ns", "openmicroscopy.org/omero/bulk_annotations")

    manlist = list()
    for n in mapann_names:
        manlist.append(rstring(str(n).lower()))
    params.add("filter", rlist(manlist))

    service_opts = deepcopy(conn.SERVICE_OPTS)

    # Set the desired group context
    if group_id is None:
        group_id = -1
    service_opts.setOmeroGroup(group_id)

    # Paging
    if page is not None and page > 0:
        params.page((page-1) * limit, limit)

    where_clause = ''
    if experimenter_id is not None and experimenter_id != -1:
        params.addId(experimenter_id)
        where_clause = 'and a.details.owner.id = :id'
    qs = conn.getQueryService()

    # TODO:
    # a.details.owner.id as ownerId,
    # a as tag_details_permissions,
    q = """
        select new map(mv.value as value,
               a.ns as ns,
               count(i.id) as childCount)
        from ImageAnnotationLink ial join ial.child a join a.mapValue mv 
             join ial.parent i join i.wellSamples ws join ws.well w 
             join w.plate p join p.screenLinks sl join sl.parent s 
        where a.ns = :ns
        %s
        and lower(mv.name) in (:filter)
        group by mv.value, a.ns
        order by lower(mv.value)
        """ % (where_clause)

    for e in qs.projection(q, params, service_opts):
        e = unwrap(e)
        e = [e[0]["value"],
             e[0]["value"],
             e[0]["value"],
             experimenter_id, #e[0]["ownerId"],
             {}, #e[0]["tag_details_permissions"],
             e[0]["ns"],
             e[0]["childCount"]]
        mapannotations.append(_marshal_tag(conn, e[0:7]))
    return mapannotations


def marshal_screens(conn, mapann_value=None, group_id=-1, experimenter_id=-1,
                    page=1, limit=settings.PAGE):

    ''' Marshals screens

        @param conn OMERO gateway.
        @type conn L{omero.gateway.BlitzGateway}
        @param group_id The Group ID to filter by or -1 for all groups,
        defaults to -1
        @type group_id L{long}
        @param experimenter_id The Experimenter (user) ID to filter by
        or -1 for all experimenters
        @type experimenter_id L{long}
        @param page Page number of results to get. `None` or 0 for no paging
        defaults to 1
        @type page L{long}
        @param limit The limit of results per page to get
        defaults to the value set in settings.PAGE
        @type page L{long}
    '''
    screens = []
    params = omero.sys.ParametersI()
    params.addString("ns", "openmicroscopy.org/omero/bulk_annotations")
    params.addString("value", mapann_value)
    service_opts = deepcopy(conn.SERVICE_OPTS)

    # Set the desired group context
    if group_id is None:
        group_id = -1
    service_opts.setOmeroGroup(group_id)

    # Paging
    if page is not None and page > 0:
        params.page((page-1) * limit, limit)

    where_clause = ''
    if experimenter_id is not None and experimenter_id != -1:
        params.addId(experimenter_id)
        where_clause = 'and screen.details.owner.id = :id'
    qs = conn.getQueryService()
    q = """
        select new map(screen.id as id,
               screen.name as name,
               screen.details.owner.id as ownerId,
               screen as screen_details_permissions,
               (select count(spl.id) from ScreenPlateLink spl
                where spl.parent=screen.id) as childCount)
        from ImageAnnotationLink ial join ial.child a join a.mapValue mv 
             join ial.parent i join i.wellSamples ws join ws.well w 
             join w.plate p join p.screenLinks sl join sl.parent screen 
        where a.ns = :ns
        and mv.value  = :value
        %s
        group by screen.id, screen.name
        order by lower(screen.name), screen.id
        """ % where_clause
        
    for e in qs.projection(q, params, service_opts):
        e = unwrap(e)
        e = [mapann_value,
             e[0]["name"],
             e[0]["ownerId"],
             e[0]["screen_details_permissions"],
             e[0]["childCount"]]
        screens.append(_marshal_screen(conn, e[0:5]))

    return screens


def marshal_images(conn, mapann_value, load_pixels=False,
                   group_id=-1, experimenter_id=-1,
                   page=1, date=False, thumb_version=False,
                   limit=settings.PAGE):

    ''' Marshals images

        @param conn OMERO gateway.
        @type conn L{omero.gateway.BlitzGateway}
        @param mapann_value The Map annotation value to filter by.
        @type mapann_value L{string}
        @param load_pixels Whether to load the X,Y,Z dimensions
        @type load_pixels Boolean
        @param group_id The Group ID to filter by or -1 for all groups,
        defaults to -1
        @type group_id L{long}
        @param experimenter_id The Experimenter (user) ID to filter by
        or -1 for all experimenters
        @type experimenter_id L{long}
        @param page Page number of results to get. `None` or 0 for no paging
        defaults to 1
        @type page L{long}
        @param limit The limit of results per page to get
        defaults to the value set in settings.PAGE
        @type page L{long}

    '''
    images = []
    params = omero.sys.ParametersI()
    service_opts = deepcopy(conn.SERVICE_OPTS)

    # Set the desired group context
    if group_id is None:
        group_id = -1
    service_opts.setOmeroGroup(group_id)

    # Paging
    if page is not None and page > 0:
        params.page((page-1) * limit, limit)

    from_join_clauses = []
    where_clause = []

    params.addString("ns", "openmicroscopy.org/omero/bulk_annotations")
    where_clause.append('a.ns = :ns')

    if experimenter_id is not None and experimenter_id != -1:
        params.addId(experimenter_id)
        where_clause.append('image.details.owner.id = :id')
    if mapann_value is not None:
        params.addString("value", mapann_value)
        where_clause.append('mv.value  = :value')

    qs = conn.getQueryService()

    extraValues = ""
    if load_pixels:
        extraValues = """
             ,
             pix.sizeX as sizeX,
             pix.sizeY as sizeY,
             pix.sizeZ as sizeZ
             """

    if date:
        extraValues += """,
            image.details.creationEvent.time as date,
            image.acquisitionDate as acqDate
            """

    q = """
        select new map(image.id as id,
               image.name as name,
               image.details.owner.id as ownerId,
               image as image_details_permissions,
               image.fileset.id as filesetId %s)
        """ % extraValues

    from_join_clauses.append("""
        ImageAnnotationLink ial 
        join ial.child a 
        join a.mapValue mv 
        join ial.parent image
    """)

    if load_pixels:
        # We use 'left outer join', since we still want images if no pixels
        from_join_clauses.append('left outer join image.pixels pix')

    q += """
        %s %s
        order by lower(image.name), image.id
        """ % (' from ' + ' '.join(from_join_clauses),
               build_clause(where_clause, 'where', 'and'))

    for e in qs.projection(q, params, service_opts):
        e = unwrap(e)[0]
        d = [e["id"],
             e["name"],
             e["ownerId"],
             e["image_details_permissions"],
             e["filesetId"]]
        kwargs = {'conn': conn, 'row': d[0:5]}
        if load_pixels:
            d = [e["sizeX"], e["sizeY"], e["sizeZ"]]
            kwargs['row_pixels'] = d
        if date:
            kwargs['acqDate'] = e['acqDate']
            kwargs['date'] = e['date']

        images.append(_marshal_image(**kwargs))

    # Load thumbnails separately
    # We want version of most recent thumbnail (max thumbId) owned by user
    if thumb_version and len(images) > 0:
        userId = conn.getUserId()
        iids = [i['id'] for i in images]
        params = omero.sys.ParametersI()
        params.addIds(iids)
        params.add('thumbOwner', wrap(userId))
        q = """select image.id, thumbs.version from Image image
            join image.pixels pix join pix.thumbnails thumbs
            where image.id in (:ids)
            and thumbs.id = (
                select max(t.id)
                from Thumbnail t
                where t.pixels = pix.id
                and t.details.owner.id = :thumbOwner
            )
            """
        thumbVersions = {}
        for t in qs.projection(q, params, service_opts):
            iid, tv = unwrap(t)
            thumbVersions[iid] = tv
        # For all images, set thumb version if we have it...
        for i in images:
            if i['id'] in thumbVersions:
                i['thumbVersion'] = thumbVersions[i['id']]

    return images
