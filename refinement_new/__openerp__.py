# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz Solutions
#    Copyright (C) 2013-Today <http://www.globalteckz.com>).
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
    "name" : "Refinement New",
    "version" : "1.1",
    "depends" : ['base', 'sale','sale_margin','sale_stock','account','sale_quotation_builder', 'sale_management'],
    "author" : "ThirdmindCS",
    "description": """Refinment module to cover all additional content in products and to provide billing / quotes with additional refinement products """,
    "website" : "www.thirdmindcs.com",
    'images': [

    ],
    "category" : "Sales Management",
    'summary': 'Source Gesellschaft für verkaufsfördernde Produkte mbH',
    "demo" : [],
    "data" : [  'security/refinement_security.xml',
                'security/ir.model.access.csv',
                'report/report_invoice_layout.xml',
                'report/report_sale_order.xml',
                'report/report_confirm_order.xml',
                'views/refinement_view.xml',
                'views/product_product_view.xml',
                'views/sale_view.xml',
                'views/mail_report_sale_layout.xml',
                'views/invoice_view.xml',
                #'views/delivery_item_view.xml',
                #'data/delivery_item_data.xml',
                
    ],
    'auto_install': False,
    "installable": True,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

