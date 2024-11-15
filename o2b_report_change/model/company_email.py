# -*- coding: utf-8 -*-
from odoo import api, fields, models

class Company(models.Model):
    _inherit = "res.company"

    quotes_email = fields.Char(string='Quotes Email')
    so_invoice_email = fields.Char(string='SO and Invoice Email')
    purchase_email = fields.Char(string="Purchase Email")
