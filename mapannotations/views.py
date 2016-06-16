#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
# Author: Aleksandra Tarkowska <A(dot)Tarkowska(at)dundee(dot)ac(dot)uk>,
#
# Version: 1.0


import logging

from Ice import Exception as IceException
from omero import ApiUsageException, ServerError

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseServerError, HttpResponseBadRequest, \
    HttpResponseRedirect

import show
import omeroweb.webclient.views

from omeroweb.http import HttpJsonResponse
from omeroweb.webclient.decorators import login_required, render_response
from omeroweb.webclient.views import get_long_or_default, get_bool_or_default
from omeroweb.webclient.views import switch_active_group
from omeroweb.webclient.views import fake_experimenter
from omeroweb.webclient.forms import GlobalSearchForm, ContainerForm
from omeroweb.webclient.show import Show, IncorrectMenuError

import tree

from omeroweb.webclient import tree as webclient_tree
from omeroweb.webclient import views as webclient_views
from omeroweb.webclient.views import api_annotations \
    as webclient_api_annotations


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
def index(request, conn=None, url=None, **kwargs):
    """
    This view handles most of the top-level pages, as specified by 'menu' E.g.
    userdata, usertags, history, search etc.
    Query string 'path' that specifies an object to display in the data tree
    is parsed.
    We also prepare the list of users in the current group, for the
    switch-user form. Change-group form is also prepared.
    """
    request.session.modified = True
    menu = "mapannotations"
    template = "mapannotations/mapannotations.html"

    # tree support
    show = Show(conn, request, menu)

    # Constructor does no loading.  Show.first_selected must be called first
    # in order to set up our initial state correctly.
    try:
        first_sel = show.first_selected
    except IncorrectMenuError, e:
        return HttpResponseRedirect(e.uri)
    # We get the owner of the top level object, E.g. Project
    # Actual api_paths_to_object() is retrieved by jsTree once loaded
    initially_open_owner = show.initially_open_owner

    # need to be sure that tree will be correct omero.group
    if first_sel is not None:
        switch_active_group(request, first_sel.details.group.id.val)

    # search support
    init = {}
    global_search_form = GlobalSearchForm(data=request.POST.copy())

    # get url without request string - used to refresh page after switch
    # user/group etc
    url = reverse(viewname="mapindex")

    # validate experimenter is in the active group
    active_group = (request.session.get('active_group') or
                    conn.getEventContext().groupId)
    # prepare members of group...
    leaders, members = conn.getObject(
        "ExperimenterGroup", active_group).groupSummary()
    userIds = [u.id for u in leaders]
    userIds.extend([u.id for u in members])
    users = []
    if len(leaders) > 0:
        users.append(("Owners", leaders))
    if len(members) > 0:
        users.append(("Members", members))
    users = tuple(users)

    # check any change in experimenter...
    user_id = request.GET.get('experimenter')
    if initially_open_owner is not None:
        if (request.session.get('user_id', None) != -1):
            # if we're not already showing 'All Members'...
            user_id = initially_open_owner
    try:
        user_id = long(user_id)
    except:
        user_id = None
        # ... or check that current user is valid in active group
        user_id = request.session.get('user_id', None)
        if user_id is None or int(user_id) not in userIds:
            if user_id != -1:           # All users in group is allowed
                user_id = conn.getEventContext().userId

    request.session['user_id'] = user_id

    myGroups = list(conn.getGroupsMemberOf())
    myGroups.sort(key=lambda x: x.getName().lower())
    groups = myGroups

    new_container_form = ContainerForm()

    context = {
        'menu': menu,
        'init': init,
        'myGroups': myGroups,
        'new_container_form': new_container_form,
        'global_search_form': global_search_form}
    context['groups'] = groups
    context['active_group'] = conn.getObject(
        "ExperimenterGroup", long(active_group))
    context['active_user'] = conn.getObject("Experimenter", long(user_id))
    context['initially_select'] = show.initially_select
    context['isLeader'] = conn.isLeader()
    context['current_url'] = url
    context['page_size'] = settings.PAGE
    context['template'] = template

    return context


