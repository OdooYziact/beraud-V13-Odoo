# -*- coding: utf-8 -*-
{
    'name': "Invoicing time spent between companies",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Yziact",
    'maintainer': 'VRA',
    'website': "http://gitlab.yziact.net/odoo/commons/module",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'purchase',
        'sale',
        'product',
    ],

    # always loaded
    'data': [
        # 'views/product_product.xml',
        # 'security/ir.model.access.csv',
    ],
}
