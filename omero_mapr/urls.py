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

from . import views
from django.urls import re_path
from django.urls import reverse
from django.utils.functional import lazy
from django.views.generic import RedirectView
from django.views.decorators.cache import never_cache

from .mapr_settings import mapr_settings

reverse_lazy = lazy(reverse, str)

# concatenate aliases to use in url regex
CONFIG_REGEX = "(%s)" % ("|".join(mapr_settings.CONFIG))
DEFAULT_CONFIG = list(mapr_settings.CONFIG.keys())[0]

urlpatterns = []

# alias
for m in mapr_settings.CONFIG:
    urlpatterns.append(
        re_path(r'^%s/$' % m,
                views.index, {'menu': m},
                name="maprindex_%s" % m)
        )

urlpatterns += [

    # core
    re_path(r'^$', never_cache(
            RedirectView.as_view(
                url=reverse_lazy('maprindex_%s' % DEFAULT_CONFIG),
                permanent=True,
                query_string=True)),
            name="maprindex"),

    re_path(r'^api/config/$', views.api_mapr_config, name='mapr_config'),

    re_path(r'^api/(?P<menu>%s)/count/$' % (CONFIG_REGEX),
            views.api_experimenter_list,
            name='mapannotations_api_experimenters'),
    re_path(r'^api/(?P<menu>%s)/datasets/$' % CONFIG_REGEX,
            views.api_datasets_list,
            name='mapannotations_api_datasets'),
    re_path(r'^api/(?P<menu>%s)/plates/$' % CONFIG_REGEX,
            views.api_plate_list,
            name='mapannotations_api_plates'),
    re_path(r'^api/(?P<menu>%s)/images/$' % CONFIG_REGEX,
            views.api_image_list,
            name='mapannotations_api_images'),

    re_path(r'^api/(?P<menu>%s)/paths_to_object/$' % CONFIG_REGEX,
            views.api_paths_to_object,
            name='mapannotations_api_paths_to_object'),

    re_path(r'^metadata_details/(?P<c_type>%s)/$' % CONFIG_REGEX,
            views.load_metadata_details,
            name="mapannotations_load_metadata_details"),

    re_path(r'^api/(?P<menu>%s)/annotations/$' % CONFIG_REGEX,
            views.api_annotations,
            name='mapannotations_api_annotations'),

    # must be last on the list
    re_path(r'^api/(?P<menu>%s)/$' % CONFIG_REGEX,
            views.api_mapannotation_list,
            name='mapannotations_api_mapannotations'),

    # autocomplete
    re_path(r'^api/autocomplete/(?P<menu>%s)/$' % CONFIG_REGEX,
            views.mapannotations_autocomplete,
            name='mapannotations_autocomplete'),

    # favicon
    re_path(r'^favicon/$',
            views.mapannotations_favicon,
            name='mapannotations_favicon'),

]
