# -*- coding: utf-8 -*-
import calendar
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta
from odoo.tools import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import datetime

from odoo.tools.populate import compute


class account_asset(models.Model):

    _inherit = 'account.asset'

    location = fields.Selection([('cbba', 'CBBA'), ('lpz', 'LPZ'), ('scz', 'SCZ'),
                                 ('sczpo', 'SCZ/PROYECTO POTOSI')], string='Campo ciudad',
                                readonly=True, states={'draft': [('readonly', False)], 'model': [('readonly', True)]})
    reference_asset = fields.Char('Número de serie')

    def _recompute_board(self, depreciation_number, starting_sequence, amount_to_depreciate, depreciation_date,
                         already_depreciated_amount, amount_change_ids):
        self.ensure_one()
        residual_amount = amount_to_depreciate
        self.historical_depreciation_auxiliar = residual_amount
        # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
        move_vals = []
        prorata = self.prorata and not self.env.context.get("ignore_prorata")
        if amount_to_depreciate != 0.0:
            sw = 0
            historical_depreciation = 0
            c = 0
            var = self.depreciation_move_ids.filtered(lambda x: x.state == 'posted')
            if(self.accumulated_depreciation > 0):
                self.depreciation_initial_auxiliar = self.accumulated_depreciation
                self.historical_depreciation_auxiliar = self.amount_massive
                date_aux = self.date_massive
                date_massive_next = date_aux + timedelta(1)
                max_day_in_month = calendar.monthrange(date_massive_next.year, date_massive_next.month)[1]
                date_massive_next = date_massive_next.replace(day=max_day_in_month)
                depreciation_date = date_massive_next
                cc = starting_sequence
            else:
                self.depreciation_initial_auxiliar = 0
                var = self.depreciation_move_ids.filtered(lambda x: x.state == 'posted')

            #dapreciation_month = depreciation_date.month
            account_period = self.env['account.period'].search([('state', '=', 'open')],order='date_init')
            amount_account_period = len(account_period)
            accounting_record = self.depreciation_move_ids.filtered(lambda m: m.state == 'posted' and not m.reversal_move_id)
            order_accounting_record = sorted(accounting_record,key=lambda x: x['id'],reverse=False)
            len_accounting_record = len(order_accounting_record)
            #v = datetime.strptime(var[0].date_ufv, "%Y-%m-%d")
            #depreciation_date = v

            if(amount_account_period>0 and self.amount_massive == 0):
                depreciation_date = self.first_depreciation_date
            cc=0
            check = account_period = self.env['account.period'].search([('state', '=', 'open')])[0].date_end
            for asset_sequence in range(starting_sequence + 1, depreciation_number + 1):
                if(self.amount_massive > 0 and sw == 0):
                    cc = starting_sequence + 1
                    c = 1
                if cc < amount_account_period:
                    account_period = self.env['account.period'].search([('state', '=', 'open')])[cc]
                    cc = cc+1

                while amount_change_ids and amount_change_ids[0].date <= depreciation_date:
                    if not amount_change_ids[0].reversal_move_id:
                        residual_amount -= amount_change_ids[0].amount_total
                        amount_to_depreciate -= amount_change_ids[0].amount_total
                        already_depreciated_amount += amount_change_ids[0].amount_total
                    amount_change_ids[0].write({
                        'asset_remaining_value': float_round(residual_amount,
                                                             precision_rounding=self.currency_id.rounding),
                        'asset_depreciated_value': amount_to_depreciate - residual_amount + already_depreciated_amount,
                    })
                    amount_change_ids -= amount_change_ids[0]
                if(self.method == 'bolivian'):
                    amount,updated_increment,updated_item, valueufv, date_ufv, net_worth_item, initial_ufv, initial_date, factor, historical_depreciation, year_acumulated_depreciation,sw, depreciation_initial, year_acumulated_depreciation_updated, aitb = self._compute_board_amount(asset_sequence, residual_amount, amount_to_depreciate, depreciation_number, starting_sequence, depreciation_date, sw)

                else:
                    amount = self._compute_board_amount(asset_sequence, residual_amount, amount_to_depreciate, depreciation_number, starting_sequence, depreciation_date, sw)
                prorata_factor = 1
                if(c>0):
                    move_ref = self.name + ' (%s/%s)' % (prorata and asset_sequence + 1 or asset_sequence + 1, self.method_number)
                else:
                    move_ref = self.name + ' (%s/%s)' % (prorata and asset_sequence - 1 or asset_sequence, self.method_number)
                if prorata and asset_sequence == 1:
                    move_ref = self.name + ' ' + _('(prorata entry)')
                    first_date = self.prorata_date
                    if int(self.method_period) % 12 != 0:
                        month_days = calendar.monthrange(first_date.year, first_date.month)[1]
                        days = month_days - first_date.day + 1
                        prorata_factor = days / month_days
                    else:
                        total_days = (depreciation_date.year % 4) and 365 or 366
                        days = (self.company_id.compute_fiscalyear_dates(first_date)['date_to'] - first_date).days + 1
                        prorata_factor = days / total_days
                amount = self.currency_id.round(amount * prorata_factor)
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    if(self.method != 'bolivian'):
                        continue
                residual_amount -= amount
                method = self.method
                if(self.method == 'bolivian'):
                    residual_amount = net_worth_item
                    vals = {
                        'amount': amount,
                        'asset_id': self,
                        'move_ref': move_ref,
                        'date': depreciation_date,
                        'historical_depreciation': historical_depreciation,
                        'updated_increment': updated_increment,
                        'updated_item': updated_item,
                        'value_ufv': valueufv,
                        'date_ufv': date_ufv,
                        'factor': factor,
                        'year_acumulated_depreciation': year_acumulated_depreciation,
                        'year_acumulated_depreciation_updated': year_acumulated_depreciation_updated,
                        'net_worth_item': net_worth_item,
                        'initial_ufv': initial_ufv,
                        'initial_date': initial_date,
                        'depreciation_initial': depreciation_initial,
                        'aitb': aitb,
                        'method': method,
                        'asset_remaining_value': float_round(residual_amount,
                                                             precision_rounding=self.currency_id.rounding),
                        'asset_depreciated_value': amount,
                    }
                else:
                    vals = {
                        'amount': amount,
                        'asset_id': self,
                        'move_ref': move_ref,
                        'date': depreciation_date,
                        'method':method,
                        'asset_remaining_value': float_round(residual_amount,
                                                             precision_rounding=self.currency_id.rounding),
                        'asset_depreciated_value': amount_to_depreciate - residual_amount + already_depreciated_amount,
                    }

                if(self.method == 'bolivian' and factor > 0):
                    sw0 =0
                    check_period_account = self.env['account.period'].search([('date_end','=',date_ufv)]).state
                    if(check_period_account == 'open'):
                        verify_posted = self.depreciation_move_ids.filtered(lambda x: x.state == 'posted')
                        for r in verify_posted:
                            if(r.date_ufv == date_ufv):
                                sw0 = 1
                        if(sw0!=1):
                            move_vals.append(self.env['account.move']._prepare_move_for_asset_depreciation(vals))


                if(self.method != 'bolivian'):
                    move_vals.append(self.env['account.move']._prepare_move_for_asset_depreciation(vals))
                    depreciation_date = depreciation_date + relativedelta(months=+int(self.method_period))
                    # datetime doesn't take into account that the number of days is not the same for each month
                    if int(self.method_period) % 12 != 0:
                        max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                        depreciation_date = depreciation_date.replace(day=max_day_in_month)

                if int(self.method_period) % 12 != 0:
                    depreciation_date = depreciation_date + relativedelta(months=+int(self.method_period))
                    max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(day=max_day_in_month)
                    sw = 1

        return move_vals