# -*- coding: utf-8 -*-
from odoo import http

# class RlmWebsiteCustomCss(http.Controller):
#     @http.route('/rlm_website_custom_css/rlm_website_custom_css/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rlm_website_custom_css/rlm_website_custom_css/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rlm_website_custom_css.listing', {
#             'root': '/rlm_website_custom_css/rlm_website_custom_css',
#             'objects': http.request.env['rlm_website_custom_css.rlm_website_custom_css'].search([]),
#         })

#     @http.route('/rlm_website_custom_css/rlm_website_custom_css/objects/<model("rlm_website_custom_css.rlm_website_custom_css"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rlm_website_custom_css.object', {
#             'object': obj
#         })