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

import os
from setuptools import setup, find_packages


def get_requirements():
    with open('requirements.txt') as f:
        rv = f.read().splitlines()
    return rv


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


VERSION = '0.1.2'


setup(
    name="omero-mapr",
    packages=find_packages(exclude=['ez_setup']),
    version=VERSION,
    description="MAPR is a Python plugin for OMERO.web",
    long_description=read('README.rst'),
    author='The Open Microscopy Team',
    author_email='ome-devel@lists.openmicroscopy.org.uk',
    license='AGPLv3',
    url="https://github.com/aleksandra-tarkowska/mapr",
    download_url='https://github.com/aleksandra-tarkowska/mapr/tarball/%s' % VERSION,  # NOQA
    install_requires=get_requirements(),
    include_package_data=True,
    zip_safe=False,
)
