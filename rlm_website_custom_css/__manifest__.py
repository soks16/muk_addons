# -*- coding: utf-8 -*-
{
    'name': "RLM Website Custom CSS",

    'summary': """
        Custom CSS Module""",

    'description': """
        Custom CSS Module 
    """,

    'author': "russ@redlabmedia.com",
    'website': "http://www.redlabmedia.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.6',

    # any module necessary for this one to work correctly
    'depends': ['web','web_editor','website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/rlm_website_custom_css.xml',
        'views/templates.xml',
        'views/snippets.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
