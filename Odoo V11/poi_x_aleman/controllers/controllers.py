# -*- coding: utf-8 -*-
from odoo import http

class Academy(http.Controller):
     @http.route('/Familia', auth='user', website=True)
     def index(self, **kw):
         user = http.request.env.user
         family = http.request.env['op.family']
         family = family.search([])
         return http.request.render('poi_x_aleman.family_web', {
             'family': family
         })

     @http.route('/Familia/Alumno', type='http', auth='user', website=True)
     def student(self, redirect=None, **post):
         values = self._prepare_portal_layout_values()
         #partner = request.env.user.partner_id
         values.update({
             'error': {},
             'error_message': [],
         })
