# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models


class SalaryRuleInput(models.Model):
    _inherit = 'hr.payslip'

    def get_inputs(self, contract_ids, date_from, date_to):
        """This Compute the other inputs to employee payslip.
                           """
        res = super(SalaryRuleInput, self).get_inputs(contract_ids, date_from, date_to)
        # print self, contract_ids, date_from, date_to
        contract_obj = self.env['hr.contract']
        emp_id = contract_obj.browse(contract_ids[0]).employee_id
        adv_salary = self.env['salary.advance'].search([('employee_id', '=', emp_id.id)])
        #print emp_id, adv_salary
        for adv_obj in adv_salary:
            current_date = datetime.strptime(date_from, '%Y-%m-%d').date().month
            date = adv_obj.date
            existing_date = datetime.strptime(date, '%Y-%m-%d').date().month
            if current_date == existing_date:
                state = adv_obj.state
                amount = adv_obj.advance
                for result in res:
                    if state == 'approve' and amount != 0 and result.get('code') == 'SAR':
                        result['amount'] = amount
        return res
