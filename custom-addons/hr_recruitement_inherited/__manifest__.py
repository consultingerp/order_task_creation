# -*- coding: utf-8 -*-

{
    'name': ('Applicant Form Submission'),
    'version': '12.0.1.0.0',
    'author': "ThirdmindCS, Nisha Odedra",
    'category': 'Hidden',
    'license': 'AGPL-3',
    'depends': [
        'website_hr_recruitment', 'hr_recruitment'
    ],
    'description': "Modify the Job Application form view for additional field "
                   "Expected Salary",
    'website': 'http://www.thirdmindscs.com',
    'data': ['views/applicant_view.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
