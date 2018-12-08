{
    'name': 'Views-Extended',
    'category': 'miscellaneous',
    'sequence': 55,
    'summary': 'Modify multiple views in Odoo Apps',
    'website': 'https://www.odoo.com/page/e-commerce',
    'version': '1.0',
    'description': """
OpenERP View Modifications
==================

        """,
    'depends': ['base', 'website_partner', 'product','stock'],
    'data': [
        'views/partner_view.xml',
        'views/product_view.xml',
        
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
