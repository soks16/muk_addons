# -*- coding: utf-8 -*-
from odoo import http

# class RlmX1(http.Controller):
#     @http.route('/rlm_x1/rlm_x1/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rlm_x1/rlm_x1/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rlm_x1.listing', {
#             'root': '/rlm_x1/rlm_x1',
#             'objects': http.request.env['rlm_x1.rlm_x1'].search([]),
#         })

#     @http.route('/rlm_x1/rlm_x1/objects/<model("rlm_x1.rlm_x1"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rlm_x1.object', {
#             'object': obj
#         })