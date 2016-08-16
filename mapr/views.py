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
from mapr_settings import mapr_settings

from django.core.urlresolvers import reverse
from django.http import HttpResponseServerError, HttpResponseBadRequest, \
    HttpResponseRedirect

from show import mapr_paths_to_object
from show import MapShow as Show
import tree as mapr_tree

from omeroweb.http import HttpJsonResponse
from omeroweb.webclient.decorators import login_required, render_response
from omeroweb.webclient.views import get_long_or_default, get_bool_or_default
from omeroweb.webclient.views import switch_active_group
from omeroweb.webclient.forms import GlobalSearchForm, ContainerForm
from omeroweb.webclient.show import IncorrectMenuError

from omeroweb.webclient import tree as webclient_tree

from omeroweb.webclient.views import api_paths_to_object \
    as webclient_api_paths_to_object

import omeroweb


logger = logging.getLogger(__name__)


# Helpers
def fake_experimenter(label):
    """
    Marshal faked experimenter when id is -1
    Load omero.client.ui.menu.dropdown.everyone.label as username
    """
    return {
        'id': -1,
        'omeName': label,
        'firstName': label,
        'lastName': ''
    }


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


def _get_ns(mapr_settings, menu):
    ns = []
    try:
        ns = mapr_settings.MENU_MAPR[menu]['ns']
    except:
        pass
    return ns


def _get_keys(mapr_settings, menu):
    keys = None
    try:
        keys = mapr_settings.MENU_MAPR[menu]['all']
    except:
        pass
    return keys


@login_required()
@render_response()
def index(request, menu, value=None, conn=None, url=None, **kwargs):
    """
    This view handles most of the top-level pages, as specified by 'menu' E.g.
    userdata, usertags, history, search etc.
    Query string 'path' that specifies an object to display in the data tree
    is parsed.
    We also prepare the list of users in the current group, for the
    switch-user form. Change-group form is also prepared.
    """
    request.session.modified = True
    template = "mapr/base_mapr.html"

    # tree support
    show = Show(conn=conn, request=request, menu=menu, value=value)

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
    url = reverse(viewname="maprindex_%s" % menu)

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
        'menu_default': ", ".join(mapr_settings.MENU_MAPR[menu]['default']),
        'menu_all': ", ".join(mapr_settings.MENU_MAPR[menu]['all']),
        'init': init,
        'myGroups': myGroups,
        'new_container_form': new_container_form,
        'global_search_form': global_search_form
    }
    context['groups'] = groups
    context['active_group'] = conn.getObject(
        "ExperimenterGroup", long(active_group))
    context['active_user'] = \
        conn.getObject("Experimenter", long(user_id)) or {'id': -1}
    context['initially_select'] = show.initially_select
    context['isLeader'] = conn.isLeader()
    context['current_url'] = url
    context['page_size'] = settings.PAGE
    context['template'] = template
    context['map_value'] = value

    return context


@login_required()
def api_paths_to_object(request, menu=None, value=None, conn=None, **kwargs):
    """
    This override omeroweb.webclient.api_paths_to_object
    to support custom path to map.value
    """

    mapann_ns = _get_ns(mapr_settings, menu)
    keys = _get_keys(mapr_settings, menu)

    try:
        mapann_value = get_str_or_default(request, 'map.value', None)
        mapann_names = get_list_or_default(request, 'name', keys)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    if menu in mapr_settings.MENU_MAPR:

        try:
            experimenter_id = get_long_or_default(request, 'experimenter',
                                                  None)
            # project_id = get_long_or_default(request, 'project', None)
            # dataset_id = get_long_or_default(request, 'dataset', None)
            image_id = get_long_or_default(request, 'image', None)
            screen_id = get_long_or_default(request, 'screen', None)
            plate_id = get_long_or_default(request, 'plate', None)
            acquisition_id = get_long_or_default(request, 'run', None)
            # acquisition will override 'run' if both are specified as they are
            # the same thing
            acquisition_id = get_long_or_default(request, 'acquisition',
                                                 acquisition_id)
            # well_id = request.GET.get('well', None)
            group_id = get_long_or_default(request, 'group', None)
        except ValueError:
            return HttpResponseBadRequest('Invalid parameter value')

        paths = mapr_paths_to_object(
            conn=conn, mapann_ns=mapann_ns, mapann_query=value,
            mapann_value=mapann_value, mapann_names=mapann_names,
            screen_id=screen_id, plate_id=plate_id, image_id=image_id,
            experimenter_id=experimenter_id, group_id=group_id)

        return HttpJsonResponse({'paths': paths})
    return webclient_api_paths_to_object(request, conn=conn, **kwargs)

