# -*- coding: utf-8 -*-
##############################################################################
#   Copyright (C) 2018 Poiesis Consulting (<http://www.poiesisconsulting.com>).
#   by jory
##############################################################################

from odoo import models, fields, api, exceptions, _
from datetime import datetime, timedelta, time
from odoo import netsvc
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class AdvanceWizard(models.TransientModel):
    """
    For Advance
    """
    _name = "advance.wizard"
    _description = "Anticipo wizard"

    event_id = fields.Many2one('create.event', 'Evento', required=True, readonly=True)
    partner_id = fields.Many2one('res.partner', string=u'Cliente')
    advance_lines = fields.Many2many('regalos.line', 'general_regalos_rel_adv', 'event_id', 'user_id',
                                     string=u'Items de Anticipo')
    picking_id = fields.Many2one('stock.picking', 'Traspasado'),

    @api.model
    def default_get(self, fields):
        res = super(AdvanceWizard, self).default_get(fields)
        event_id = self._context.get('active_id')
        res.update({
            'event_id': event_id
        })
        return res
