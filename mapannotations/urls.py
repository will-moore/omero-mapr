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


from mapannotations import views
from django.conf.urls import url, patterns


urlpatterns = patterns(
    '',
    url(r'^$', views.index,
        name="mapindex"),

    url(r'^api/experimenters/(?P<experimenter_id>([-1]|[0-9])+)/$',
        views.api_experimenter_detail,
        name='mapannotations_api_experimenter'),
    url(r'^api/mapannotations/$', views.api_mapannotation_list,
        name='mapannotations_api_mapannotations'),
    url(r'^api/plates/$', views.api_plate_list,
        name='mapannotations_api_plates'),
    url(r'^api/images/$', views.api_image_list,
        name='mapannotations_api_images'),

    url(r'^api/paths_to_object/$', views.api_paths_to_object,
        name='mapannotations_api_paths_to_object'),

    url(r'^autocomplete/$', views.mapannotations_autocomplete,
        name='mapannotations_autocomplete'),

)
