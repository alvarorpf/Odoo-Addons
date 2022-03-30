# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pos_establishment_id = fields.Many2one('pos.establishment', 'Establecimiento')

