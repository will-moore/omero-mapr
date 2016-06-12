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
from django.core.urlresolvers import reverse

import omeroweb.webclient.show as omeroweb_show


class MapShow(omeroweb_show.Show):

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
        if first_obj in ["map"] and self.menu != "mapannotations":
            # redirect to usertags/?show=tag-123
            raise omeroweb_show.IncorrectMenuError(
                reverse(viewname="mapindex") +
                "?show=" + self._initially_select[0].replace(".id", "")
            )
        super(MapShow, self)._find_first_selected()

omeroweb_show.Show = MapShow


def map_paths_to_object(conn, experimenter_id=None, group_id=None,
                        page_size=None, map_value=None):
    qs = conn.getQueryService()
    if page_size is None:
        page_size = settings.PAGE

    service_opts = deepcopy(conn.SERVICE_OPTS)

    if group_id is not None:
        service_opts.setOmeroGroup(group_id)

    # Hierarchies for this object
    paths = []

    q = """
        select distinct(mv.value)
        from ImageAnnotationLink ial join ial.child a join a.mapValue mv
        where mv.value = :mvalue
    """

    params = omero.sys.ParametersI()
    params.addString("mvalue", map_value)

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
