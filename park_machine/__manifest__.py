# -*- coding: utf-8 -*-
{
    'name': "Park Machine",

    'summary': """
        Monitor your installations and interventions with park machine module
    """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Yziact",
    'maintainer': 'VR',
    'website': "http://gitlab.yziact.net/odoo/commons/module",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'helpdesk',
        'hr_timesheet',
        'project',
        'stock',
        'industry_fsm',
        'sale',
    ],

    # always loaded
    'data': [
        'views/park_machine.xml',
        'views/res_partner.xml',
        'views/product_category.xml',
        'views/product.xml',
        # 'security/ir.model.access.csv',
    ],
}
