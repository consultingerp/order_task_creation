{
    'name': 'Sales CRM -Extended',
    'category': 'Sales/CRM',
    'sequence': 55,
    'summary': 'Reference for Opportunity on Quotation',
    'website': 'www.thirdmindscs.com',
    'version': '1.0',
    'description': """
This module will added opportunity refernce to the quotation, also 
allowed to add reference into the quotation for the related opportunity.
==================

        """,
    'depends': ['sale','crm', 'sale_crm'],
    'data': ["views/sale_view.xml",
        
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
