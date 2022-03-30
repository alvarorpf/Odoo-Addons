# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, tools


class Company(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    transient_account_purchase_id = fields.Many2one('account.account', 'Cuenta Transitoria Compras', required=False)
    transient_account_sale_id = fields.Many2one('account.account', 'Cuenta Transitoria Ventas', required=False)