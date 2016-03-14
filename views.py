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

import logging
import traceback
from Ice import Exception as IceException
from omero import ApiUsageException, ServerError

from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest

from omeroweb.http import HttpJsonResponse
from omeroweb.webclient.decorators import login_required, render_response
from omeroweb.webclient.views import get_long_or_default, get_bool_or_default

import tree

from omeroweb.webclient import tree as webclient_tree

logger = logging.getLogger(__name__)

def get_str_or_default(request, name, default):
    """
    Retrieves a parameter from the request. If the parameter is not present
    the default is returned

    This does not catch exceptions as it makes sense to throw exceptions if
    the arguments provided do not pass basic type validation
    """
    val = None
    val_raw = request.GET.get(name, default)
    if val_raw is not None:
        val = str(val_raw)
    return val

def get_list_or_default(request, name, default):
    """
    Retrieves a list of parameters from the request. If list is not present
    the default is returned

    This does not catch exceptions as it makes sense to throw exceptions if
    the arguments provided do not pass basic type validation
    """
    return request.GET.getlist(name, default)

@login_required()
@render_response()
def index(request, **kwargs):
    return HttpResponse()

@login_required()
def api_experimenter_detail(request, experimenter_id, conn=None, **kwargs):
    # Validate parameter
    try:
        experimenter_id = long(experimenter_id)
        group_id = get_long_or_default(request, 'group', -1)
    except ValueError:
        return HttpResponseBadRequest('Invalid experimenter id')

    try:
        # Get the experimenter
        experimenter = webclient_tree.marshal_experimenter(
            conn=conn, experimenter_id=experimenter_id)
        mapann_names = get_list_or_default(request, 'name',
                                               ["Gene Symbol"])
        mapann_query = get_str_or_default(request, 'query', None)
        if mapann_query:
            experimenter['extra'] = {'query': mapann_query}

        experimenter['childCount'] = tree.count_mapannotations(
            conn=conn,
            mapann_names=mapann_names,
            mapann_query=mapann_query,
            group_id=group_id,
            experimenter_id=experimenter_id)

    except ApiUsageException as e:
        return HttpResponseBadRequest(e.serverStackTrace)
    except ServerError as e:
        return HttpResponseServerError(e.serverStackTrace)
    except IceException as e:
        return HttpResponseServerError(e.message)

    return HttpJsonResponse({'experimenter': experimenter})

@login_required()
def api_mapannotation_list(request, conn=None, **kwargs):
    # Get parameters
    try:
        page = get_long_or_default(request, 'page', 1)
        limit = get_long_or_default(request, 'limit', settings.PAGE)
        group_id = get_long_or_default(request, 'group', -1)
        experimenter_id = get_long_or_default(request, 'experimenter_id', -1)
        mapann_value = get_str_or_default(request, 'id', None)
        mapann_names = get_list_or_default(request, 'name',
                                           ["Gene Symbol"])
        mapann_query = get_str_or_default(request, 'query', None)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    # While this interface does support paging, it does so in a
    # very odd way. The results per page is enforced per query so this
    # will actually get the limit for projects, datasets (without
    # parents), screens and plates (without parents). This is fine for
    # the first page, but the second page may not be what is expected.

    mapannotations=[]
    screens=[]
    try:
        # Get all genes from map annotation
        if mapann_value is not None:
            screens = tree.marshal_screens(conn=conn,
                                         mapann_value=mapann_value,
                                         mapann_names=mapann_names,
                                         group_id=group_id,
                                         page=page,
                                         limit=limit)
        else:
            mapannotations = tree.marshal_mapannotations(conn=conn,
                                     mapann_names=mapann_names,
                                     mapann_query=mapann_query,
                                     group_id=group_id,
                                     experimenter_id=experimenter_id,
                                     page=page,
                                     limit=limit)

    except ApiUsageException as e:
        return HttpResponseBadRequest(e.serverStackTrace)
    except ServerError as e:
        return HttpResponseServerError(e.serverStackTrace)
    except IceException as e:
        return HttpResponseServerError(e.message)

    return HttpJsonResponse({'tags': mapannotations, 'screens': screens })


