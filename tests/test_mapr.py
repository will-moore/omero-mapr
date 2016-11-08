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

import json
import omero
from django.core.urlresolvers import reverse

from omeroweb.testlib import IWebTest


class TestMapr(IWebTest):

    def image_with_channels(self):
        """
        Returns a new foundational Image with Channel objects attached for
        view method testing.
        """
        pixels = self.pix(client=self.client)
        for the_c in range(pixels.getSizeC().val):
            channel = omero.model.ChannelI()
            channel.logicalChannel = omero.model.LogicalChannelI()
            pixels.addChannel(channel)
        image = pixels.getImage()
        return self.sf.getUpdateService().saveAndReturnObject(image)

    def test_basic(self):

        # Add project
        request_url = reverse("manage_action_containers",
                              args=["addnewcontainer"])
        data = {
            'folder_type': 'project',
            'name': 'foobar'
        }
        csrf_token = self.django_client.cookies['csrftoken'].value
        extra = {'HTTP_X_CSRFTOKEN': csrf_token}
        response = self.django_client.post(request_url, data=data, **extra)
        pid = json.loads(response.content).get("id")

        # Add dataset to the project
        request_url = reverse("manage_action_containers",
                              args=["addnewcontainer", "project", pid])
        data = {
            'folder_type': 'dataset',
            'name': 'foobar'
        }
        csrf_token = self.django_client.cookies['csrftoken'].value
        extra = {'HTTP_X_CSRFTOKEN': csrf_token}
        response = self.django_client.post(request_url, data=data, **extra)
        did = json.loads(response.content).get("id")

        # Link image to Dataset
        img = self.createTestImage(session=self.sf)
        request_url = reverse("api_links")
        data = {
            'dataset': {did: {'image': [img.id.val]}}
        }

        csrf_token = self.django_client.cookies['csrftoken'].value
        extra = {'HTTP_X_CSRFTOKEN': csrf_token}
        response = self.django_client.post(
            request_url, data=json.dumps(data),
            content_type="application/json", **extra)

        # add map annotation
        request_url = reverse("annotate_map")
        mapann = [['mapkey', 'mapvalue'], ['mapkey2', 'mapvalue2']]
        data = {
            'image': img.id.val,
            'mapAnnotation': json.dumps(mapann)
        }
        csrf_token = self.django_client.cookies['csrftoken'].value
        extra = {'HTTP_X_CSRFTOKEN': csrf_token}
        response = self.django_client.post(request_url, data=data, **extra)
        assert response.get('Content-Type') == 'application/json'
        res = json.loads(response.content)
        assert res

        # test autocomplete
        request_url = reverse("mapannotations_autocomplete",
                              args=["key"])
        data = {
            'value': 'map',
            'query': 'true'
        }
        response = self.django_client.get(request_url, data=data)
        assert response.get('Content-Type') == 'application/json'
        res = json.loads(response.content)

        assert res == [{'value': 'mapvalue'}, {'value': 'mapvalue2'}]
