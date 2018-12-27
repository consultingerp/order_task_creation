# -*- coding: utf-8 -*-

{
    "name" : "Refinement New",
    "version" : "12.0.1.0.0",
    "depends" : [
        "sale",
        "sale_margin",
        "sale_stock",
        "account",
        "hr"
    ],
    "author" : "ThirdmindCS, Nisha Odedra",
    "description": "Refinment module to cover all additional content in "
                   "products and to provide billing / quotes with additional "
                   "refinement products ",
    "website" : "www.thirdmindcs.com",
    "images": [

    ],
    "category" : "Sales Management",
    "summary": "Source Gesellschaft für verkaufsfördernde Produkte mbH",
    "demo" : [],
    "data" : [  
        "security/refinement_security.xml",
        "security/ir.model.access.csv",
        "report/report_sale_order.xml",
        "report/report_confirm_order.xml",
        "report/report_invoice_layout.xml",
        "views/refinement_view.xml",
        "views/product_product_view.xml",
        "views/sale_view.xml",
        "views/mail_report_sale_layout.xml",
        "views/invoice_view.xml",
                
    ],
    "auto_install": False,
    "installable": True,
    "application": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
