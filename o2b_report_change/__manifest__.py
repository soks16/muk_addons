# -*- coding: utf-8 -*-
{
    'name': 'O2b Report Changes',
    'category': 'report',
    "author": "O2btechnologies",
    'website':'https://www.o2btechnologies.com',
    'description': """Change Report Formate""",
    'depends': ['web','sale','account','base','stock','purchase'],
    'data': [
             'views/header.xml',
             'views/sale.xml',
             'views/sale_view.xml',
             'views/company_email.xml',
             'views/invoice.xml',
             'views/stock_picking_view.xml',
             'views/purchase_quote.xml',
             'views/purchase_order.xml',
             'views/delivery_slip.xml',
             'views/picking_slip.xml',
        
    ],
    'installable': True,
}
