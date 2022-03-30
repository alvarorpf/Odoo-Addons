from odoo import api, fields, models,_
from odoo.exceptions import UserError
import json
from json import dumps


class AccountPayment(models.Model):
    _inherit = "account.payment"

    transfer_id = fields.Many2one('internal.transfer', 'Traspaso Interno')
    # Module MUST mark is_prepaid as TRUE when they want to use the prepaid accounts
    is_prepaid = fields.Boolean('Is Prepaid', default=False)

    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'is_prepaid')
    def _compute_destination_account_id(self):
        super(AccountPayment, self)._compute_destination_account_id()
        if self.partner_id and self.is_prepaid:
            if self.partner_type == 'customer':
                if not self.partner_id.property_prepaid_account_receivable_id:
                    raise UserError(_('Cuenta para pago adelantado no configurado en el contacto.'))
                self.destination_account_id = self.partner_id.property_prepaid_account_receivable_id.id
                self.partner_type = 'customer'
            else:
                if not self.partner_id.property_prepaid_account_payable_id:
                    raise UserError(_('Cuenta de cobro adelantado no configurado en el contacto.'))
                self.destination_account_id = self.partner_id.property_prepaid_account_payable_id.id
                self.partner_type = 'supplier'

    def _synchronize_from_moves(self, changed_fields):
        ''' Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):

            # After the migration to 14.0, the journal entry could be shared between the account.payment and the
            # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
            if pay.move_id.statement_line_id:
                continue

            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                if len(liquidity_lines) != 1 or len(counterpart_lines) != 1:
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal entry must always contains:\n"
                        "- one journal item involving the outstanding payment/receipts account.\n"
                        "- one journal item involving a receivable/payable account.\n"
                        "- optional journal items, all sharing the same account.\n\n"
                    ) % move.display_name)

                if writeoff_lines and len(writeoff_lines.account_id) != 1:
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, all the write-off journal items must share the same account."
                    ) % move.display_name)

                if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal items must share the same currency."
                    ) % move.display_name)

                if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal items must share the same partner."
                    ) % move.display_name)

                partner_type = counterpart_lines.move_id.payment_id.partner_type

                liquidity_amount = liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id': liquidity_lines.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount': abs(liquidity_amount),
                    'partner_type': partner_type,
                    'currency_id': liquidity_lines.currency_id.id,
                    'destination_account_id': counterpart_lines.account_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                if liquidity_amount > 0.0:
                    payment_vals_to_write.update({'payment_type': 'inbound'})
                elif liquidity_amount < 0.0:
                    payment_vals_to_write.update({'payment_type': 'outbound'})

            move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))

