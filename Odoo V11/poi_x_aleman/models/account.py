import re
from odoo import models, api, fields, _


class AccountAccount(models.Model):
    _inherit = 'account.account'

    balance_currency_id = fields.Many2one('res.currency', 'Moneda de Balance')
    balance_income_id = fields.Many2one('account.account', 'Cuenta Balance de Ingreso')
    balance_discharge_id = fields.Many2one('account.account', 'Cuenta Balance de Egreso')

