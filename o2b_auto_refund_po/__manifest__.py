# © 2018 O2b Technologies Pvt. Ltd. (info@o2b.co.in)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Auto Refund Bill/Purchase Order',
    'version': '11.0.1.0.0',
    'author': 'O2b Technologies',
    'contributors': [
        'O2b Technologies <info@o2btechnologies.com>'
    ],
    'category': 'Utility',
    'website': 'https://www.o2btechnologies.com',
    'license': 'GPL-3 or any later version',
    'summary': 'Auto Refund Bill/Purchase Order',
    'depends': [
        'stock','account','purchase'
    ],
    'data': [
        'views/invoice_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}