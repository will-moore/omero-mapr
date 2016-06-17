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

from omero.rtypes import rint

import omeroweb.webclient.show as omeroweb_show
import tree


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


def map_paths_to_object(conn, experimenter_id=None, group_id=None,
                        page_size=None, mapann_names=[], mapann_value=None):
    params, where_clause = tree._set_parameters(
        mapann_names=mapann_names, params=None,
        experimenter_id=experimenter_id,
        mapann_query=None, mapann_value=mapann_value,
        page=0, limit=settings.PAGE)

    service_opts = deepcopy(conn.SERVICE_OPTS)

    # Set the desired group context
    if group_id is None:
        group_id = -1
    service_opts.setOmeroGroup(group_id)

    qs = conn.getQueryService()

    # Hierarchies for this object
    paths = []

    q = """
        select distinct(mv.value)
        from ImageAnnotationLink ial join ial.child a join a.mapValue mv
        where %s """ % (" and ".join(where_clause))

    for e in qs.projection(q, params, service_opts):
        path = []

        # Always experimenter->mapValue
        path.append({
            'type': 'experimenter',
            'id': -1
        })

        path.append({
            'type': 'tag',
            'id': e[0].val
        })

        paths.append(path)

    return paths
