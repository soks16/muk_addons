# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from lxml import etree

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval

class Task(models.Model):
    _inherit = "project.task"

    task_seq = fields.Char(string='Task Number', compute='get_task_seq', track_visibility='always', index=True)

    @api.multi
    def get_task_seq(self):
        for result in self:
            result.task_seq = "HS-"+str(result.id)

    def _message_post_after_hook(self, message):
        res = super(Task, self)._message_post_after_hook(message)
        subject = message.subject
        message.subject = 'Re: ' + self.task_seq + '('+self.name+')'
        return super(Task, self)._message_post_after_hook(message)