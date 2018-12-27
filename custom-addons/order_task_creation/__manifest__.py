# -*- coding: utf-8 -*-

{
    "name": "Order Task creation",
    "version": "12.0.1.0.0",
    "category": "Project Management",
    "sequence": 101,
    "website": "http://www.openerp.com",
    "summary": "Project task creation",
    "description": "This module is developed for project task creation",
    "author": "GlobalTeckz, Nisha Odedra",
    "website": "http://www.globalteckz.com",
    "images": [],
    "depends": ["sale", "project"],
    "data": [
            "security/ir.model.access.csv",
            "wizard/create_task_view.xml",
            "views/sale_view.xml",
            "views/project_view.xml",
            "views/miscellaneous_view.xml",
            "views/order_task.xml",
    ],
    "demo": [],
    "test": [],
    "installable": True,
    "auto_install": False,
    "css": [],
    "qweb": [],
    "application": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
