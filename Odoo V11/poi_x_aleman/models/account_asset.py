# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from dateutil import parser
from odoo.exceptions import UserError, ValidationError


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    notes = fields.Char('Notas')
    amount = fields.Integer('Cantidad')
    code = fields.Char(string='Referencia', size=50, readonly=False)

    @api.one
    @api.constrains('code')
    def _check_unique_code(self):
        if self.code:
            asset = self.env['account.asset.asset'].search([('code', '=', self.code)])
            if len(asset) > 1:
                raise ValidationError(_('El código que esta tratando de ingresar ya se encuentra registrado".'))


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    def asset_create(self):
        # SuperCopyCheck. Override de la creación del Activo para la respectiva asignación de cuenta analítica
        # Ajuste para la compra de activos fijos para el colegio aleman, se crean la cantidad de datos maestros solicitados en las facturas de proveedor
        if self.asset_category_id:
            count = 1
            price = self.price_subtotal / self.quantity
            code = ''
            while count <= int(self.quantity):
                if self.invoice_id and self.invoice_id.number:
                    code = self.invoice_id.number + '-' + self._get_code(self.invoice_id.asset_sequence)
                vals = {
                    'name': self.name,
                    'code': code,
                    'category_id': self.asset_category_id.id,
                    'value': price,
                    'partner_id': self.invoice_id.partner_id.id,
                    'company_id': self.invoice_id.company_id.id,
                    'currency_id': self.invoice_id.company_currency_id.id,
                    'date': self.asset_start_date or self.invoice_id.date_invoice,
                    'invoice_id': self.invoice_id.id,
                    'account_analytic_id': self.account_analytic_id.id or self.asset_category_id.account_analytic_id.id,  # Asigna la cuenta analítica del gasto
                    'amount': 1,
                }
                changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
                vals.update(changed_vals['value'])
                asset = self.env['account.asset.asset'].create(vals)
                if self.asset_category_id.open_asset:
                    asset.validate()
                count = count + 1
                self.invoice_id.asset_sequence = self.invoice_id.asset_sequence + 1
        return True

    @api.multi
    def _get_code(self, number):
        if number:
            code = 0
            if number < 10:
                code = '0000' + str(number)
            elif number >= 10 and number < 100:
                code = '000' + str(number)
            elif number >= 100 and number < 1000:
                code = '00' + str(number)
            elif number >= 1000 and number <=10000:
                code = '0' + str(number)
            return code