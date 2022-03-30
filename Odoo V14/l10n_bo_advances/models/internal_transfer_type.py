# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class InternalTransferType(models.Model):
    _name = 'internal.transfer.type'
    _description = 'Tipo de Traspaso Interno'

    """
    Modelo para la administracion de tipos de movimientos internos.
    """

    name = fields.Char('Nombre', required=True)
    journal_departure_id = fields.Many2one('account.journal', string='Diario Origen', required=True)
    journal_entry_id = fields.Many2one('account.journal', string='Diario Destino', required=True)
    sequence_id = fields.Many2one("ir.sequence", "Secuencia", required=True)
    max_amount = fields.Float("Monto Maximo", required=True)
    type = fields.Selection([('expenses', 'Gastos'), ('refund', 'Reembolsos'), ('other', 'Otros Movimientos')], string="Tipo", required=True)

    @api.constrains('max_amount')
    def _check_max_amount(self):
        for record in self:
            if self.max_amount < 0:
                raise UserError(
                    _('Debe ingresar un monto mayor a 0'))