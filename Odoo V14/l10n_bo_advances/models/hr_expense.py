# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    """
    Campo para relacionar un anticipo con un informe de gastos
    """
    advance_id = fields.Many2one('internal.transfer', 'Traspaso Interno')

