from odoo import api, fields, models,_
from odoo.exceptions import UserError
import json
from json import dumps


class AccountMove(models.Model):
    _inherit = "account.move"

    def _create_bridge_move(self, line_to_reconcile, prepayment_line):
        moves = {}
        invoice_residual = abs(line_to_reconcile.amount_residual)
        if prepayment_line.debit > 0:
            debit = prepayment_line.amount_residual < invoice_residual and prepayment_line.amount_residual or invoice_residual
        else:
            debit = 0
        if prepayment_line.credit > 0:
            credit = prepayment_line.amount_residual*-1 < invoice_residual and prepayment_line.amount_residual*-1 or invoice_residual
        else:
            credit = 0
        for move in self:
            journal = move.journal_id
            part = self.env['res.partner']._find_accounting_partner(move.partner_id)
            line1 =  {
                'partner_id': part.id,
                'name': u'Conciliación por Adelanto',
                'debit': debit > 0 and 0 or credit,
                'credit': credit > 0 and 0 or debit,
                'account_id': prepayment_line.account_id.id,
                'analytic_account_id': prepayment_line.analytic_account_id.id,
            }
            line2 = {
                'partner_id': part.id,
                'name': 'Conciliación por Adelanto',
                'debit': debit,
                'credit': credit,
                'account_id': line_to_reconcile.account_id.id,
                'analytic_account_id': prepayment_line.analytic_account_id.id,
            }
            line = [(0, 0, line1),(0, 0, line2)]
            move_ref = move.name
            move_vals = {
                'ref': move_ref + str(_(' (Pago Adelantado)')),
                'line_ids': line,
                'journal_id': journal.id,
                'date': move.invoice_date,
                'narration': move.narration,
            }
            move = self.env['account.move'].create(move_vals)
            move.post()
        return move


    def register_prepayment(self, prepayment_line):
        line_to_reconcile = self.env['account.move.line']
        prepayment_line_id = line_to_reconcile.browse(prepayment_line)
        for move in self:
            line_to_reconcile += move.line_ids.filtered(
                lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable')).sorted(key=lambda r: r.date_maturity)
            for lr in line_to_reconcile:
                new_move = move._create_bridge_move(lr, prepayment_line_id)
                bridge_move_line = False
                payment_line = False
                for line in new_move.line_ids:
                    if line.account_id.id == lr.account_id.id:
                        payment_line = line
                    elif line.account_id.id == prepayment_line_id.account_id.id:
                        bridge_move_line = line
                (bridge_move_line + prepayment_line_id).reconcile()
                break
        return (line_to_reconcile + payment_line).reconcile()

    def js_assign_outstanding_line(self, line_id):
        self.ensure_one()
        lines = self.env['account.move.line'].browse(line_id)
        lines += self.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
        if len(lines) < 2:
            return self.register_prepayment(line_id)
        return lines.reconcile()

    def _compute_payments_widget_to_reconcile_info(self):
        for move in self:
            move.invoice_outstanding_credits_debits_widget = json.dumps(False)
            move.invoice_has_outstanding = False
            if move.state != 'posted' \
                    or move.payment_state not in ('not_paid', 'partial') \
                    or not move.is_invoice(include_receipts=True):
                continue
            pay_term_lines = move.line_ids\
                .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            domain = [
                #('account_id', 'in', pay_term_lines.account_id.ids),
                ('move_id.state', '=', 'posted'),
                ('partner_id', '=', move.commercial_partner_id.id),
                ('reconciled', '=', False),
                '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
            ]
            payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}
            if move.is_inbound():
                domain.append(('balance', '<', 0.0))
                payments_widget_vals['title'] = _('Outstanding credits')
            else:
                domain.append(('balance', '>', 0.0))
                payments_widget_vals['title'] = _('Outstanding debits')
            for line in self.env['account.move.line'].search(domain):
                if line.currency_id == move.currency_id:
                    amount = abs(line.amount_residual_currency)
                else:
                    amount = move.company_currency_id._convert(
                        abs(line.amount_residual),
                        move.currency_id,
                        move.company_id,
                        line.date,
                    )
                if move.currency_id.is_zero(amount):
                    continue
                payments_widget_vals['content'].append({
                    'journal_name': line.ref or line.move_id.name,
                    'amount': amount,
                    'currency': move.currency_id.symbol,
                    'id': line.id,
                    'move_id': line.move_id.id,
                    'position': move.currency_id.position,
                    'digits': [69, move.currency_id.decimal_places],
                    'payment_date': fields.Date.to_string(line.date),
                })
            if not payments_widget_vals['content']:
                continue
            move.invoice_outstanding_credits_debits_widget = json.dumps(payments_widget_vals)
            move.invoice_has_outstanding = True