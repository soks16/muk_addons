# -*- coding: utf-8 -*-
# © Openlabs Technologies & Consulting (P) Limited
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Fleet Management Fuel',
    'version': '11.1',
    'category': 'Human Resources',
    'website': 'http://www.meengineeringexpertise.com',
    'author': 'MeEngineeringExpertise',
    'summary' : 'Vehicle, leasing, insurances, costs',
    'description' : """
Vehicle, leasing, insurances, cost
==================================
With this module, Odoo helps you managing all your vehicles, the
contracts associated to those vehicle as well as services, fuel log
entries, costs and many other features necessary to the management 
of your fleet of vehicle(s)

Main Features
-------------
* Add vehicles to your fleet
* Manage contracts for vehicles
* Reminder when a contract reach its expiration date
* Add services, fuel log entry, odometer values for all vehicles
* Show all costs associated to a vehicle or to a type of service
* Analysis graph for costs
""",
    'depends': ['base', 'mail', 'fleet', 'stock', 'account'],
    'data': [
        'data/product_data.xml',
        'data/stock_data.xml',
        'data/email_template.xml',
        'views/fleet_views.xml',
        'views/update_res_company_view.xml',
        'views/ir_cron.xml',
    ],
    'installable': True,
    'application': True,
}
