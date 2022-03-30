from odoo import api, fields, models, _
import datetime


class CalculateBankCommission(models.TransientModel):
    _name = "wizard.calculate.bank.commission"
    _description = "Cálculo de Comisión Bancaria"

    date = fields.Date("Fecha", default=fields.Date.today)
    pos_establishment_ids = fields.Many2many("pos.establishment", string="Establecimientos")
    line_ids = fields.One2many("wizard.calculate.bank.commission.lines", "wizard_id", "Líneas")

    @api.onchange('date', 'pos_establishment_ids')
    def _onchange_wizard(self):
        for r in self:
            lines = []
            config_obj = self.env['pos.config']
            session_obj = self.env['pos.session']
            date_init = str(r.date) + " 00:00:00"
            date_end = str(r.date) + " 23:59:59"
            r.line_ids = [(5, 0, 0)]
            if r.pos_establishment_ids:
                for pe in r.pos_establishment_ids.ids:
                    configs = config_obj.search([('pos_establishment_id', '=', pe)])
                    if configs:
                        for c in configs:
                            sessions = session_obj.search([('config_id', '=', c.id), ('start_at', '>=', date_init), ('stop_at', '<=', date_end), ('state', '=', 'closed')])
                            if sessions:
                                for s in sessions:
                                    move = s.move_id
                                    if not move.pos_processed:
                                        data = (0, 0, {
                                            'move_id': move and move.id or False,
                                            'pos_establishment_id': pe
                                        })
                                        lines.append(data)
            r.line_ids = lines

    def action_continue(self):
        for r in self:
            s_lines = []
            statement = False
            statement_obj = self.env['account.bank.statement']
            for l in r.line_ids:
                move_obj = self.env['account.move']
                payment_method = l.pos_establishment_id.pos_payment_method_id or False
                if payment_method:
                    account = payment_method.receivable_account_id or False
                    move = l.move_id
                    line = move.line_ids.filtered(lambda x: x.account_id.id == account.id)
                    if line:
                        line1 = {
                            'name': u'Comisión Bancaria - ' + move.name,
                            'debit': 0,
                            'credit': line.balance,
                            'account_id': line.account_id and line.account_id.id or False,
                        }
                        commission = round((line.balance * l.pos_establishment_id.percentage)/100, 2)
                        residual = line.balance - commission
                        line2 = {
                            'name': u'Comisión Bancaria - ' + move.name,
                            'debit': commission,
                            'credit': 0,
                            'account_id': l.pos_establishment_id.commission_account_id and l.pos_establishment_id.commission_account_id.id or False,
                        }
                        s_line = (0, 0, {
                            'date': datetime.date.today(),
                            'payment_ref': u'Comisión Bancaria - ' + move.name,
                            'amount': residual,
                        })
                        s_lines.append(s_line)
                        line3 = {
                            'name': u'Comisión Bancaria - ' + move.name,
                            'debit': residual,
                            'credit': 0,
                            'account_id': l.pos_establishment_id.conciliation_account_id and l.pos_establishment_id.conciliation_account_id.id or False,
                        }
                        line = [(0, 0, line1), (0, 0, line2), (0, 0, line3)]
                        move_vals = {
                            'ref': u'Comisión Bancaria - ' + move.name,
                            'move_type': 'entry',
                            'line_ids': line,
                            'journal_id': l.pos_establishment_id.journal_id and l.pos_establishment_id.journal_id.id or False,
                            'date': datetime.date.today(),
                            'narration': '',
                        }
                        move.pos_processed = True
                        move2 = move_obj.create(move_vals)
                        move2.post()
                    if not statement:
                        statement = statement_obj.create({
                            'name': "Cierre POS - " + str(r.date),
                            'journal_id': l.pos_establishment_id.journal_id and l.pos_establishment_id.journal_id.id or False,
                            'date': r.date,
                        })
            if statement:
                statement.line_ids = s_lines


class CalculateBankCommissionLines(models.TransientModel):
    _name = "wizard.calculate.bank.commission.lines"

    wizard_id = fields.Many2one("wizard.calculate.bank.commission", "Wizard")
    check = fields.Boolean(" ", default=True)
    move_id = fields.Many2one("account.move", "Asiento")
    pos_establishment_id = fields.Many2one('pos.establishment', 'Establecimiento')
    journal_id = fields.Many2one(related="move_id.journal_id", string="Diario")
    date = fields.Date(related="move_id.date", string="Fecha")
    currency_id = fields.Many2one(related="move_id.currency_id", string="Moneda")
    amount = fields.Monetary(related="move_id.amount_total", string="Total")
    state = fields.Selection(related="move_id.state", string="Estado")
