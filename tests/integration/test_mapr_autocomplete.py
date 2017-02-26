#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
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
# Author: Aleksandra Tarkowska <A(dot)Tarkowska(at)dundee(dot)ac(dot)uk>.
#
# Version: 1.0
#

import os
import pytest

from django.core.urlresolvers import reverse

from omero.constants.namespaces import NSBULKANNOTATIONS
from omero.rtypes import unwrap
from omero.util.populate_metadata import BulkToMapAnnotationContext
from omero.util.populate_metadata import ParsingContext

from omero_mapr.testlib import IMaprTest
from omeroweb.testlib import _get_response_json


class TestMaprAutocomplete(IMaprTest):

    def setup_method(self, method):
        row_count = 1
        col_count = 6
        self.screen, self.plate = self.create_screen(row_count, col_count)

        csv = os.path.join(os.path.dirname(__file__),
                           'bulk_to_map_annotation_context_ns.csv')

        ctx = ParsingContext(self.client, self.screen.proxy(), file=csv)
        ctx.parse()
        ctx.write_to_omero()

        cfg = os.path.join(
            os.path.dirname(__file__), 'bulk_to_map_annotation_context.yml')

        # Get file annotations
        anns = self.get_screen_annotations()
        # Only expect a single annotation which is a 'bulk annotation'
        assert len(anns) == 1
        table_file_ann = anns[0]
        assert unwrap(table_file_ann.getNs()) == NSBULKANNOTATIONS
        fileid = table_file_ann.file.id.val

        ctx = BulkToMapAnnotationContext(
            self.client, self.screen.proxy(), fileid=fileid, cfg=cfg)
        ctx.parse()
        ctx.write_to_omero()

    @pytest.mark.parametrize('ac', (
        {'menu': 'gene', 'value': None, 'search_value': 'CDC20'},
        {'menu': 'organism', 'value': 'Homo sapiens', 'search_value': 'homo'},
        {'menu': 'gene', 'value': "beta'Cop", 'search_value': "'"},
        {'menu': 'gene', 'value': "123 (abc%def)", 'search_value': "%"},
    ))
    def test_autocomplete_default(self, ac):
        # test autocomplete
        request_url = reverse("mapannotations_autocomplete",
                              args=[ac['menu']])
        data = {
            'value': ac['search_value'],
            'query': 'true',
        }
        response = _get_response_json(self.django_client, request_url, data)

        res = []
        if ac['value'] is not None:
            res = [{'value': ac['value']}]
        assert response == res

    @pytest.mark.parametrize('ac', (
        {'menu': 'gene', 'value': 'CDC14',
         'search_value': 'CDC', 'case_sensitive': True},
        {'menu': 'gene', 'value': 'cdc14',
         'search_value': 'cdc', 'case_sensitive': True},
        {'menu': 'gene', 'value': "beta'Cop",
         'search_value': "'", 'case_sensitive': True},
    ))
    def test_autocomplete_case_sensitive(self, ac):
        # test autocomplete
        request_url = reverse("mapannotations_autocomplete",
                              args=[ac['menu']])
        data = {
            'value': ac['search_value'],
            'case_sensitive': ac['case_sensitive'],
            'query': 'true',
        }
        response = _get_response_json(self.django_client, request_url, data)

        assert response == [{'value': ac['value']}]

    @pytest.mark.parametrize('ac', (
        {'menu': 'gene', 'values': ('CDC14', 'cdc14', 'Cdc14'),
         'search_value': 'cdc', 'case_sensitive': False},
    ))
    def test_autocomplete_case_insensitive(self, ac):
        # test autocomplete
        request_url = reverse("mapannotations_autocomplete",
                              args=[ac['menu']])
        data = {
            'value': ac['search_value'],
            'case_sensitive': ac['case_sensitive'],
            'query': 'true',
        }
        response = _get_response_json(self.django_client, request_url, data)
        res = [r['value'] for r in response]

        assert len(res) == len(ac['values'])
        assert sorted(res) == sorted(ac['values'])
