# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz Software Solution
#    Copyright (C) 2013-Today Globalteckz (<http://www.globalteckz.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Web Extended",
    'category': 'Theme',
    'version': '1.0',
    'depends': ['web'],
    'external_dependencies': {},
   
    'data': [
        'views/web_extended_view.xml',
    ],

   'qweb': [
        'static/src/xml/logo.xml',
    ],

    'author': 'Globalteckz',
    'website': 'http://www.globalteckz.com',
    'license': 'AGPL-3',

    'application':True,
    'installable': True,
    'auto_install': True
}
