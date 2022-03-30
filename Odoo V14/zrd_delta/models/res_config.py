# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    transient_account_purchase_id = fields.Many2one('account.account', related='company_id.transient_account_purchase_id', readonly=False, required=False)
    transient_account_sale_id = fields.Many2one('account.account', related='company_id.transient_account_sale_id', readonly=False, required=False)
