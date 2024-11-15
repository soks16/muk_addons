# -*- coding: utf-8 -*-
{
    'name': "rlm_x1",

    'summary': """
        Red Lab Media Website Extension 1""",

    'description': """
        Red Lab Media Odoo Website Extension. Containing custom LESS, Snippets, etc. 
    """,

    'author': "Russ Schneider",
    'website': "http://www.redlabmedia.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.4.8',

    # any module necessary for this one to work correctly
    'depends': ['web','web_editor','website','portal'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'views/snippets.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