omeroweb.webclient.views.api_paths_to_object = api_paths_to_object


@login_required()
def api_experimenter_list(request, menu,
                          value=None, conn=None, **kwargs):

    mapann_ns = _get_ns(mapr_settings, menu)
    keys = _get_keys(mapr_settings, menu)

    # Get parameters
    try:
        # page = get_long_or_default(request, 'page', 1)
        # limit = get_long_or_default(request, 'limit', settings.PAGE)
        group_id = get_long_or_default(request, 'group', -1)
        experimenter_id = get_long_or_default(request, 'experimenter', -1)
        mapann_value = value or get_str_or_default(request, 'value', None) \
            or get_str_or_default(request, 'id', None)
        mapann_names = get_list_or_default(request, 'name', keys)
        mapann_query = get_str_or_default(request, 'query', None)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    try:
        if experimenter_id > -1:
            # Get the experimenter
            experimenter = webclient_tree.marshal_experimenter(
                conn=conn, experimenter_id=experimenter_id)
        else:
            # fake experimenter -1
            experimenter = fake_experimenter(
                mapr_settings.MENU_MAPR[menu]['label'])

        if mapann_value is not None or mapann_query is not None:
            if mapann_query:
                experimenter['extra'] = {'query': mapann_query}
            if mapann_value:
                experimenter['extra'] = {'value': mapann_value}
            # count children
            experimenter['childCount'] = mapr_tree.count_mapannotations(
                conn=conn,
                mapann_ns=mapann_ns,
                mapann_names=mapann_names,
                mapann_value=mapann_value,
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
def api_mapannotation_list(request, menu, conn=None, **kwargs):

    mapann_ns = _get_ns(mapr_settings, menu)
    keys = _get_keys(mapr_settings, menu)

    # Get parameters
    try:
        page = get_long_or_default(request, 'page', 1)
        limit = get_long_or_default(request, 'limit', settings.PAGE)
        group_id = get_long_or_default(request, 'group', -1)
        experimenter_id = get_long_or_default(request, 'experimenter_id', -1)
        mapann_value = get_str_or_default(request, 'id', None) \
            or get_str_or_default(request, 'value', None)
        mapann_names = get_list_or_default(request, 'name', keys)
        mapann_query = get_str_or_default(request, 'query', None)
        orphaned = get_bool_or_default(request, 'orphaned', False)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    mapannotations = []
    screens = []
    projects = []
    try:
        # Get attributes from map annotation
        if orphaned:
            if mapann_value is not None or mapann_query is not None:
                mapannotations = mapr_tree.marshal_mapannotations(
                    conn=conn,
                    mapann_ns=mapann_ns,
                    mapann_names=mapann_names,
                    mapann_value=mapann_value,
                    mapann_query=mapann_query,
                    group_id=group_id,
                    experimenter_id=experimenter_id,
                    page=page,
                    limit=limit)
        else:
            screens = mapr_tree.marshal_screens(
                conn=conn,
                mapann_ns=mapann_ns,
                mapann_names=mapann_names,
                mapann_value=mapann_value,
                mapann_query=mapann_query,
                group_id=group_id,
                experimenter_id=experimenter_id,
                page=page,
                limit=limit)
            projects = mapr_tree.marshal_projects(
                conn=conn,
                mapann_ns=mapann_ns,
                mapann_names=mapann_names,
                mapann_value=mapann_value,
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

    return HttpJsonResponse({'maps': mapannotations,
                             'screens': screens, 'projects': projects})


@login_required()
def api_datasets_list(request, menu, conn=None, **kwargs):

    mapann_ns = _get_ns(mapr_settings, menu)
    keys = _get_keys(mapr_settings, menu)

    # Get parameters
    try:
        page = get_long_or_default(request, 'page', 1)
        limit = get_long_or_default(request, 'limit', settings.PAGE)
        group_id = get_long_or_default(request, 'group', -1)
        experimenter_id = get_long_or_default(request,
                                              'experimenter_id', -1)
        project_id = get_str_or_default(request, 'id', None)
        mapann_names = get_list_or_default(request, 'name', keys)
        mapann_value = get_str_or_default(request, 'value', None)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    datasets = []
    try:
        # Get the images
        datasets = mapr_tree.marshal_datasets(
            conn=conn,
            project_id=project_id,
            mapann_ns=mapann_ns,
            mapann_names=mapann_names,
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

    return HttpJsonResponse({'datasets': datasets})


@login_required()
def api_plate_list(request, menu, conn=None, **kwargs):

    mapann_ns = _get_ns(mapr_settings, menu)
    keys = _get_keys(mapr_settings, menu)

    # Get parameters
    try:
        page = get_long_or_default(request, 'page', 1)
        limit = get_long_or_default(request, 'limit', settings.PAGE)
        group_id = get_long_or_default(request, 'group', -1)
        experimenter_id = get_long_or_default(request,
                                              'experimenter_id', -1)
        screen_id = get_str_or_default(request, 'id', None)
        mapann_names = get_list_or_default(request, 'name', keys)
        mapann_value = get_str_or_default(request, 'value', None)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    plates = []
    try:
        # Get the images
        plates = mapr_tree.marshal_plates(
            conn=conn,
            screen_id=screen_id,
            mapann_ns=mapann_ns,
            mapann_names=mapann_names,
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
def api_image_list(request, menu, conn=None, **kwargs):

    mapann_ns = _get_ns(mapr_settings, menu)
    keys = _get_keys(mapr_settings, menu)

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
        parent = get_str_or_default(request, 'node', None)
        parent_id = get_long_or_default(request, 'id', None)
        mapann_names = get_list_or_default(request, 'name', keys)
        mapann_value = get_str_or_default(request, 'value', None)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    images = []
    try:
        # Get the images
        images = mapr_tree.marshal_images(
            conn=conn,
            parent=parent,
            parent_id=parent_id,
            mapann_ns=mapann_ns,
            mapann_names=mapann_names,
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

    template = "mapr/metadata_general.html"

    context = dict()
    context['template'] = template
    context['menu'] = c_type
    context['manager'] = {'obj_type': 'map', 'obj_id': c_id}
    context['maprindex'] = reverse(viewname=('maprindex'))
    context['maprindex_path'] = reverse(viewname=('maprindex_%s' % c_type))
    return context


@login_required()
def api_annotations(request, menu, conn=None, **kwargs):

    mapann_ns = _get_ns(mapr_settings, menu)
    keys = _get_keys(mapr_settings, menu)

    # Get parameters
    try:
        mapann_value = get_str_or_default(request, 'map', None)
        mapann_names = get_list_or_default(request, 'name', keys)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    anns = []
    exps = []
    try:
        anns, exps = mapr_tree.load_mapannotation(
            conn=conn,
            mapann_ns=mapann_ns,
            mapann_names=mapann_names,
            mapann_value=mapann_value)
    except ApiUsageException as e:
        return HttpResponseBadRequest(e.serverStackTrace)
    except ServerError as e:
        return HttpResponseServerError(e.serverStackTrace)
    except IceException as e:
        return HttpResponseServerError(e.message)

    return HttpJsonResponse({'annotations': anns, 'experimenters': exps})


@login_required()
def mapannotations_autocomplete(request, menu, conn=None, **kwargs):

    mapann_ns = _get_ns(mapr_settings, menu)
    keys = _get_keys(mapr_settings, menu)

    # Get parameters
    try:
        page = get_long_or_default(request, 'page', 1)
        limit = get_long_or_default(request, 'limit', settings.PAGE)
        group_id = get_long_or_default(request, 'group', -1)
        experimenter_id = get_long_or_default(request, 'experimenter_id', -1)
        query = get_str_or_default(request, 'query', None)
        mapann_names = get_list_or_default(request, 'name', keys)
    except ValueError:
        return HttpResponseBadRequest('Invalid parameter value')

    autocomplete = []
    try:
        autocomplete = mapr_tree.marshal_autocomplete(
            conn=conn,
            query=query,
            mapann_ns=mapann_ns,
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

    return HttpJsonResponse(autocomplete)
