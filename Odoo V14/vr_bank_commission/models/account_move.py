# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    pos_processed = fields.Boolean('Procesado en POS', default=False)
