# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp

class AccountInvoiceLine(models.Model):
    """ Override AccountInvoice_line to add the link to the purchase order line it is related to"""
    _inherit = 'account.invoice.line'

    refund_quantity = fields.Float('Refund Quantity')


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.multi
    def compute_refund(self, mode='refund'):
        inv_obj = self.env['account.invoice']
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        context = dict(self._context or {})
        xml_id = False

        for form in self:
            created_inv = []
            date = False
            description = False
            for inv in inv_obj.browse(context.get('active_ids')):
                if inv.state in ['draft', 'cancel']:
                    raise UserError(_('Cannot create credit note for the draft/cancelled invoice.'))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise UserError(_('Cannot create a credit note for the invoice which is already reconciled, invoice should be unreconciled first, then only you can add credit note for this invoice.'))

                date = form.date or False
                description = form.description or inv.name
                refund = inv.refund(form.date_invoice, date, description, inv.journal_id.id)
                # update line --------
                qty_dict = context.get('qty_dict')
                if qty_dict:
                    for rline in refund.invoice_line_ids:
                        if not qty_dict.get(rline.purchase_line_id):
                            rline.unlink()
                        elif qty_dict.get(rline.purchase_line_id):
                            rline.quantity = qty_dict.get(rline.purchase_line_id)

                    """

                    for invline in inv.invoice_line_ids:
                        if qty_dict.get(invline.product_id):
                            invline.refund_quantity = qty_dict.get(invline.product_id)
                    """
                refund.compute_taxes()

                created_inv.append(refund.id)
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_ids
                    to_reconcile_ids = {}
                    to_reconcile_lines = self.env['account.move.line']
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_lines += line
                            to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                        if line.reconciled:
                            line.remove_move_reconcile()
                    refund.action_invoice_open()
                    for tmpline in refund.move_id.line_ids:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_lines += tmpline
                    to_reconcile_lines.filtered(lambda l: l.reconciled == False).reconcile()
                    if mode == 'modify':
                        invoice = inv.read(inv_obj._get_refund_modify_read_fields())
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.browse(invoice['invoice_line_ids'])
                        invoice_lines = inv_obj.with_context(mode='modify')._refund_cleanup_lines(invoice_lines)
                        tax_lines = inv_tax_obj.browse(invoice['tax_line_ids'])
                        tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': form.date_invoice,
                            'state': 'draft',
                            'number': False,
                            'invoice_line_ids': invoice_lines,
                            'tax_line_ids': tax_lines,
                            'date': date,
                            'origin': inv.origin,
                            'fiscal_position_id': inv.fiscal_position_id.id,
                        })
                        for field in inv_obj._get_refund_common_fields():
                            if inv_obj._fields[field].type == 'many2one':
                                invoice[field] = invoice[field] and invoice[field][0]
                            else:
                                invoice[field] = invoice[field] or False
                        inv_refund = inv_obj.create(invoice)
                        if inv_refund.payment_term_id.id:
                            inv_refund._onchange_payment_term_date_invoice()
                        created_inv.append(inv_refund.id)
                xml_id = inv.type == 'out_invoice' and 'action_invoice_out_refund' or \
                         inv.type == 'out_refund' and 'action_invoice_tree1' or \
                         inv.type == 'in_invoice' and 'action_invoice_in_refund' or \
                         inv.type == 'in_refund' and 'action_invoice_tree2'
                # Put the reason in the chatter
                subject = _("Credit Note")
                body = description
                refund.message_post(body=body, subject=subject)

        if xml_id:
            result = self.env.ref('account.%s' % (xml_id)).read()[0]
            invoice_domain = safe_eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result
        return True

    @api.multi
    def invoice_refund(self):
        context = dict(self._context or {})
        data_refund = self.read(['filter_refund'])[0]['filter_refund']
        inv_obj = self.env['account.invoice']
        inv = inv_obj.browse(context.get('active_ids'))
        if inv.origin and inv.origin.startswith('PO'):
            context = {'refund_id':self.id,'invoice_id':inv.id,'data_refund':data_refund}
            wizard_id = self.env['purchase.order.refund'].create({'invoice_id':inv.id})
            invoice_line_ids = inv.invoice_line_ids.filtered(lambda r: r.quantity > 0)
            line_return_obj = self.env['invoice.return.picking.line']
            for line in invoice_line_ids.filtered(lambda r: r.purchase_line_id.qty_received > 0):
                qty = line.purchase_line_id.qty_received
                line_return_obj.create({'purchase_line_id':line.purchase_line_id.id,'product_id':line.product_id.id,'quantity':qty,'wizard_id':wizard_id.id})
            return {
                'name': 'Warning',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'purchase.order.refund',
                'context': context,
                'res_id': wizard_id.id,
                'target': 'new',
            }
        return self.compute_refund(data_refund)

class ReturnInvoiceLine(models.TransientModel):
    _name = "invoice.return.picking.line"
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Product", required=True, domain="[('id', '=', product_id)]")
    quantity = fields.Float("Quantity", digits=dp.get_precision('Product Unit of Measure'), required=True)
    wizard_id = fields.Many2one('purchase.order.refund', string="Wizard")
    purchase_line_id = fields.Many2one('purchase.order.line', string='Purchase Line')


