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

from omero.model import ScreenI, PlateI, WellI, WellSampleI, ScreenPlateLinkI
from omero.rtypes import rint, rstring, unwrap
from omero.util.temp_files import create_path
from omero.util.populate_metadata import BulkToMapAnnotationContext
from omero.util.populate_metadata import ParsingContext

from django.core.urlresolvers import reverse

from omeroweb.testlib import IWebTest, _get_response_json
from omero.constants.namespaces import NSBULKANNOTATIONS


class IMaprTest(IWebTest):
    """
    Abstract class derived from ITest which implements helpers for creating
    Django clients using django.test
    """

    # TODO: move to testlib, common from test_populate.py
    def create_csv(
        self,
        col_names="Well,Well Type,Concentration",
        row_data=("A1,Control,0", "A2,Treatment,10")
    ):

        csv_file_name = create_path("test", ".csv")
        csv_file = open(csv_file_name, 'w')
        try:
            csv_file.write(col_names)
            csv_file.write("\n")
            csv_file.write("\n".join(row_data))
        finally:
            csv_file.close()
        return str(csv_file_name)

    def create_plate(self, row_count, col_count):
        plates = self.import_plates(plateRows=row_count,
                                    plateCols=col_count)
        return plates[0]

    def create_plate1(self, row_count, col_count):
        uuid = self.ctx.sessionUuid

        def create_well(row, column):
            well = WellI()
            well.row = rint(row)
            well.column = rint(column)
            ws = WellSampleI()
            image = self.new_image(name=uuid)
            ws.image = image
            well.addWellSample(ws)
            return well

        plate = PlateI()
        plate.name = rstring("TestPopulateMetadata%s" % uuid)
        for row in range(row_count):
            for col in range(col_count):
                well = create_well(row, col)
                plate.addWell(well)
        return self.client.sf.getUpdateService().saveAndReturnObject(plate)

    def new_screen(self, name=None, description=None):
        """
        Creates a new screen object.
        :param name: The screen name. If None, a UUID string will be used
        :param description: The screen description
        """
        return self.new_object(ScreenI, name=name, description=description)

    def make_screen(self, name=None, description=None, client=None):
        """
        Creates a new screen instance and returns the persisted object.
        :param name: The screen name. If None, a UUID string will be used
        :param description: The screen description
        :param client: The client to use to create the object
        """
        if client is None:
            client = self.client
        screen = self.new_screen(name=name, description=description)
        return client.sf.getUpdateService().saveAndReturnObject(screen)

    def get_screen_annotations(self):
        query = """select s from Screen s
            left outer join fetch s.annotationLinks links
            left outer join fetch links.child
            where s.id=%s""" % self.screen.id.val
        qs = self.client.sf.getQueryService()
        screen = qs.findByQuery(query, None)
        anns = screen.linkedAnnotationList()
        return anns
    # TODO: END move to testlib, common from test_populate.py


class TestMapr(IMaprTest):

    def setup_method(self):
        super(IMaprTest, self).setup_class()
        self.screen = self.make_screen("test_screen_mapr")
        row_count = 1
        col_count = 2
        self.plate = self.create_plate1(row_count, col_count)
        plate_name = self.plate.name.val

        link = ScreenPlateLinkI()
        link.setParent(self.screen.proxy())
        link.setChild(self.plate.proxy())
        self.client.sf.getUpdateService().saveAndReturnObject(link)

        gene = {
            'col_names':
                "Plate,Well Number,Well,Gene Identifier,Gene Symbol,Organism",
            'row_data': (
                "%s,1,A1,CDC20,ENSG00000117399,Homo sapiens" % plate_name,
                "%s,2,A2,CDC20,YGL116W,Mouse" % plate_name
            )
        }
        self.csv_name = self.create_csv(gene['col_names'], gene['row_data'])

        ctx = ParsingContext(self.client, self.screen.proxy(),
                             file=self.csv_name)
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

    def test_basic(self):

        # test autocomplete
        request_url = reverse("mapannotations_autocomplete",
                              args=["gene"])
        data = {
            'value': 'cdc',
            'query': 'true'
        }
        response = _get_response_json(self.django_client, request_url, data)

        assert response == [{'value': 'CDC20'}]
