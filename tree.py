import time
import omero

from omero.rtypes import rlong, unwrap, wrap
from django.conf import settings
from django.http import Http404
from datetime import datetime
from copy import deepcopy

from omeroweb.webclient.tree import parse_permissions_css
def _marshal_mapannotation(conn, row):
    ''' Given a Genes row (list) marshals it into a dictionary.  Order
        and type of columns in row is:
          * id (rlong)
          * name (rstring)
          * details.owner.id (rlong)
          * details.permissions (dict)
          * child_count (rlong)

        @param conn OMERO gateway.
        @type conn L{omero.gateway.BlitzGateway}
        @param row The Project row to marshal
        @type row L{list}
    '''
    project_id, name, owner_id, permissions, child_count = row
    project = dict()
    project['id'] = unwrap(project_id)
    project['value'] = unwrap(name)
    project['ownerId'] = unwrap(owner_id)
    project['childCount'] = unwrap(child_count)
    project['permsCss'] = \
        parse_permissions_css(permissions, unwrap(owner_id), conn)
    return project


def marshal_mapannotations(conn, group_id=-1, experimenter_id=-1,
                  page=1, limit=settings.PAGE):
    ''' Marshals genes

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
    mapannotations = []
    params = omero.sys.ParametersI()
    params.addString("ns", "openmicroscopy.org/omero/bulk_annotations")
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

    q = """
        select new map(a.id as id,
               mv.value as value,
               a.details.owner.id as ownerId,
               a as a_details_permissions,
               count(s.id) as childCount)
        from ImageAnnotationLink ial join ial.child a join a.mapValue mv 
             join ial.parent i join i.wellSamples ws join ws.well w 
             join w.plate p join p.screenLinks sl join sl.parent s 
        where a.ns = :ns
        %s
        group by a.id, mv.value
        order by lower(mv.value), a.id
        """ % (where_clause)

    for e in qs.projection(q, params, service_opts):
        e = unwrap(e)
        e = [e[0]["id"], e[0]["value"], e[0]["ownerId"],
             e[0]["a_details_permissions"], e[0]["childCount"]]
        mapannotations.append(_marshal_mapannotation(conn, e[0:5]))
    return mapannotations

def _marshal_screen(conn, row):
    ''' Given a Screen row (list) marshals it into a dictionary.  Order and
        type of columns in row is:
          * id (rlong)
          * name (rstring)
          * details.owner.id (rlong)
          * details.permissions (dict)
          * child_count (rlong)

        @param conn OMERO gateway.
        @type conn L{omero.gateway.BlitzGateway}
        @param row The Screen row to marshal
        @type row L{list}
    '''

    screen_id, name, owner_id, permissions, child_count = row
    screen = dict()
    screen['id'] = unwrap(screen_id)
    screen['name'] = unwrap(name)
    screen['ownerId'] = unwrap(owner_id)
    screen['childCount'] = unwrap(child_count)
    screen['permsCss'] = \
        parse_permissions_css(permissions, unwrap(owner_id), conn)
    return screen


def marshal_screens(conn, node_id=None, group_id=-1, experimenter_id=-1,
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
    params.addLong("aid", node_id)
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
        and a.id = :aid
        %s
        group by screen.id, screen.name
        order by lower(screen.name), screen.id
        """ % where_clause
        
    for e in qs.projection(q, params, service_opts):
        e = unwrap(e)
        e = [e[0]["id"],
             e[0]["name"],
             e[0]["ownerId"],
             e[0]["screen_details_permissions"],
             e[0]["childCount"]]
        screens.append(_marshal_screen(conn, e[0:5]))

    return screens