@login_required()
def api_plate_list(request, conn=None, **kwargs):
    ''' Get a list of plates
    '''
    # Get parameters
    try:
        page = get_long_or_default(request, 'page', 1)
        limit = get_long_or_default(request, 'limit', settings.PAGE)
        group_id = get_long_or_default(request, 'group', -1)
        load_pixels = get_bool_or_default(request, 'sizeXYZ', False)
        thumb_version = get_bool_or_default(request, 'thumbVersion', False)
        date = get_bool_or_default(request, 'date', False)
        experimenter_id = get_long_or_default(request,
                                              'experimenter_id', -1)
        screen_id = get_str_or_default(request, 'id', None)
        mapann_value = get_str_or_default(request, 'value', None)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    plates = []
    try:
        # Get the images
        plates = tree.marshal_plates(conn=conn,
                                     screen_id=screen_id,
                                     mapann_value=mapann_value,
                                     group_id=group_id,
                                     experimenter_id=experimenter_id,
                                     page=page,
                                     limit=limit)
    except ApiUsageException as e:
        return HttpResponseBadRequest(e.serverStackTrace)
    except ServerError as e:
        return HttpResponseServerError(e.serverStackTrace)
    except IceException as e:
        return HttpResponseServerError(e.message)

    return HttpJsonResponse({'plates': plates})


@login_required()
def api_image_list(request, conn=None, **kwargs):
    ''' Get a list of images
        Specifiying dataset_id will return only images in that dataset
        Specifying experimenter_id will return orpahned images for that
        user
        The orphaned images will include images which belong to the user
        but are not in any dataset belonging to the user
        Currently specifying both, experimenter_id will be ignored

    '''
    # Get parameters
    try:
        page = get_long_or_default(request, 'page', 1)
        limit = get_long_or_default(request, 'limit', settings.PAGE)
        group_id = get_long_or_default(request, 'group', -1)
        load_pixels = get_bool_or_default(request, 'sizeXYZ', False)
        thumb_version = get_bool_or_default(request, 'thumbVersion', False)
        date = get_bool_or_default(request, 'date', False)
        experimenter_id = get_long_or_default(request,
                                              'experimenter_id', -1)
        plate_id = get_str_or_default(request, 'id', None)
        mapann_value = get_str_or_default(request, 'value', None)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    images = []
    try:
        # Get the images
        images = tree.marshal_images(conn=conn,
                                     plate_id=plate_id,
                                     mapann_value=mapann_value,
                                     load_pixels=load_pixels,
                                     group_id=group_id,
                                     experimenter_id=experimenter_id,
                                     page=page,
                                     date=date,
                                     thumb_version=thumb_version,
                                     limit=limit)
    except ApiUsageException as e:
        return HttpResponseBadRequest(e.serverStackTrace)
    except ServerError as e:
        return HttpResponseServerError(e.serverStackTrace)
    except IceException as e:
        return HttpResponseServerError(e.message)

    return HttpJsonResponse({'images': images})

@login_required()
def mapannotations_autocomplete(request, conn=None, **kwargs):

    # Get parameters
    try:
        page = get_long_or_default(request, 'page', 1)
        limit = get_long_or_default(request, 'limit', settings.PAGE)
        group_id = get_long_or_default(request, 'group', -1)
        experimenter_id = get_long_or_default(request, 'experimenter_id', -1)
        query = get_str_or_default(request, 'query', None)
        mapann_names = get_list_or_default(request, 'name',
                                           ["Gene Symbol"])
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    # While this interface does support paging, it does so in a
    # very odd way. The results per page is enforced per query so this
    # will actually get the limit for projects, datasets (without
    # parents), screens and plates (without parents). This is fine for
    # the first page, but the second page may not be what is expected.

    autocomplete=[]
    try:
        autocomplete = tree.marshal_autocomplete(
            conn=conn,
            query=query,
            mapann_names=mapann_names,
            group_id=group_id,
            experimenter_id=experimenter_id,
            page=page,
            limit=limit)
    except ApiUsageException as e:
        return HttpResponseBadRequest(e.serverStackTrace)
    except ServerError as e:
        return HttpResponseServerError(e.serverStackTrace)
    except IceException as e:
        return HttpResponseServerError(e.message)

    return HttpJsonResponse({"suggestions": autocomplete})