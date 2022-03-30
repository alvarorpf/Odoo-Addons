# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

ACCOUNT_DOMAIN = "['&', '&', '&', ('deprecated', '=', False), ('internal_type','=','other'), ('company_id', '=', current_company_id), ('is_off_balance', '=', False)]"


class ProductProduct(models.Model):
    _inherit = "product.product"

    property_account_transient_income_categ_id = fields.Many2one('account.account', company_dependent=True,
        string="Cuenta de ingresos transitoria",
        domain=ACCOUNT_DOMAIN)
    property_account_transient_expense_categ_id = fields.Many2one('account.account', company_dependent=True,
        string="Cuenta de gastos transitoria",
        domain=ACCOUNT_DOMAIN)