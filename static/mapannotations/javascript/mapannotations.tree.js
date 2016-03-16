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

//   Here we override jstree setup and configure


// jQuery load callback...

$(function () {

    // TODO: make a function and add button
    $.jstree.reference('#dataTree').settings.sort = function(nodeId1, nodeId2) {
        return;
        // map annotiation values are sorted in query //
        //var inst = this;
        //var node1 = inst.get_node(nodeId1);
        //var node2 = inst.get_node(nodeId2);
        //var name1 = node1.text.toLowerCase();
        //var name2 = node2.text.toLowerCase();

        //// If the nodes are the same type then just compare lexicographically
        //if (node1.type === node2.type && node1.text && node2.text) {
        //    // Unless they are experimenters and one of them is the current user.
        //    if(node1.type === 'experimenter') {
        //        if (node1.data.obj.id === WEBCLIENT.USER.id) {
        //            return -1;
        //        } else if (node2.data.obj.id === WEBCLIENT.USER.id) {
        //            return 1;
        //        }
        //    }
        //    // Unless they are tags.
        //    if (node1.data.obj.childCount > 0 && node2.data.obj.childCount > 0) {
        //        return node1.data.obj.childCount >= node2.data.obj.childCount ? -1 : 1;
        //    } else if (name1 === name2) {
        //        // If names are same, sort by ID
        //        return node1.data.obj.id <= node2.data.obj.id ? -1 : 1;
        //    }
        //    return name1 <= name2 ? -1 : 1;
        //} else {
        //    return node1.data.obj.id <= node2.data.obj.id ? -1 : 1;
        //}
    };

    $.jstree.reference('#dataTree').settings.types['experimenter'] = {
        'icon' : WEBCLIENT.URLS.static_webclient + 'image/icon_user.png',
        'valid_children': ['tag']
    };
    $.jstree.reference('#dataTree').settings.types['tag']['icon'] = MAPANNOTATIONS.URLS.static_webclient + 'image/gene_icon36x36.png';

    $.jstree.reference('#dataTree').settings.types['plate'] = {
        'icon': WEBCLIENT.URLS.static_webclient + 'image/folder_plate16.png',
        'valid_children': ['image']
    };
});