#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
#
# Copyright (c) 2016,2017 University of Dundee.
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
# Author: Aleksandra Tarkowska <A(dot)Tarkowska(at)dundee(dot)ac(dot)uk>.
#
# Version: 1.0
#

import pytest

from django.core.urlresolvers import reverse, NoReverseMatch

from omeroweb.testlib import IWebTest, _get_response


@pytest.fixture
def empty_settings(settings):
    settings.MAPR_CONFIG = {}


class TestMapr(IWebTest):

    def test_settings(self, settings):
        assert len(settings.MAPR_CONFIG.keys()) > 0
        for menu in settings.MAPR_CONFIG.keys():
            request_url = reverse("maprindex_%s" % menu)
            _get_response(self.django_client, request_url, {}, status_code=200)

    @pytest.mark.xfail(raises=StopIteration)
    def test_empty_settings(self, empty_settings):
        # test empty config
        reverse("maprindex")

    @pytest.mark.parametrize('menu', ['foo', '', 'mygenes'])
    def test_bad_settings(self, settings, menu):
        assert menu not in settings.MAPR_CONFIG.keys()
        with pytest.raises(NoReverseMatch) as excinfo:
            request_url = reverse("maprindex_%s" % menu)
            _get_response(self.django_client, request_url, {}, status_code=200)
        regx = r"Reverse for 'maprindex_%s'.*" % menu
        assert excinfo.match(regx)
