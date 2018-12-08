# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz
#    Copyright (C) 2013-today Globalteckz (<http://www.globalteckz.com>).
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
    'name': 'Order Task creation',
    'version': '1.1',
    'author': 'Globalteckz',
    'category': 'Project Management',
    'sequence': 101,
    'website': 'http://www.openerp.com',
    'summary': 'Project task creation',
    'description': """
This module is developed for project task creation
    """,
    'author': 'GlobalTeckz',
    'website': 'http://www.globalteckz.com',
    'images': [],
    'depends': ['base','sale','project','project_timesheet'],


    'data': ['security/ir.model.access.csv', 
             'wizard/create_task_view.xml',
             'sale_view.xml',
             'project_view.xml',
             'miscellaneous_view.xml',
             'order_task.xml',
            
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'css': [],
    'qweb': [
       
    ],
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
