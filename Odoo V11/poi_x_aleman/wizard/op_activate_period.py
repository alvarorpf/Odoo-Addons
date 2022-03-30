# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ActivatePeriod(models.TransientModel):
    _name = "op.activate.period"

    period_id = fields.Many2one('op.school.period', 'Gestion Escolar')

    @api.multi
    def action_activate_period(self):
        for r in self:
            if r.period_id:
                r.period_id.state = 'active'
