{
    'name': 'Sales-Views-Extended',
    'category': 'miscellaneous',
    'sequence': 55,
    'author': 'Nisha Odedra',
    'summary': 'Modify Sales View for default settings',
    'website': 'www.thirdmindscs.com',
    'version': '12.0.1.0.0',
    'description': "OpenERP View Modifications",
    'depends': ['sale', 'stock_dropshipping'],
    'data': ["views/sale_view.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
