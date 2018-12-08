{
    'name': 'Sales-Views-Extended',
    'category': 'miscellaneous',
    'sequence': 55,
    'summary': 'Modify Sales View for default settings',
    'website': 'www.thirdmindscs.com',
    'version': '1.0',
    'description': """
OpenERP View Modifications
==================

        """,
    'depends': ['sale','stock_dropshipping'],
    'data': ["views/sale_view.xml",
        
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
