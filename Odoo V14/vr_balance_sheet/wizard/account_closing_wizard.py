# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountClosingWizard(models.TransientModel):
    _name = 'account.closing.wizard'
    _description = ''

    name = fields.Char()
    date_start = fields.Date(string="Fecha de Inicio")
    date_end = fields.Date(string="Fecha Final")
    drag_account_id = fields.Many2one('account.account', string="Cuenta de resultado actual")
    closing_account_id = fields.Many2one('account.account', string="Cuenta de orden")
    journal_id = fields.Many2one('account.journal', string="Diario")
    amount = fields.Float(string="Monto", compute='compute_amount')
    amount_transfer = fields.Float(string="Monto",compute='compute_amount')

    @api.depends('date_start', 'date_end', 'drag_account_id')
    def compute_amount(self):
        """Metodo que trae la ganancias o perdidas del perdio selccioando
           :param self:
           :return:Ganancia y perdidas del periodo seleccionado
           """
        if self.date_start and self.date_end:
            options = {'unfolded_lines': [],
                       'date': {'string': '2021', 'period_type': 'fiscalyear', 'mode': 'range', 'strict_range': False,
                                'date_from': '2021-01-01', 'date_to': '2021-08-30', 'filter': 'custom'}}
            options['date']['date_from'] = self.date_start.strftime('%Y-%m-%d')
            options['date']['date_to'] = self.date_end.strftime('%Y-%m-%d')
            var, line = self.env['account.financial.html.report'].browse(1)._get_table(options)
            self.amount = line[-1]['columns'][0]['no_format']
        else:
            self.amount = 0
        if self.date_start and self.date_end and self.drag_account_id:
            account_line = self.env['account.move.line'].search([('account_id', '=', self.drag_account_id.id),
                                                                 ('move_id.state', '=', 'posted'),
                                                                 ('move_id.date', '>=', self.date_start.strftime('%Y-%m-%d')),
                                                                 ('move_id.date', '<=', self.date_end.strftime('%Y-%m-%d'))])
            debit = 0
            credit = 0
            for line in account_line:
                debit += line.debit
                credit += line.credit
            self.amount_transfer = debit - credit
        else:
            self.amount_transfer = 0

    def action_redistribute(self):
        """Se crea un asiento contable con la informacion que tiene el wizard
           :param self:
           :return:Ganancia y perdidas del periodo seleccionado
           """
        obj_account_move = self.env['account.move']
        array = []
        if self.amount == 0:
            raise UserError(_("No hay un monto para el cierre"))
        if self.amount > 0:
            array.append((0, 0, {'account_id': self.drag_account_id.id, 'credit': abs(self.amount)}))
            array.append((0, 0, {'account_id': self.closing_account_id.id, 'debit': abs(self.amount)}))
        if self.amount < 0:
            array.append((0, 0, {'account_id': self.drag_account_id.id, 'debit': abs(self.amount)}))
            array.append((0, 0, {'account_id': self.closing_account_id.id, 'credit': abs(self.amount)}))
        account_move = obj_account_move.create({'ref': 'Traspaso', 'journal_id': self.journal_id.id, 'date': fields.Date.today(), 'line_ids': array})
        return {
            'name': _('Asiento Contable'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_id': account_move.id,
            'target': 'new',
        }

    def action_redistribute_transfer(self):
        """Se crea un asiento contable con la informacion que tiene el wizard
           :param self:
           :return:Ganancia y perdidas del periodo seleccionado
           """
        obj_account_move = self.env['account.move']
        array = []
        if self.amount_transfer == 0:
            raise UserError(_("No hay un monto para el cierre"))
        if self.amount_transfer > 0:
            array.append((0, 0, {'account_id': self.drag_account_id.id, 'credit': abs(self.amount_transfer)}))
            array.append((0, 0, {'account_id': self.closing_account_id.id, 'debit': abs(self.amount_transfer)}))
        if self.amount_transfer < 0:
            array.append((0, 0, {'account_id': self.drag_account_id.id, 'debit': abs(self.amount_transfer)}))
            array.append((0, 0, {'account_id': self.closing_account_id.id, 'credit': abs(self.amount_transfer)}))
        account_move = obj_account_move.create({'ref': 'Traspaso', 'journal_id': self.journal_id.id, 'date': fields.Date.today(), 'line_ids': array})
        return {
            'name': _('Asiento Contable'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_id': account_move.id,
            'target': 'new',
        }