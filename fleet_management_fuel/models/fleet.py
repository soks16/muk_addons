# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models, fields, _
import odoo.addons.decimal_precision as dp
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning,UserError
from collections import defaultdict


class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    next_km = fields.Float(string='Km prochain vidange', help='Km prochain vidange', compute='compute_next_km', store=True)

    validate_suivi = fields.Boolean('Suivi du prochain service',related='cost_subtype_id.validate_suivi')

    @api.multi
    @api.depends('cost_subtype_id', 'odometer')
    def compute_next_km(self):
        company = self.env.user.company_id
        for rec in self:
            if rec.cost_subtype_id.validate_suivi:
                rec.next_km = rec.odometer + company.next_km
            else:
                rec.next_km = 0

class FleetServiceType(models.Model):
    _inherit = 'fleet.service.type'

    validate_suivi = fields.Boolean('Suivi du prochain service')

class FleetVehicleLogFuel(models.Model):
    # _inherit = 'fleet.vehicle.log.fuel'
    _name = 'fleet.vehicle.log.fuel'
    _inherit=['fleet.vehicle.log.fuel','mail.thread','mail.activity.mixin']


    @api.model
    def _get_default_product(self):
        return self.env.ref('fleet_management_fuel.gasoil_produit', False) and self.env.ref('fleet_management_fuel.gasoil_produit') or self.env['product.product']

    product_id = fields.Many2one('product.product','Produit',readonly=True, default=_get_default_product)

    next_km = fields.Float(string='Km prochain vidange', help='Km prochain vidange')

    # product_id = fields.Many2one('product.product','Produit',readonly=True, default=lambda self: self.env.ref('fleet_management_fuel.gasoil_produit').id)
    # product_id = fields.Many2one('product.product','Produit',readonly=True)
    price_per_liter = fields.Float(related='product_id.lst_price', store=True)
    validate_cons = fields.Boolean('Consommation gasoil validé')
    consom_type = fields.Selection([
        ('interne', 'Interne'),
        ('externe', 'Externe')
        ], 'Gasoil interne/externe', default="interne", required=True)


    # @api.model
    @api.multi
    def consommation_gasoil(self):
        # print('-----------------consommation')
        self.write({
            'validate_cons': True
        })
        if self.consom_type == 'interne':
            type_operation = self.env['stock.picking.type'].search([('code','=','internal')])[0]
            vals ={
            'picking_type_id':type_operation.id,
            'move_type':'direct',
            'location_id':type_operation.default_location_src_id.id,
            'location_dest_id':type_operation.default_location_dest_id.id,
            }
            picking = self.env['stock.picking'].create(vals)
            move_line={
            'name':self.product_id.name,
            'product_uom':self.product_id.uom_id.id,
            'product_id':self.product_id.id,
            'product_uom_qty':self.liter,
            'quantity_done':self.liter,
            'location_id':type_operation.default_location_src_id.id,
            'price_unit':self.price_per_liter,
            'tax_ids':[(6, 0, self.product_id.taxes_id.ids)],
            # 'location_dest_id': type_operation.default_location_dest_id.id,

            'location_dest_id': self.env.ref('fleet_management_fuel.stock_location_cons_wh').id, # type_operation.default_location_dest_id.id,
            'picking_id':picking.id,
            }
            stock_move = self.env['stock.move'].create(move_line)
            if picking.move_lines:
                picking.button_validate()
            else:
                picking.unlink()
        km_liste = []
        for service in self.vehicle_id.log_services:
            km_liste.append(service.next_km)
        greater_km = (max(km_liste))

        self.write({
            'next_km': greater_km
        })
        # print (km_liste)
        # print (greater_km)
        company = self.env.user.company_id
        if self.odometer >= greater_km - company.notif_km:
            # print ('================== time to vidange')
            # print (datetime.today())
            template_id = self.env['mail.template'].search([('model_id.model', '=','fleet.vehicle.log.fuel'),('name', '=','Vidange')])[0]
            # print(template_id)
            if template_id:
                template_id.send_mail(self.id)
            date = fields.Datetime.from_string(self.date)   
            self.env['mail.activity'].sudo().create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': 'Vidange pour ' + self.vehicle_id.name,
                'date_deadline' : date,
                'user_id': self._uid,
                'res_id': self.id,
                'res_model_id': self.env.ref('fleet_management_fuel.model_fleet_vehicle_log_fuel').id,

            })

