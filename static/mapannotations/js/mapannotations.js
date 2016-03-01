
// Copyright (c) 2015 University of Dundee.

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

// jQuery load callback...
$(function() {

    // 
    var WEBSTATIC = JSTREEDEMO.WEBCLIENT_STATIC,
        WEBINDEX = JSTREEDEMO.WEBINDEX,
        MAPINDEX = JSTREEDEMO.MAPINDEX,
        EXPID = activeUserId();

    // Select jstree and then cascade handle events and setup the tree.
    var jstree = $("#dataTree")

    .on("click.jstree", ".jstree-anchor", function (e) {
        e.preventDefault();
        var datatree = $.jstree.reference($('#dataTree'));
        // Expand on click (not select because of key navigation)
        if (datatree.is_parent(this)) {
            datatree.open_node(this);
        }
    })

    // Support ?show=tag-123
    // NB: we only support a single level of tree traversal (not recursive as on containers.html)
    .on('loaded.jstree', function(e, data) {
        var inst = data.instance;
        var param = OME.getURLParameter('show');
        if (!param) {
            // If not found, just select root node
            inst.select_node('ul > li:first');
        } else {
            // Tree root may be experimenter or 'All members' (this supports both)
            var root = inst.get_node('ul > li:first');
            inst.open_node(root, function() {
                var node = inst.locate_node(param, root)[0];
                if (!node) return;
                inst.select_node(node);
                inst.open_node(node);
                // we also focus the node, to scroll to it and setup hotkey events
                $("#" + node.id).children('.jstree-anchor').focus();
            });
        }
    })

    // Setup jstree
    .jstree({

        'plugins': [
            'types',
            'childcount'    // uses webclient/javascript/jquery.jstree.childcount_plugin.js
        ],

        'core' : {
            'themes': {
                'dots': false,
                'variant': 'ome'
            },
            'force_text': true,
            // Make use of function for 'data' because there are some scenarios in which
            // an ajax call is not used to get the data. Namely, the all-user view
            'data' : function(node, callback) {

                // Dictionary for adding query parameters to url
                var payload = {};

                // try to get the ID of the node we're loading data for
                if (node.hasOwnProperty('data') && node.type != 'experimenter') {
                    if (node.data.hasOwnProperty('obj')) {
                        payload.id = node.data.obj.id;
                    }
                }

                // Configure URL for request
                // Get the type of the node being expanded
                // Figure out what type of children it should have
                // Request the list of children from that url, adding any relevant filters
                var url;
                if (node.type === 'experimenter') {
                    url = MAPINDEX + 'api/mapannotations/';
                } else if (node.type === 'mapannotation') {
                    url = MAPINDEX + 'api/screens/';
                } else if (node.type === 'screen') {
                    url = WEBINDEX + 'api/plates/';
                } else if (node.type === 'plate') {
                    url = WEBINDEX + 'api/plate_acquisitions/';
                } else if (node.id === '#') {
                    // root of tree
                    if (EXPID && EXPID != -1) {
                        url = WEBINDEX + 'api/experimenters/' + EXPID + '/';
                    } else {
                        // ...or multiple experimenters
                        node = {
                            'data': {'id': -1, 'obj': {'id': -1}},
                            'text': 'Genes',
                            'children': true,
                            'type': 'experimenter',
                            'state': {
                                'opened': true
                            },
                            'li_attr': {
                                'data-id': -1
                            }
                        };

                        callback.call(this, [node]);
                        return;
                    }
                } else {
                    return;
                }

                // Load the data via AJAX...
                $.ajax({
                    url: url,
                    data: payload,
                    cache: false,
                    success: function (data, textStatus, jqXHR) {
                        callback.call(this, data);
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        // Global error handling is sufficient here
                    },
                    // Converter is required because the JSON format being returned is not
                    // jstree specific.
                    'converters' : {
                        "text json": function (json) {
                            var data = JSON.parse(json);
                            var jstree_data = [];
                            var node;

                            if (data.hasOwnProperty('experimenter')) {
                                var value = data.experimenter;
                                node = {
                                    'data': {'id': value.id, 'obj': value},
                                    'text': value.firstName + ' ' + value.lastName,
                                    'children': true,
                                    'type': 'experimenter',
                                    'state': {
                                        'opened': true
                                    },
                                    'li_attr': {
                                        'data-id': value.id
                                    }
                                };

                                jstree_data.push(node);
                            }

                            // Add nodes to the jstree data structure
                            if (data.hasOwnProperty('mapannotations')) {
                                $.each(data.mapannotations, function(index, value) {
                                    var node = {
                                        'data': {'id': value.id, 'obj': value},
                                        'text': value.name,
                                        'children': value.childCount > 0 ? true : false,
                                        'type': 'mapannotation',
                                        'li_attr': {
                                            'data-id': value.id
                                        }
                                    };
                                    jstree_data.push(node);
                                });
                            }

                            // Add screens to the jstree data structure
                            if (data.hasOwnProperty('screens')) {
                                $.each(data.screens, function(index, value) {
                                     var node = {
                                        'data': {'id': value.id, 'obj': value},
                                        'text': value.name,
                                        'children': value.childCount > 0 ? true : false,
                                        'type': 'screen',
                                        'li_attr': {
                                            'data-id': value.id
                                        }
                                     };
                                     jstree_data.push(node);
                                });
                            }

                            // Add plates to the jstree data structure
                            if (data.hasOwnProperty('plates')) {
                                $.each(data.plates, function(index, value) {
                                     var node = {
                                        'data': {'id': value.id, 'obj': value},
                                        'text': value.name,
                                        'children': value.childCount > 0 ? true : false,
                                        'type': 'plate',
                                        'li_attr': {
                                            'data-id': value.id
                                        }
                                     };
                                     jstree_data.push(node);
                                });
                            }

                            // Add plates to the jstree data structure
                            if (data.hasOwnProperty('acquisitions')) {
                                $.each(data.acquisitions, function(index, value) {
                                     var node = {
                                        'data': {'id': value.id, 'obj': value},
                                        'text': value.name,
                                        'children': false,
                                        'type': 'acquisition',
                                        'li_attr': {
                                            'data-id': value.id
                                        }
                                     };
                                     jstree_data.push(node);
                                });
                            }

                            return jstree_data;
                        }
                    }
                });
            }
        },

        'types' : {
            '#' : {
                'valid_children': ['experimenter']
            },
            'default': {
                'draggable': false
            },
            'experimenter': {
                'icon' : WEBSTATIC + 'image/icon_user.png',
                'valid_children': ['mapannotation']
            },
            'mapannotation': {
                'icon': WEBSTATIC + 'image/left_sidebar_icon_tag.png',
                'valid_children': ['screen']
            },
            'screen': {
                'icon': WEBSTATIC + 'image/folder_screen16.png',
                'valid_children': ['plate']
            },
            'plate': {
                'icon': WEBSTATIC + 'image/folder_plate16.png',
                'valid_children': ['acquisition']
            },
            'acquisition': {
                'icon': WEBSTATIC + 'image/image16.png',
            }
        }
    });
});


