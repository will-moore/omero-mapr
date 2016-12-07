//   Copyright (C) 2016 University of Dundee & Open Microscopy Environment.
//   All rights reserved.

//   This program is free software: you can redistribute it and/or modify
//   it under the terms of the GNU Affero General Public License as
//   published by the Free Software Foundation, either version 3 of the
//   License, or (at your option) any later version.

//   This program is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//   GNU Affero General Public License for more details.

//   You should have received a copy of the GNU Affero General Public License
//   along with this program.  If not, see <http://www.gnu.org/licenses/>.

//   Author: Aleksandra Tarkowska <A(dot)Tarkowska(at)dundee(dot)ac(dot)uk>,

//   Version: 1.0

//   Here we override ui.autocomplete


$(function () {

    $("label").inFieldLabels();

    var jstreeInst = $.jstree.reference('#dataTree');
    var oldData = jstreeInst.settings.core.data;
    
    $("#id_autocomplete").autocomplete({
        autoFocus: false,
        delay: 1000,
        source: function( request, response ) {
            $.ajax({
                dataType: "json",
                type : 'GET',
                url: MAPANNOTATIONS.URLS.autocomplete,
                data: {
                    value: request.term.toLowerCase(),
                    query: true,
                    experimenter_id: WEBCLIENT.active_user,
                    group: WEBCLIENT.active_group_id
                },
                success: function(data) {
                    if (data.length > 0) {
                        response( $.map( data, function(item) {
                            return item;
                        }));
                    } else {
                       response([{ label: 'No results found.', value: -1 }]);
                   }
                },
                error: function(data) {
                    response([{ label: 'Error occured.', value: -1 }]);
                }
            });
        },
        minLength: 1,
        open: function() {},
        close: function() {},
        focus: function(event,ui) {},
        select: function(event, ui) {
            if (ui.item.value == -1) {
                return false;
            }
            // keep selected value in input
            $( "#id_autocomplete" ).val("");
            jstreeInst.deselect_all();
            jstreeInst.close_all();
            OME.clearThumbnailsPanel();
            WEBCLIENT.URLS.api_experimenter = MAPANNOTATIONS.URLS.autocomplete_default
            jstreeInst.settings.core.data = function(node, callback, payload) {
                oldData.apply(jstreeInst, [node, callback, {'value': ui.item.value}]);
            };
            jstreeInst.refresh();
            return false;
        }
    }).data("ui-autocomplete")._renderItem = function( ul, item ) {
        return $( "<li>" )
            .append( "<a>" + item.label + "</a>" )
            .appendTo( ul );
    }

    $("#search_hints").tooltip({
        track: true,
        show: false,
        hide: false,
        items: '[data-content]',
        content: function() {
            return $(this).data('content');
        },
    });

});
