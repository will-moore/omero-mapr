
#
# Copyright (c) 2015 University of Dundee.
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


from mapannotations import views
from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name="mapindex"),
    # Generic container list. This is necessary as an experimenter may have
    # datasets/etc which do not belong to any project
    url(r'^api/mapannotations/$', views.api_mapannotation_list, name='api_mapannotations'),
    url(r'^api/screens/$', views.api_screens_list, name='api_screens'),

)
