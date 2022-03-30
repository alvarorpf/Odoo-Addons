# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    operation_id = fields.Many2one('operation.transaction', 'Operacion de transacción')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    operation_purchase_id = fields.Many2one('operation.transaction', 'Transaccion de Flete')
    operation_sale_id = fields.Many2one('operation.transaction', 'Transaccion de Flete')
    state = fields.Selection(related='move_id.state', string='Estado', readonly=True)
    payment_state = fields.Selection(related='move_id.payment_state', string='Estado de Pago', readonly=True)
    is_transitory = fields.Boolean('Transitoria Aplicada')

    def action_edit_description(self):
        context = {}
        context['active_ids'] = self.ids
        context['invoice_line_id'] = len(self.ids) > 0 and self.ids[0] or False
        view_id = self.env.ref('zrd_delta.edit_description_wizard_form').id
        wizard_form = {
            'name': u"Edición de Descripción",
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'edit.description.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'domain': str([]),
            'target': 'new',
            'context': context,
        }
        return wizard_form
