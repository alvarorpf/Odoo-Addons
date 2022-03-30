# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime


class OpRequestCharge(models.Model):
    _inherit = "res.partner"

    @api.multi
    def _compute_odoo_id(self):
        user_obj = self.env['res.users']
        for s in self:
            user_ids = user_obj.search([('partner_id', '=', s.id)])
            if user_ids:
                s.odoo_id = user_ids[0].id
                s.user_exist = True
            else:
                s.user_exist = False

    contact_id = fields.One2many('op.parent.contact', 'partner_id', 'Familiar')
    family_id = fields.Many2many(related='contact_id.family_id', readonly=True)
    odoo_id = fields.Many2one('res.users', string="Usuario de Odoo", compute="_compute_odoo_id")
    user_exist = fields.Boolean(
        'Existe usuario', compute="_compute_odoo_id")

    @api.multi
    def action_create_user(self):
        self.env.cr.execute(
            """insert into res_users("partner_id", "company_id", "login", "active", "notification_type") values ('%s', '%s', '%s', True,  'imbox')  RETURNING id;"""
            % (self.id, self.company_id.id, self.email))
        user_obj = self.env['res.users']
        user_id = self.env.cr.fetchone()
        if user_id:
            user_id = user_id[0]
        user_id = user_obj.browse(user_id)
        user_id.groups_id = user_obj._default_groups()
