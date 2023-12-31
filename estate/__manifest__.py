# -*- coding: utf-8 -*-
{
    'name': "Estate",

    'summary': """
        Estate""",

    'description': """
        Estate
    """,

    'author': "Netlinks Ltd",
    'website': "https://www.netlinks.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/security.xml',    
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/estate_property_views.xml',
        'views/users_view.xml',
        'wizards/accept_reason_view.xml',
    ],
    # only loaded in demonstration mode

}
