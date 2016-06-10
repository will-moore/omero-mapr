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