#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
# Author: Aleksandra Tarkowska <A(dot)Tarkowska(at)dundee(dot)ac(dot)uk>,
#
# Version: 1.0

import omero

from copy import deepcopy

from django.conf import settings
from map_settings import map_settings
from django.core.urlresolvers import reverse

from omero.rtypes import rint, rlong, unwrap

import omeroweb.webclient.show as omeroweb_show
import tree as map_tree


class MapShow(omeroweb_show.Show):

    omeroweb_show.Show.TOP_LEVEL_PREFIXES += ('map',)
    omeroweb_show.Show.SUPPORTED_OBJECT_TYPES += ('map',)

    def __init__(self, conn, request, menu):
        super(MapShow, self).__init__(conn, request, menu)

    def _find_first_selected(self):
        if len(self._initially_select) == 0:
            return None

        # tree hierarchy open to first selected object
        m = self.PATH_REGEX.match(self._initially_select[0])
        if m is None:
            return None
        first_obj = m.group('object_type')
        # if we're showing a tag, make sure we're on the tags page...
        if first_obj in ["map"] and self.menu not in map_settings.MENU_MAPPER:
            # redirect to usertags/?show=tag-123
            raise omeroweb_show.IncorrectMenuError(
                reverse(viewname="mapindex") +
                "?show=" + self._initially_select[0].replace(".id", "")
            )
        # if in mapannotations app hierachy is different
        if self.menu in map_settings.MENU_MAPPER:
            first_selected = None
            try:
                key = m.group('key')
                value = m.group('value')
                if key == 'id':
                    value = long(value)
                attributes = {key: value}
                # Set context to 'cross-group'
                self.conn.SERVICE_OPTS.setOmeroGroup('-1')
                first_selected = self._load_first_selected(
                    first_obj, attributes)
            except:
                pass
            if first_obj not in self.TOP_LEVEL_PREFIXES:
                # Need to see if first item has parents
                if first_selected is not None:
                    for p in first_selected.getAncestry():
                        # If 'Well' is a parent, we have stared with Image.
                        # We want to start again at 'Well' to
                        # _load_first_selected with well, so we get
                        # 'acquisition' in ancestors.
                        if p.OMERO_CLASS == "Well":
                            return self._find_first_selected()
                        if p.OMERO_CLASS == "Acquisition":
                            return self._find_first_selected()
                        if first_obj == "tag":
                            # Parents of tags must be tagset (no OMERO_CLASS)
                            self._initially_open.insert(
                                0, "tagset-%s" % p.getId())
                        else:
                            self._initially_open.insert(
                                0,
                                "%s-%s" % (p.OMERO_CLASS.lower(), p.getId())
                            )
                        self._initially_open_owner = p.details.owner.id.val
                    m = self.PATH_REGEX.match(self._initially_open[0])
                    if m.group('object_type') == 'image':
                        self._initially_open.insert(0, "orphaned-0")
            return first_selected
        return super(MapShow, self)._find_first_selected()

    def _load_first_selected(self, first_obj, attributes):
        first_selected = None
        if first_obj in ["map"]:
            first_selected = self._load_mapannotations(attributes)
            self._initially_open_owner = first_selected.details.owner.id.val
        else:
            first_selected = super(MapShow, self) \
                ._load_first_selected(first_obj, attributes)
        return first_selected

    def _load_mapannotations(self, attributes):
        """
        TODO: make sure it is calling right context (groups, users)
        """
        if 'value' in attributes:
            service_opts = deepcopy(self.conn.SERVICE_OPTS)
            params = omero.sys.ParametersI()
            params.addString("mvalue", attributes['value'])
            f = omero.sys.Filter()
            f.limit = rint(1)
            params.theFilter = f

            q = """
                select distinct (a)
                from ImageAnnotationLink ial join ial.child a
                join a.mapValue mv
                where mv.value = :mvalue
            """
            qs = self.conn.getQueryService()
            m = qs.findByQuery(q, params, service_opts)
            # hardcode to always tell to load all users
            m.details.owner = omero.model.ExperimenterI(-1L, False)
            return omero.gateway.MapAnnotationWrapper(self.conn, m)

omeroweb_show.Show = MapShow


def map_paths_to_object(conn, mapann_names=[], mapann_value=None,
                        screen_id=None, plate_id=None, image_id=None,
                        experimenter_id=None, group_id=None, page_size=None):

    qs = conn.getQueryService()
    params, where_clause = map_tree._set_parameters(
        mapann_names=mapann_names, params=None,
        experimenter_id=experimenter_id,
        mapann_query=None, mapann_value=mapann_value,
        page=0, limit=settings.PAGE)

    service_opts = deepcopy(conn.SERVICE_OPTS)

    if group_id is not None:
        service_opts.setOmeroGroup(group_id)

    q = '''
        select
            distinct new map (mv.value as map_value,
        '''

    q_select = []
    if screen_id:
        q_select.append(" sl.parent.id as screen_id ")
    elif plate_id:
        q_select.append(" sl.parent.id as screen_id ")
        q_select.append(" p.id as plate_id")
    elif image_id:
        q_select.append(" sl.parent.id as screen_id ")
        q_select.append(" p.id as plate_id ")
        q_select.append(" i.id as image_id ")

    if q_select:
        q += ", ".join(q_select) + ", "

    q += ''' count(i.id) as imgCount)
        from ImageAnnotationLink ial join ial.child a join a.mapValue mv
            join ial.parent i
            join i.wellSamples ws
            join ws.well w
            join w.plate p
            join p.screenLinks sl
        '''

    q += " where 1=1 and "
    if image_id:
        q += " i.id = :iid and "
        params.add('iid', rlong(image_id))
    elif screen_id:
        q += " sl.parent.id = :sid and "
        params.add('sid', rlong(screen_id))
    elif plate_id:
        q += " p.id = :pid and "
        params.add('pid', rlong(plate_id))

    if len(where_clause) > 0:
        q += ' and '.join(where_clause)

    q += " group by mv.value "
    q_groupby = []
    if screen_id:
        q_groupby.append(" sl.parent.id ")
    elif plate_id:
        q_groupby.append(" sl.parent.id ")
        q_groupby.append(" p.id ")
    elif image_id:
        q_groupby.append(" sl.parent.id ")
        q_groupby.append(" p.id ")
        q_groupby.append(" i.id ")

    if q_groupby:
        q += ", " + ", ".join(q_groupby)

    # Hierarchies for this object
    paths = []

    for e in unwrap(qs.projection(q, params, service_opts)):
        path = []

        # Experimenter is always found
        path.append({
            'type': 'experimenter',
            'id': -1
        })

        try:
            mapValue = e[0]["map_value"]
            ds = {
                'type': 'tag',
                'id': mapValue,
            }
            path.append(ds)
        except:
            pass

        # If it is experimenter->project->dataset->image
        try:
            path.append({
                'type': 'screen',
                'id': e[0]["screen_id"]
            })
        except:
            pass

        # If it is experimenter->dataset->image or
        # experimenter->project->dataset->image
        try:
            plateId = e[0]["plate_id"]
            ds = {
                'type': 'plate',
                'id': plateId,
            }
            path.append(ds)
        except:
            pass
        # Image always present
        try:
            path.append({
                'type': 'image',
                'id': e[0]["image_id"]
            })
        except:
            pass
        paths.append(path)
    return paths
