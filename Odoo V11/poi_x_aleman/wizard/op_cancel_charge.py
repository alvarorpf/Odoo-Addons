# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class OpCancelCharge(models.TransientModel):
    _name = "op.cancel.charge"

    @api.multi
    def action_cancel_charges(self):
        if self.env.context.get('active_ids', False):
            self.env['account.op.charge'].browse(self.env.context['active_ids']).action_cancel()

