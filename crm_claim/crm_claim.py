# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields
import odoo.addons.decimal_precision as dp
import datetime
from odoo.exceptions import Warning
from odoo.addons.base import res
class crm_claim_stage(models.Model):
    """ Model for claim stages. This models the main stages of a claim
        management flow. Main CRM objects (leads, opportunities, project
        issues, ...) will now use only stages, instead of state and stages.
        Stages are for example used to display the kanban view of records.
    """
    _name = "crm.claim.stage"
    _description = "Claim stages"
    _order = "sequence"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', help="Used to order stages. Lower is better.",default=1)
    team_ids = fields.Many2many('crm.team', 'crm_team_claim_stage_rel', 'stage_id', 'team_id', string='Teams', help="Link between stages and sales teams. When set, this limitate the current stage to the selected sales teams.")
    case_default = fields.Boolean('Common to All Teams', help="If you check this field, this stage will be proposed by default on each sales team. It will not assign this stage to existing teams.")


class crm_claim(models.Model):
    """ Crm claim
    """
    _name = "crm.claim"
    _description = "Claim"
    _order = "priority,date desc"
    _inherit = ['mail.thread']

    # def _get_default_stage_id(self, cr, uid, context=None):
    #     """ Gives default stage_id """
    #     team_id = self.pool['crm.team']._get_default_team_id(cr, uid, context=context)
    #     return self.stage_find(cr, uid, [], team_id, [('sequence', '=', '1')], context=context)

    name = fields.Char('Claim Subject', required=True)
    active = fields.Boolean('Active')
    action_next = fields.Char('Next Action')
    date_action_next = fields.Datetime('Next Action Date')
    description = fields.Text('Description')
    resolution = fields.Text('Resolution')
    create_date = fields.Datetime('Creation Date' , readonly=True)
    write_date = fields.Datetime('Update Date' , readonly=True)
    date_deadline = fields.Date('Deadline')
    date_closed = fields.Datetime('Closed', readonly=True)
    date = fields.Datetime('Claim Date', select=True)
    ref = fields.Char('Reference' )#selection=res.res_request.referenceable_models
    categ_id = fields.Many2one('crm.claim.category', 'Category')
    priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority')
    type_action = fields.Selection([('correction','Corrective Action'),('prevention','Preventive Action')], 'Action Type')
    user_id = fields.Many2one('res.users', 'Responsible', track_visibility='always')
    user_fault = fields.Char('Trouble Responsible')
    team_id = fields.Many2one('crm.team', 'Sales Team', oldname='section_id',\
                        select=True, help="Responsible sales team."\
                                " Define Responsible user and Email account for"\
                                " mail gateway.")
    company_id = fields.Many2one('res.company', 'Company')
    partner_id = fields.Many2one('res.partner', 'Partner')
    email_cc = fields.Text('Watchers Emails', size=252, help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma")
    email_from = fields.Char('Email', size=128, help="Destination email for email gateway.")
    partner_phone = fields.Char('Phone')
    stage_id = fields.Many2one ('crm.claim.stage', 'Stage', track_visibility='onchange',
                domain="['|', ('team_ids', '=', team_id), ('case_default', '=', True)]")
    cause = fields.Text('Root Cause')

    # _defaults = {
    #     'user_id': lambda s, cr, uid, c: uid,
    #     'team_id': lambda s, cr, uid, c: s.pool['crm.team']._get_default_team_id(cr, uid, context=c),
    #     'date': fields.datetime.now,
    #     'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'crm.case', context=c),
    #     'priority': '1',
    #     'active': lambda *a: 1,
    #     'stage_id': lambda s, cr, uid, c: s._get_default_stage_id(cr, uid, c)
    # }

    # def stage_find(self, cr, uid, cases, team_id, domain=[], order='sequence', context=None):
    #     """ Override of the base.stage method
    #         Parameter of the stage search taken from the lead:
    #         - team_id: if set, stages must belong to this team or
    #           be a default case
    #     """
    #     if isinstance(cases, (int, long)):
    #         cases = self.browse(cr, uid, cases, context=context)
    #     # collect all team_ids
    #     team_ids = []
    #     if team_id:
    #         team_ids.append(team_id)
    #     for claim in cases:
    #         if claim.team_id:
    #             team_ids.append(claim.team_id.id)
    #     # OR all team_ids and OR with case_default
    #     search_domain = []
    #     if team_ids:
    #         search_domain += [('|')] * len(team_ids)
    #         for team_id in team_ids:
    #             search_domain.append(('team_ids', '=', team_id))
    #     search_domain.append(('case_default', '=', True))
    #     # AND with the domain in parameter
    #     search_domain += list(domain)
    #     # perform search, return the first found
    #     stage_ids = self.pool.get('crm.claim.stage').search(cr, uid, search_domain, order=order, context=context)
    #     if stage_ids:
    #         return stage_ids[0]
    #     return False

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """This function returns value of partner address based on partner
           :param email: ignored
        """
        if self.partner_id:
            self.email_from= self.partner_id.email
            self.partner_phone = self.partner_id.phone
        if not self.partner_id:
            self.email_from= False
            self.partner_phone = False
        


    # def create(self, cr, uid, vals, context=None):
    #     context = dict(context or {})
    #     if vals.get('team_id') and not context.get('default_team_id'):
    #         context['default_team_id'] = vals.get('team_id')

    #     # context: no_log, because subtype already handle this
    #     return super(crm_claim, self).create(cr, uid, vals, context=context)

    # def copy(self, cr, uid, id, default=None, context=None):
    #     claim = self.browse(cr, uid, id, context=context)
    #     default = dict(default or {},
    #         stage_id = self._get_default_stage_id(cr, uid, context=context),
    #         name = _('%s (copy)') % claim.name)
    #     return super(crm_claim, self).copy(cr, uid, id, default, context=context)

    # -------------------------------------------------------
    # Mail gateway
    # -------------------------------------------------------

    # def message_new(self, cr, uid, msg, custom_values=None, context=None):
    #     """ Overrides mail_thread message_new that is called by the mailgateway
    #         through message_process.
    #         This override updates the document according to the email.
    #     """
    #     if custom_values is None:
    #         custom_values = {}
    #     desc = html2plaintext(msg.get('body')) if msg.get('body') else ''
    #     defaults = {
    #         'name': msg.get('subject') or _("No Subject"),
    #         'description': desc,
    #         'email_from': msg.get('from'),
    #         'email_cc': msg.get('cc'),
    #         'partner_id': msg.get('author_id', False),
    #     }
    #     if msg.get('priority'):
    #         defaults['priority'] = msg.get('priority')
    #     defaults.update(custom_values)
    #     return super(crm_claim, self).message_new(cr, uid, msg, custom_values=defaults, context=context)

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def _claim_count(self):
        claims_data = self.env['crm.claim'].read_group([('partner_id', 'in', self.ids)], ['partner_id'], ['partner_id'])
        result = dict((data['partner'][0], data['partner_id_count']) for data in claims_data)
        for partner in self:
            partner.claim_count = result.get(project.id, 0)

        # Claim = self.pool['crm.claim']
        # return {
        #     partner_id.id: Claim.search_count(cr,uid, ['|', ('partner_id', 'in', partner_id.child_ids.ids), ('partner_id', '=', partner_id.id)], context=context)
        #     for partner_id in self.pool['res.partner'].browse(cr, uid, ids, context=context)
        # }

    claim_count = fields.Integer(compute='_claim_count', string='# Claims', type='integer')

class crm_claim_category(models.Model):
    _name = "crm.claim.category"
    _description = "Category of claim"

    name = fields.Char('Name', required=True, translate=True)
    team_id = fields.Many2one('crm.team', 'Sales Team')

