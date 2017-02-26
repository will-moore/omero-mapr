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

from omero.model import ScreenI
from omero.rtypes import rstring
from omero.util.temp_files import create_path

from omeroweb.testlib import IWebTest


class IMaprTest(IWebTest):

    """
    Extends ITest
    """

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

    def set_name(self, obj, name):
        q = self.client.sf.getQueryService()
        up = self.client.sf.getUpdateService()
        obj = q.get(obj.__class__.__name__, obj.id.val)
        obj.setName(rstring(name))
        return up.saveAndReturnObject(obj)

    def create_screen(self, row_count, col_count):
        # TODO: remove 5.2 vs 5.3 compatibility
        try:
            plate = self.importPlates(plateRows=row_count,
                                      plateCols=col_count)[0]
        except AttributeError:
            plate = self.import_plates(plateRows=row_count,
                                       plateCols=col_count)[0]
        plate = self.set_name(plate, "Plate001")
        screen = ScreenI()
        screen.name = rstring("Screen001")
        screen.linkPlate(plate.proxy())
        return (self.client.sf.getUpdateService().saveAndReturnObject(screen),
                plate)

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