class FleetVehicle(models.Model):
    
    _name = 'fleet.vehicle'
    _inherit=['fleet.vehicle','mail.thread','mail.activity.mixin']

    user_id = fields.Many2one('res.users', string='Chef de Parc auto', required=True, track_visibility='onchange', default=lambda self: self.env.user)
    assurance_date = fields.Date('Date renouvellement assurance', help='date de renouvellement assurance')
    visite_date = fields.Date('Date prochaine visite technique', help='date de la prochaine visite technique')
    carnet_date = fields.Date('Date renouvellement carnet de circulation', help='date de renouvellement carnet de circulation')
    assurance_notif = fields.Date('Date notif assurance', compute='_compute_assurance_notif',store=True)
    visite_notif = fields.Date('Date notif visite technique', compute='_compute_visite_notif',store=True)
    carnet_notif = fields.Date('Date notif carnet de circulation', compute='_compute_carnet_notif',store=True)


    @api.one
    @api.depends('assurance_date')
    def _compute_assurance_notif(self):
        company = self.env.user.company_id
        days_notif = company.jr_notif
        if self.assurance_date:
            date_notif = fields.Datetime.from_string(self.assurance_date) - relativedelta(days=days_notif)

            self.assurance_notif = date_notif
            
    @api.one
    @api.constrains('assurance_notif')
    def const_notif_assurance(self):
        if self.assurance_notif:
            mail_activity_id = self.env['mail.activity'].search([('res_id', '=',self.id),('summary', 'ilike', 'Notifcation renouvellement assurance pour'),('res_model_id', '=',self.env.ref('fleet.model_fleet_vehicle').id)])
            print ('================= here assurance_notif' )
            print (mail_activity_id)
            if mail_activity_id:
                mail_activity_id.sudo().write({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': 'Notifcation renouvellement assurance pour ' + self.name,
                    'date_deadline' : self.assurance_notif,
                    'user_id': self.user_id.id,
                    # 'res_id': event.id,
                    # 'res_model_id': self.env.ref('elevage.model_animal_event_calendar').id,

                })
            else:
                mail_activity_id.sudo().create({
                    'res_id': self.id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': 'Notifcation renouvellement assurance pour ' + self.name,
                    'date_deadline' : self.assurance_notif,
                    'user_id': self.user_id.id,
                    # 'res_id': event.id,
                    'res_model_id': self.env.ref('fleet.model_fleet_vehicle').id,

                })
    @api.one
    @api.depends('visite_date')
    def _compute_visite_notif(self):
        company = self.env.user.company_id
        days_notif = company.jr_notif
        if self.visite_date:
            self.visite_notif = fields.Datetime.from_string(self.visite_date) - relativedelta(days=days_notif)
            
            
    @api.one
    @api.constrains('visite_notif')
    def const_notif_visite(self):
        if self.visite_notif:
            mail_activity_id = self.env['mail.activity'].search([('res_id', '=',self.id),('summary', 'ilike', 'Notifcation de la visite technique pour'),('res_model_id', '=',self.env.ref('fleet.model_fleet_vehicle').id)])
            print ('================= here visite_notif' )
            print (mail_activity_id)
            if mail_activity_id:
                mail_activity_id.sudo().write({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': 'Notifcation de la visite technique pour ' + self.name,
                    'date_deadline' : self.visite_notif,
                    'user_id': self.user_id.id,
                    # 'res_id': event.id,
                    # 'res_model_id': self.env.ref('elevage.model_animal_event_calendar').id,

                })
            else:
                mail_activity_id.sudo().create({
                    'res_id': self.id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': 'Notifcation de la visite technique pour ' + self.name,
                    'date_deadline' : self.visite_notif,
                    'user_id': self.user_id.id,
                    # 'res_id': event.id,
                    'res_model_id': self.env.ref('fleet.model_fleet_vehicle').id,

                })
    @api.one
    @api.depends('carnet_date')
    def _compute_carnet_notif(self):
        company = self.env.user.company_id
        days_notif = company.jr_notif
        if self.carnet_date:
            self.carnet_notif = fields.Datetime.from_string(self.carnet_date) - relativedelta(days=days_notif)
            
            
    @api.one
    @api.constrains('carnet_notif')
    def const_notif_carnet(self):
        if self.carnet_notif:
            mail_activity_id = self.env['mail.activity'].search([('res_id', '=',self.id),('summary', 'ilike', 'Notifcation renouvellement carnet de circulation pour'),('res_model_id', '=',self.env.ref('fleet.model_fleet_vehicle').id)])
            print ('================= here carnet_notif' )
            print (mail_activity_id)
            if mail_activity_id:
                mail_activity_id.sudo().write({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': 'Notifcation renouvellement carnet de circulation pour ' + self.name,
                    'date_deadline' : self.carnet_notif,
                    'user_id': self.user_id.id,
                    # 'res_id': event.id,
                    # 'res_model_id': self.env.ref('elevage.model_animal_event_calendar').id,

                })
            else:
                mail_activity_id.sudo().create({
                    'res_id': self.id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': 'Notifcation renouvellement carnet de circulation pour ' + self.name,
                    'date_deadline' : self.carnet_notif,
                    'user_id': self.user_id.id,
                    # 'res_id': event.id,
                    'res_model_id': self.env.ref('fleet.model_fleet_vehicle').id,

                })

    @api.model
    def send_notification(self):
        assurance_events = self.search([('assurance_notif', '=', fields.Datetime.now())])
        visite_events = self.search([('visite_notif', '=', fields.Datetime.now())])
        carnet_events = self.search([('carnet_notif', '=', fields.Datetime.now())])
        # print('=============== send_notification')
        # print(fields.Datetime.now())
        for event in assurance_events:
            template_id = self.env['mail.template'].search([('model_id.model', '=','fleet.vehicle'),('name', '=','Renouvellement assurance')])[0]
            if template_id:
                template_id.send_mail(event.id)
        for event in visite_events:
            template_id = self.env['mail.template'].search([('model_id.model', '=','fleet.vehicle'),('name', '=','Visite technique')])[0]
            if template_id:
                template_id.send_mail(event.id)
        for event in carnet_events:
            template_id = self.env['mail.template'].search([('model_id.model', '=','fleet.vehicle'),('name', '=','Renouvellement carnet de circulation')])[0]
            if template_id:
                template_id.send_mail(event.id)