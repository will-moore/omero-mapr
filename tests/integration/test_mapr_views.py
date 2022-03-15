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

import json
import pytest

from django.urls import reverse

from omeroweb.testlib import get_json


class TestMaprViews(object):

    @pytest.mark.parametrize('ac', (
        {'menu': 'organism', 'value': 'Homo sapiens',
         'res_value': {'value': 'Homo sapiens'}, 'count': 1},
        {'menu': 'organism', 'value': "value_doesn't_exist",
         'res_value': {}, 'count': 0},
        {'menu': 'gene', 'value': "cdc14",
         'res_value': {'value': 'cdc14'}, 'count': 3},

        # case sensitive
        # key doesnt exists, case sensitive
        {'menu': 'gene', 'value': 'CDC20', 'case_sensitive': True,
         'res_value': {}, 'count': 0},
        # key doesnt exists, case insensitive
        {'menu': 'gene', 'value': 'CDC20', 'case_sensitive': False,
         'res_value': {}, 'count': 0},

        # find matching key, case sensitive
        {'menu': 'gene', 'value': 'Cdc14', 'case_sensitive': True,
         'res_value': {'value': 'Cdc14'}, 'count': 1},
        # find matching key, case insensitive
        {'menu': 'gene', 'value': 'cDc14', 'case_sensitive': False,
         'res_value': {'value': 'cDc14'}, 'count': 3},
    ))
    def test_api_experimenter_list_query_string(self, imaprtest, ac):
        def _expected(menu, extra, count, uid):
            _res = {
                "experimenter": {
                    "omeName": menu.capitalize(),
                    "firstName": menu.capitalize(),
                    "extra": extra,
                    "lastName": "",
                    "id": uid,
                    "childCount": count,
                }
            }
            _res['experimenter']['extra'] = extra if extra else {}
            return json.loads(json.dumps(_res))

        request_url = reverse("mapannotations_api_experimenters",
                              args=[ac['menu']])
        data = {
            'value': ac['value'],
            # 'experimenter_id': -1 by default
        }
        try:
            cs = ac['case_sensitive']
        except KeyError:
            cs = False
        data['case_sensitive'] = cs
        ac['res_value']['case_sensitive'] = cs
        response = get_json(
            imaprtest.django_client, request_url, data)

        assert response == _expected(
            ac['menu'], ac['res_value'], ac['count'], -1)

    @pytest.mark.parametrize('ac', (
        {'menu': 'organism', 'value': 'Homo sapiens',
         'res_value': {'Homo sapiens': 2}},
        {'menu': 'organism', 'value': "value_doesn't_exist",
         'res_value': {}},
        {'menu': 'gene', 'value': "cdc14",
         'res_value': {'CDC14': 1, 'cdc14': 2, 'Cdc14': 1}},

        # case sensitive
        # key doesnt exists, case sensitive
        {'menu': 'gene', 'value': "value_doesn't_exist",
         'case_sensitive': True, 'res_value': {}},
        # key doesnt exists, case insensitive
        {'menu': 'gene', 'value': "value_doesn't_exist",
         'case_sensitive': False, 'res_value': {}},

        # find matching key, case sensitive
        {'menu': 'gene', 'value': 'Cdc14', 'case_sensitive': True,
         'res_value': {'Cdc14': 1}},
        # find matching key, case insensitive
        {'menu': 'gene', 'value': 'cDc14', 'case_sensitive': False,
         'res_value': {'CDC14': 1, 'cdc14': 2, 'Cdc14': 1}, 'count': 3},
    ))
    def test_api_mapannotations_query_string(self, imaprtest, ac):
        request_url = reverse("mapannotations_api_mapannotations",
                              args=[ac['menu']])
        data = {
            'value': ac['value'],
            'orphaned': True,
            # 'experimenter_id': -1 by default
        }
        try:
            data['case_sensitive'] = ac['case_sensitive']
        except KeyError:
            pass

        response = get_json(
            imaprtest.django_client, request_url, data)

        try:
            c = ac['count']
        except KeyError:
            c = len(ac['res_value'])
        assert len(response['maps']) == c

        if len(ac['res_value']) > 0:
            names = ["%s (%d)" % (k, v) for k, v in ac['res_value'].items()]
            for r in response['maps']:
                assert r['name'] in names
