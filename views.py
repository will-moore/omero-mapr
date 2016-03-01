
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

from Ice import Exception as IceException
from omero import ApiUsageException, ServerError

from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest

from omeroweb.http import HttpJsonResponse
from omeroweb.webclient.decorators import login_required, render_response
from omeroweb.webclient.views import get_long_or_default

import tree

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
        experimenter_id = get_long_or_default(request, 'id', -1)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    # While this interface does support paging, it does so in a
    # very odd way. The results per page is enforced per query so this
    # will actually get the limit for projects, datasets (without
    # parents), screens and plates (without parents). This is fine for
    # the first page, but the second page may not be what is expected.

    try:
        # Get all genes from map annotation
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

    return HttpJsonResponse({'mapannotations': mapannotations})

@login_required()
def api_screens_list(request, conn=None, **kwargs):
    # Get parameters
    try:
        page = get_long_or_default(request, 'page', 1)
        limit = get_long_or_default(request, 'limit', settings.PAGE)
        group_id = get_long_or_default(request, 'group', -1)
        node_id = get_long_or_default(request, 'id', None)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    # While this interface does support paging, it does so in a
    # very odd way. The results per page is enforced per query so this
    # will actually get the limit for projects, datasets (without
    # parents), screens and plates (without parents). This is fine for
    # the first page, but the second page may not be what is expected.

    try:
        # Get all genes from map annotation
        screens = tree.marshal_screens(conn=conn,
                                     node_id=node_id,
                                     group_id=group_id,
                                     page=page,
                                     limit=limit)

    except ApiUsageException as e:
        return HttpResponseBadRequest(e.serverStackTrace)
    except ServerError as e:
        return HttpResponseServerError(e.serverStackTrace)
    except IceException as e:
        return HttpResponseServerError(e.message)

    return HttpJsonResponse({'screens': screens})

