#
# Copyright (c) 2016 University of Dundee.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

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
from omeroweb.webclient.tree import _marshal_plate
from omeroweb.webclient.tree import _marshal_image


def _set_parameters(mapann_names=[], params=None,
                experimenter_id=-1,
                mapann_query=None, mapann_value=None,
                page=1, limit=settings.PAGE):
    if params is None:
        params = omero.sys.ParametersI()

    # Paging
    if page is not None and page > 0:
        params.page((page-1) * limit, limit)

    where_clause = []

    if mapann_names is not None and len(mapann_names) > 0:
        manlist = [rstring(str(n)) for n in mapann_names]
        params.add("filter", rlist(manlist))
        where_clause.append('mv.name in (:filter)')

    params.addString("ns", "openmicroscopy.org/omero/bulk_annotations")
    where_clause.append('a.ns = :ns')

    if experimenter_id is not None and experimenter_id != -1:
        params.addId(experimenter_id)
        where_clause.append('a.details.owner.id = :id')

    if mapann_query:
        params.addString("query", rstring("%s%%" % str(mapann_query).lower()))
        where_clause.append('lower(mv.value) like :query')

    if mapann_value:
        params.addString("value", mapann_value)
        where_clause.append('mv.value  = :value')

    return params, where_clause

def count_mapannotations(conn,
                         mapann_names=[], mapann_query=None,
                         group_id=-1, experimenter_id=-1):
    ''' Marshals genes

        @param conn OMERO gateway.
        @type conn L{omero.gateway.BlitzGateway}
        @param mapann_names The Map annotation name to filter by.
        @type mapann_names L{string}
        @param query The Map annotation value to filter using like.
        @type query L{string}
        @param group_id The Group ID to filter by or -1 for all groups,
        defaults to -1
        @type group_id L{long}
        @param experimenter_id The Experimenter (user) ID to filter by
        or -1 for all experimenters
        @type experimenter_id L{long}
    '''
    params, where_clause = _set_parameters(
        mapann_names=mapann_names, params=None,
        experimenter_id=-1,
        mapann_query=mapann_query, mapann_value=None,
        page=0, limit=settings.PAGE)

    service_opts = deepcopy(conn.SERVICE_OPTS)

    # Set the desired group context
    if group_id is None:
        group_id = -1
    service_opts.setOmeroGroup(group_id)

    qs = conn.getQueryService()

    q = """
        select count( distinct mv.value) as childCount
        from ImageAnnotationLink ial join ial.child a join a.mapValue mv
             join ial.parent i join i.wellSamples ws join ws.well w
             join w.plate p join p.screenLinks sl join sl.parent s
        where %s
        group by mv.value, a.ns
        """ % (" and ".join(where_clause))

    return len(unwrap(qs.projection(q, params, service_opts)))