class PurchaseOrderRefund(models.TransientModel):
    _name = "purchase.order.refund"

    invoice_id = fields.Many2one('account.invoice', string='Invoice')
    product_return_lines = fields.One2many('invoice.return.picking.line', 'wizard_id', 'Moves')

    @api.multi
    def purchase_refund(self):
        context = dict(self._context or {})
        inv_obj = self.env['account.invoice']
        inv = inv_obj.browse(context.get('invoice_id'))
        purchase_id = inv.invoice_line_ids.mapped('purchase_line_id').mapped('order_id')
        product_ids = inv.invoice_line_ids.filtered(lambda r: r.quantity > 0).mapped('product_id')
        qty_dict = {}
        prod_list = []
        for line in self.product_return_lines:
            qty_dict[line.purchase_line_id] = line.quantity
            prod_list.append(line.purchase_line_id.id)
        
        returned_move = purchase_id.mapped('order_line').mapped('move_ids').mapped('origin_returned_move_id')
        #print("returned_move",returned_move)
        move_to_return = inv.invoice_line_ids.filtered(lambda r: r.quantity > 0 and r.purchase_line_id.id in prod_list).mapped('purchase_line_id').mapped('move_ids').filtered(lambda r: r.state == 'done')
        #print("move_to_return",move_to_return)
        if purchase_id and move_to_return:
            picking_id_save = inv.picking_id
            #picking_ids = move_to_return.mapped('picking_id').filtered(lambda r: str(r.id) in picking_id_save)
            
            picking_ids = move_to_return.mapped('picking_id').filtered(lambda r: r.state == 'done')
            #print("picking_ids",picking_ids)
            for picking in picking_ids:
                if not picking.return_picking_id:
                    vals = {'picking_id':picking.id}
                    pickreturn = self.env['stock.return.picking'].with_context(active_id=picking.id).create(vals)
                    #print("return_picking_id++++++++++++++",picking.return_picking_id)
                    product_return_moves = pickreturn.product_return_moves
                    #to_rm_product_return_moves = product_return_moves.filtered(lambda r: r.move_id.id in returned_move.ids).unlink()
                    #to_rm_product_return_moves = pickreturn.product_return_moves.filtered(lambda r: r.product_id.id not in prod_list).unlink()
                    product_return_moves = product_return_moves.filtered(lambda r: r.move_id.purchase_line_id.id in prod_list)
                    
                    #print("qty_dict*******",qty_dict)
                    for moves in product_return_moves:
                        moves.write({'to_refund':True,'quantity':qty_dict.get(moves.move_id.purchase_line_id)})

                    to_rm_product_return_moves = pickreturn.product_return_moves.filtered(lambda r: r.move_id.purchase_line_id.id not in prod_list).unlink()

                    new_picking_id, pick_type_id = pickreturn._create_returns()
                    new_picking = self.env['stock.picking'].browse(new_picking_id)
                    #print("move_lines",new_picking.move_lines)
                    wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, new_picking_id)]})
                    wiz.process()
        refund_obj = self.env['account.invoice.refund']
        refund_obj = refund_obj.browse(context.get('refund_id'))
        data_refund = context.get('data_refund')
        #err
        return refund_obj.with_context(active_ids=[inv.id],qty_dict=qty_dict).compute_refund(data_refund)

    @api.multi
    def purchase_refund_no(self):
        context = dict(self._context or {})
        inv_obj = self.env['account.invoice']
        inv = inv_obj.browse(context.get('invoice_id'))
        refund_obj = self.env['account.invoice.refund']
        refund_obj = refund_obj.browse(context.get('active_ids'))
        data_refund = context.get('data_refund')
        return refund_obj.with_context(active_ids=[inv.id]).compute_refund(data_refund)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    return_picking_id = fields.Many2one('stock.picking')

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    picking_id = fields.Char(string='Picking')

    @api.model
    def create(self, vals):
        rec = super(AccountInvoice, self).create(vals)
        picking_ids = rec.invoice_line_ids.mapped('purchase_id').mapped('picking_ids').filtered(lambda r: not r.return_picking_id and r.state == 'done')
        search_inv = rec.invoice_line_ids.mapped('purchase_id').mapped('invoice_ids')
        if picking_ids:
            picking_id = False
            for picking in picking_ids:
                if search_inv:
                    for inv in search_inv:
                        if inv.picking_id and str(picking.id) not in inv.picking_id and not picking_id:
                            picking_id = str(picking.id)
                        elif inv.picking_id and str(picking.id) not in inv.picking_id and picking_id and str(picking.id) not in picking_id:
                            picking_id = picking_id + ','+str(picking.id)
                        elif not inv.picking_id and not picking_id:
                            picking_id = str(picking.id)
                        elif not inv.picking_id and picking_id and str(picking.id) not in picking_id:
                            picking_id = picking_id + ','+str(picking.id)
                else:
                    if not picking_id:
                        picking_id = str(picking.id)
                    elif picking_id and str(picking.id) not in picking_id:
                        picking_id = picking_id + ','+str(picking.id)

            if picking_id:
                rec.picking_id = picking_id
        return rec



class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        new_picking_id, pick_type_id = super(ReturnPicking, self)._create_returns()
        new_picking = self.env['stock.picking'].browse(new_picking_id)
        new_picking.return_picking_id = self.picking_id.id
        return new_picking_id, pick_type_id