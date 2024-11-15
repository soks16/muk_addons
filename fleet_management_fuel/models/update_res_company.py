# -*- coding = utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing det

from odoo import fields, models, api, tools, _
from odoo.addons import decimal_precision as dp
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

# import os
# import re


class Company(models.Model):
    _inherit = "res.company"

    next_km = fields.Float("Prochain vidange à", help="Prochain vidange à", default=10000.00)
    notif_km = fields.Float("Notif prochaine vidange à", help="Notification de la prochaine vidange à", default=1000.00)
    jr_notif = fields.Float("Nbr. jour avant Notif ", help="Nbr. de jours avant la Notification", default=15.00)