def marshal_mapannotations(conn, mapann_names=[], mapann_query=None,
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
    params, where_clause = _set_parameters(
        mapann_names=mapann_names, params=None,
        experimenter_id=experimenter_id,
        mapann_query=mapann_query, mapann_value=None,
        page=page, limit=limit)

    service_opts = deepcopy(conn.SERVICE_OPTS)

    # Set the desired group context
    if group_id is None:
        group_id = -1
    service_opts.setOmeroGroup(group_id)

    qs = conn.getQueryService()

    # TODO:
    # a.details.owner.id as ownerId,
    # a as tag_details_permissions,

    q = """
        select new map(mv.value as value,
               a.ns as ns,
               count(distinct s.id) as childCount,
               count(distinct i.id) as imgCount)
        from ImageAnnotationLink ial join ial.child a join a.mapValue mv 
             join ial.parent i join i.wellSamples ws join ws.well w 
             join w.plate p join p.screenLinks sl join sl.parent s
        where %s
        group by mv.value, a.ns
        order by count(i.id) DESC
        """ % (" and ".join(where_clause))

    for e in qs.projection(q, params, service_opts):
        e = unwrap(e)
        e = [e[0]["value"],
             "%s (%d)" % (e[0]["value"], e[0]["imgCount"]),
             None,
             experimenter_id, #e[0]["ownerId"],
             {}, #e[0]["tag_details_permissions"],
             e[0]["ns"],
             e[0]["childCount"]]
        mapannotations.append(_marshal_tag(conn, e[0:7]))
    return mapannotations


def marshal_screens(conn, mapann_names=[], mapann_value=None,
                    group_id=-1, experimenter_id=-1,
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
    params, where_clause = _set_parameters(
        mapann_names=mapann_names, params=None,
        experimenter_id=experimenter_id,
        mapann_query=None, mapann_value=mapann_value,
        page=page, limit=limit)

    service_opts = deepcopy(conn.SERVICE_OPTS)

    # Set the desired group context
    if group_id is None:
        group_id = -1
    service_opts.setOmeroGroup(group_id)

    qs = conn.getQueryService()
    q = """
        select new map(screen.id as id,
               screen.name as name,
               screen.details.owner.id as ownerId,
               screen as screen_details_permissions,
               count(distinct p.id) as childCount,
               count(distinct i.id) as imgCount)
        from ImageAnnotationLink ial join ial.child a join a.mapValue mv 
             join ial.parent i join i.wellSamples ws join ws.well w 
             join w.plate p join p.screenLinks sl join sl.parent screen 
        where %s
        group by screen.id, screen.name
        order by lower(screen.name), screen.id
        """ % (" and ".join(where_clause))
        
    for e in qs.projection(q, params, service_opts):
        e = unwrap(e)
        e = [e[0]["id"],
             "%s (%d)" % (e[0]["name"], e[0]["imgCount"]),
             e[0]["ownerId"],
             e[0]["screen_details_permissions"],
             e[0]["childCount"],]
        ms = _marshal_screen(conn, e[0:5])
        ms.update({'extra': {'value': mapann_value}})
        screens.append(ms)

    return screens


def marshal_plates(conn, screen_id, 
                   mapann_value, mapann_names=[], 
                   group_id=-1, experimenter_id=-1,
                   page=1, limit=settings.PAGE):

    ''' Marshals plates

        @param conn OMERO gateway.
        @type conn L{omero.gateway.BlitzGateway}
        @param screen_id The Screen ID to filter by or `None` to
        not filter by a specific screen.
        defaults to `None`
        @type screen_id L{long}
        @param orphaned If this is to filter by orphaned data. Overridden
        by dataset_id.
        defaults to False
        @type orphaned Boolean
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
    plates = []
    params, where_clause = _set_parameters(
        mapann_names=mapann_names, params=None,
        experimenter_id=experimenter_id,
        mapann_query=None, mapann_value=mapann_value,
        page=page, limit=limit)

    params.addLong("sid", screen_id)
    where_clause.append('screen.id = :sid')

    service_opts = deepcopy(conn.SERVICE_OPTS)

    # Set the desired group context
    if group_id is None:
        group_id = -1
    service_opts.setOmeroGroup(group_id)

    qs = conn.getQueryService()
    q = """
        select new map(plate.id as id,
               plate.name as name,
               plate.details.owner.id as ownerId,
               plate as plate_details_permissions,
               count(distinct i.id) as childCount)
        from ImageAnnotationLink ial join ial.child a join a.mapValue mv 
             join ial.parent i join i.wellSamples ws join ws.well w 
             join w.plate plate join plate.screenLinks sl join sl.parent screen 
        where %s
        group by plate.id, plate.name
        order by lower(plate.name), plate.id
        """ % (" and ".join(where_clause))

    for e in qs.projection(q, params, service_opts):
        e = unwrap(e)
        e = [e[0]["id"],
             e[0]["name"],
             e[0]["ownerId"],
             e[0]["plate_details_permissions"],
             e[0]["childCount"]]
        mp = _marshal_plate(conn, e[0:5])
        mp.update({'extra': {'value': mapann_value}})
        plates.append(mp)

    return plates


def marshal_images(conn, plate_id, mapann_value,
                   mapann_names=[], load_pixels=False,
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
    params, where_clause = _set_parameters(
        mapann_names=mapann_names, params=None,
        experimenter_id=experimenter_id,
        mapann_query=None, mapann_value=mapann_value,
        page=page, limit=limit)

    service_opts = deepcopy(conn.SERVICE_OPTS)

    # Set the desired group context
    if group_id is None:
        group_id = -1
    service_opts.setOmeroGroup(group_id)

    from_join_clauses = []

    params.addLong("pid", plate_id)
    where_clause.append('plate.id = :pid')

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
        join image.wellSamples ws join ws.well well
        join well.plate plate join plate.screenLinks sl join sl.parent screen
    """)

    if load_pixels:
        # We use 'left outer join', since we still want images if no pixels
        from_join_clauses.append('left outer join image.pixels pix')

    q += """
        %s %s
        order by lower(image.name), well.id
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

def marshal_autocomplete(conn, query=None, mapann_names=None,
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
    if not query:
        return ['Pattern not found']
    params, where_clause = _set_parameters(
        mapann_names=mapann_names, params=None,
        experimenter_id=experimenter_id,
        mapann_query=query, mapann_value=None,
        page=page, limit=limit)

    service_opts = deepcopy(conn.SERVICE_OPTS)

    # Set the desired group context
    if group_id is None:
        group_id = -1
    service_opts.setOmeroGroup(group_id)

    qs = conn.getQueryService()

    q = """
        select new map(mv.value as value)
        from ImageAnnotationLink ial join ial.child a join a.mapValue mv 
        where %s
        group by mv.value
        order by lower(mv.value)
        """ % (" and ".join(where_clause))

    autocomplete = []
    for e in qs.projection(q, params, service_opts):
        e = unwrap(e)
        autocomplete.append({'value': e[0]["value"]})
    return autocomplete