@login_required()
def api_paths_to_object(request, conn=None, **kwargs):
    """
    This override omeroweb.webclient.api_paths_to_object
    to support custom path to map.value
    Example to go to the image with id 1 somewhere in the tree.
    http://localhost:8000/webclient/?show=map.value-abc

    TODO: support alias for map.value
    """

    try:
        map_value = get_str_or_default(request, 'map.value', None)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    if map_value:
        paths = show.map_paths_to_object(conn, map_value=map_value)
        return HttpJsonResponse({'paths': paths})
    return webclient_views.api_paths_to_object(request, **kwargs)

omeroweb.webclient.views.api_paths_to_object = api_paths_to_object


@login_required()
def api_experimenter_detail(request, experimenter_id, conn=None, **kwargs):
    # Validate parameter
    try:
        experimenter_id = long(experimenter_id)
        group_id = get_long_or_default(request, 'group', -1)
    except ValueError:
        return HttpResponseBadRequest('Invalid experimenter id')

    try:
        if experimenter_id > -1:
            # Get the experimenter
            experimenter = webclient_tree.marshal_experimenter(
                conn=conn, experimenter_id=experimenter_id)
        else:
            # fake experimenter -1
            experimenter = fake_experimenter(request, default_name="Genes")

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

    mapannotations = []
    screens = []
    try:
        # Get all genes from map annotation
        if mapann_value is not None:
            screens = tree.marshal_screens(
                conn=conn,
                mapann_value=mapann_value,
                mapann_names=mapann_names,
                group_id=group_id,
                page=page,
                limit=limit)
        else:
            mapannotations = tree.marshal_mapannotations(
                conn=conn,
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

    return HttpJsonResponse({'tags': mapannotations, 'screens': screens})


@login_required()
def api_plate_list(request, conn=None, **kwargs):
    ''' Get a list of plates
    '''
    # Get parameters
    try:
        page = get_long_or_default(request, 'page', 1)
        limit = get_long_or_default(request, 'limit', settings.PAGE)
        group_id = get_long_or_default(request, 'group', -1)
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
@render_response()
def load_metadata_details(request, c_type, c_id, conn=None, share_id=None,
                          **kwargs):
    """
    This page is the right-hand panel 'general metadata', first tab only.
    Shown for Projects, Datasets, Images, Screens, Plates, Wells, Tags etc.
    The data and annotations are loaded by the manager. Display of appropriate
    data is handled by the template.
    """

    template = "mapannotations/metadata_general.html"

    context = dict()
    context['template'] = template
    context['manager'] = {'obj_type': c_type, 'obj_id': c_id}

    return context


@login_required()
def api_annotations(request, conn=None, **kwargs):

    # Get parameters
    try:
        mapann_type = get_str_or_default(request, 'type', None)
        mapann_value = get_str_or_default(request, 'map', None)
        mapann_names = get_list_or_default(request, 'name',
                                           ["Gene Symbol"])
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    if mapann_type in ('map',) and mapann_value is not None \
       and not mapann_value.isdigit():
        anns = []
        exps = []
        try:
            anns, exps = tree.load_mapannotation(
                conn=conn,
                mapann_names=mapann_names,
                mapann_value=mapann_value)
        except ApiUsageException as e:
            return HttpResponseBadRequest(e.serverStackTrace)
        except ServerError as e:
            return HttpResponseServerError(e.serverStackTrace)
        except IceException as e:
            return HttpResponseServerError(e.message)

        return HttpJsonResponse({'annotations': anns, 'experimenters': exps})
    else:
        return webclient_api_annotations(request, conn=conn, **kwargs)

omeroweb.webclient.views.api_annotations = api_annotations


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

    autocomplete = []
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
