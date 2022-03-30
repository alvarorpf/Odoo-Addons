# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OperationTransaction(models.Model):
    _inherit = 'operation.transaction'

    tms_code = fields.Char("Codigo de Operacion TMS")
    tms_id = fields.Integer("ID de Operacion TMS")

    def service_get_products(self):
        products = self.env['product.product'].search([])
        array_products = []
        for p in products:
            array_products.append({
                'id_product': p.id,
                'product': p.name,
                'code': p.default_code,
            })
        res = {
            'error': False,
            'products': array_products,
        }
        return res

    def service_get_operations(self):
        operations = self.env['operation.transaction'].search([('state', '!=', 'posted')])
        array_operations = []
        for o in operations:
            array_operations.append({
                'id_operation': o.id,
                'operation': o.name,
                'date': o.date,
                'month': o.month,
                'operator': o.user_id.name,
                'analytic': o.analytic_account_id.name,
                'code_tms': o.tms_code,
                'id_tms': o.tms_id,
            })
        res = {
            'error': False,
            'operations': array_operations,
        }
        return res

    def service_get_analytics(self):
        analytics = self.env['account.analytic.account'].search([])
        array_analytics = []
        for a in analytics:
            array_analytics.append({
                'id_analytic': a.id,
                'analytic': a.name,
            })
        res = {
            'error': False,
            'analytics': array_analytics,
        }
        return res

    def service_create_analytic(self, data):
        error = False
        msg = ""
        analytic_obj = self.env['account.analytic.account']
        if data:
            analytic = analytic_obj.create({
                'name': data['name']
            })
            if analytic:
                msg = "Cuenta Analítica registrada exitosamente, Cuenta Analítica (%s)" % analytic.name
        else:
            error = True
            msg = "Debe enviar algunos parametros para procesar la informacion"
        return {
            'error': error,
            'msg': msg
        }

    def service_create_operation(self, data):
        error = False
        msg = ""
        operation_obj = self.env['operation.transaction']
        analytic_obj = self.env['account.analytic.account']
        if data:
            if not 'id_analytic' in data:
                error = True
                msg = "No se cuenta con el ID de cuenta analítica de la Operación"
            analytic = analytic_obj.search([('id', '=', data['id_analytic'])])
            if not analytic:
                error = True
                msg = "No se encontro una cuenta analitica registrada."
            operation = operation_obj.create({
                'analytic_account_id': analytic and analytic.id or False,
                'month': data['month'],
                'tms_code': data['tms_code'],
                'tms_id': int(data['tms_id']),
            })
            if operation:
                msg = "Operación registrada exitosamente, Operación (%s)" % operation.name
        else:
            error = True
            msg = "Debe enviar algunos parametros para procesar la informacion"
        return {
            'error': error,
            'msg': msg
        }

    def service_create_purchase(self, data):
        error = False
        msg = ""
        purchase_obj = self.env['purchase.order']
        partner_obj = self.env['res.partner']
        product_obj = self.env['product.product']
        operation_obj = self.env['operation.transaction']
        if data:
            if not 'id_operation' in data:
                error = True
                msg = "No se cuenta con el ID de la Operación"
            if not "ci_nit" in data:
                error = True
                msg = "No se cuenta con el CI/NIT del proveedor"
            if not "r_social" in data:
                error = True
                msg = "No se cuenta con la razon social del proveedor"
            if len(data['products']) == 0:
                error = True
                msg = "No se cuenta con productos para registrar la compra"
            partner = partner_obj.search([('nit_ci', '=', data['ci_nit'])])
            operation = operation_obj.search([('id', '=', data['id_operation'])])
            if not partner:
                partner = partner_obj.create({
                    'name': data['r_social'],
                    'nit_ci': data['ci_nit'],
                    'razon_social': data['r_social'],
                })
            lines = []
            for p in data['products']:
                prod = product_obj.search([('id', '=', int(p['product_id']))])
                if not prod:
                    error = True
                    msg = "No se encuentra el producto especifico"
                else:
                    line = (0, 0, {
                        'product_id': prod and prod.id or False,
                        'name': p['description'],
                        'product_qty': int(p['quantity']),
                        'price_unit': float(p['price']),
                    })
                    lines.append(line)
            if lines:
                purchase = purchase_obj.create({
                    'partner_id': partner and partner.id or False,
                    'operation_id': operation and operation.id or False,
                    'analytic_account_id': operation.analytic_account_id and operation.analytic_account_id.id or False,
                    'order_line': lines,
                })
                if purchase:
                    msg = "Compra registrada exitosamente, Compra(%s)" % purchase.name
        else:
            error = True
            msg = "Debe enviar algunos parametros para procesar la informacion"
        return {
            'error': error,
            'msg': msg
        }

    def service_create_sale(self, data):
        error = False
        msg = ""
        sale_obj = self.env['sale.order']
        partner_obj = self.env['res.partner']
        product_obj = self.env['product.product']
        operation_obj = self.env['operation.transaction']
        if data:
            if not 'operation' in data:
                error = True
                msg = "No se cuenta con el ID de la Operación"
            if not "ci_nit" in data:
                error = True
                msg = "No se cuenta con el CI/NIT del cliente"
            if not "r_social" in data:
                error = True
                msg = "No se cuenta con la razon social del cliente"
            if len(data['products']) == 0:
                error = True
                msg = "No se cuenta con productos para registrar la venta"
            partner = partner_obj.search([('nit_ci', '=', data['ci_nit'])])
            operation = operation_obj.search([('id', '=', data['id_operation'])])
            if not partner:
                partner = partner_obj.create({
                    'name': data['r_social'],
                    'nit_ci': data['ci_nit'],
                    'razon_social': data['r_social'],
                })
            lines = []
            for p in data['products']:
                prod = product_obj.search([('id', '=', int(p['product_id']))])
                if not prod:
                    error = True
                    msg = "No se encuentra el producto especifico"
                else:
                    line = (0, 0, {
                        'product_id': prod and prod.id or False,
                        'name': p['description'],
                        'product_uom_qty': int(p['quantity']),
                        'price_unit': float(p['price']),
                    })
                    lines.append(line)
            if lines:
                sale = sale_obj.create({
                    'partner_id': partner and partner.id or False,
                    'order_line': lines,
                    'operation_id': operation and operation.id or False,
                    'analytic_account_id': operation.analytic_account_id and operation.analytic_account_id.id or False,
                })
                if sale:
                    msg = "Venta registrada exitosamente, Venta(%s)" % sale.name
        else:
            error = True
            msg = "Debe enviar algunos parametros para procesar la informacion"
        return {
            'error': error,
            'msg': msg
        }