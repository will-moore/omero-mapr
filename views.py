
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

@login_required()
@render_response()
def index(request, **kwargs):
    return HttpResponse()

@login_required()
def api_mapannotation_list(request, conn=None, **kwargs):
    # Get parameters
    try:
        page = get_long_or_default(request, 'page', 1)
        limit = get_long_or_default(request, 'limit', settings.PAGE)
        group_id = get_long_or_default(request, 'group', -1)
        experimenter_id = get_long_or_default(request, 'experimenter_id', -1)
        ann_name = get_str_or_default(request, 'id', None)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    # While this interface does support paging, it does so in a
    # very odd way. The results per page is enforced per query so this
    # will actually get the limit for projects, datasets (without
    # parents), screens and plates (without parents). This is fine for
    # the first page, but the second page may not be what is expected.

    mapannotations=[]
    screen=[]
    try:
        # Get all genes from map annotation
        if ann_name is not None:
            screen = tree.marshal_screens(conn=conn,
                                         ann_name=ann_name,
                                         group_id=group_id,
                                         page=page,
                                         limit=limit)
        else:
            mapannotations = tree.marshal_mapannotations(conn=conn,
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

    return HttpJsonResponse({'tags': mapannotations, 'screens': screen })


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
        ann_name = get_str_or_default(request, 'id', None)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    try:
        # Get the images
        images = tree.marshal_images(conn=conn,
                                     ann_name=ann_name,
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