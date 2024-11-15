# -*- coding: utf-8 -*-

from odoo import api, fields, models,_

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    customer_po_number = fields.Char('PO Number')

class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    @api.multi
    def _run_buy(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        cache = {}
        suppliers = product_id.seller_ids\
            .filtered(lambda r: (not r.company_id or r.company_id == values['company_id']) and (not r.product_id or r.product_id == product_id))
        if not suppliers:
            msg = _('There is no vendor associated to the product %s. Please define a vendor for this product.') % (product_id.display_name,)
            raise UserError(msg)

        supplier = self._make_po_select_supplier(values, suppliers)
        partner = supplier.name

        domain = self._make_po_get_domain(values, partner)

        if domain in cache:
            po = cache[domain]
        else:
            po = self.env['purchase.order'].search([dom for dom in domain])
            po = po[0] if po else False
            cache[domain] = po
        if not po:
            vals = self._prepare_purchase_order(product_id, product_qty, product_uom, origin, values, partner)
            po = self.env['purchase.order'].create(vals)
            cache[domain] = po
        elif not po.origin or origin not in po.origin.split(', '):
            if po.origin:
                if origin:
                    po.write({'origin': po.origin + ', ' + origin})
                else:
                    po.write({'origin': po.origin})
            else:
                po.write({'origin': origin})

        # Create Line
        po_line = False
        for line in po.order_line:
            if line.product_id == product_id and line.product_uom == product_id.uom_po_id:
                if line._merge_in_existing_line(product_id, product_qty, product_uom, location_id, name, origin, values):
                    vals = self._update_purchase_order_line(product_id, product_qty, product_uom, values, line, partner)
                    po_line = line.write(vals)
                    break
        if not po_line:
            vals = self._prepare_purchase_order_line(product_id, product_qty, product_uom, values, po, supplier)
            purchase_line = self.env['purchase.order.line'].create(vals)
            #Dropship case
            if purchase_line and purchase_line.sale_line_id and purchase_line.sale_line_id.order_id.po_number:
                purchase_line.write({'customer_po_number':purchase_line.sale_line_id.order_id.po_number})
            #MTO case
            if purchase_line and not purchase_line.sale_line_id and purchase_line.move_dest_ids.group_id.sale_id:
                if purchase_line.move_dest_ids[0].group_id.sale_id.po_number:
                    purchase_line.write({'customer_po_number':purchase_line.move_dest_ids[0].group_id.sale_id.po_number})
            # Write value from PO line to PO in Po number field
            if purchase_line and purchase_line.customer_po_number:
                po_number = purchase_line.order_id.po_number
                customer_po = ''
                if not po_number:
                    purchase_line.order_id.write({'po_number':purchase_line.customer_po_number})
                elif po_number and purchase_line.customer_po_number not in po_number:
                    customer_po = po_number+ ', '+purchase_line.customer_po_number
                    purchase_line.order_id.write({'po_number':customer_po})


