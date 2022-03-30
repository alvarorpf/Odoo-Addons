# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import datetime


class OperationTransaction(models.Model):
    _name = 'operation.transaction'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Operación"

    name = fields.Char('Nombre', default='Nuevo')
    user_id = fields.Many2one('res.users', string="Operador", default=lambda self: self.env.user)
    state = fields.Selection([('draft', 'Borrador'), ('process', 'Procesado'), ('posted', 'Finalizado')],
                             string='Estado', default='draft')
    date = fields.Date('Fecha', default=datetime.date.today())
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company.id)
    month = fields.Selection([('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'),
                              ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'), ('9', 'Septiembre'), ('10', 'Octubre'),
                              ('11', 'Noviembre'), ('12', 'Diciembre'), ], string='Mes')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Cuenta analítica')
    rentability = fields.Float('Rentabilidad', compute='_compute_rentability')

    purchase_ids = fields.One2many('purchase.order', 'operation_id', 'Compras')
    sale_ids = fields.One2many('sale.order', 'operation_id', 'Ventas')

    purchase_invoice_ids = fields.One2many('account.move', 'operation_id', compute='_compute_purchase_invoice')
    sale_invoice_ids = fields.One2many('account.move', 'operation_id', compute='_compute_sale_invoice')
    invoice_line_purchase_ids = fields.One2many('account.move.line', 'operation_purchase_id', 'Facturas de Compra')
    invoice_line_sale_ids = fields.One2many('account.move.line', 'operation_sale_id', 'Facturas de Venta')

    purchase_amount_base = fields.Float('Base Imponible', compute='_compute_purchase_lines')
    purchase_amount_tax = fields.Float('Impuesto', compute='_compute_purchase_lines')
    purchase_amount_total = fields.Float('Total', compute='_compute_purchase_lines')

    sale_amount_base = fields.Float('Base Imponible', compute='_compute_sale_lines')
    sale_amount_tax = fields.Float('Impuesto', compute='_compute_sale_lines')
    sale_amount_total = fields.Float('Total', compute='_compute_sale_lines')

    @api.model
    def create(self, vals):
        res = super(OperationTransaction, self).create(vals)
        if res.name == 'Nuevo':
            sequence = self.env['ir.sequence'].search([('code', '=', 'sequence.operation.transaction')])
            res.name = sequence.next_by_id() or _('Nuevo')
        return res

    @api.depends('purchase_ids')
    def _compute_purchase_invoice(self):
        for r in self:
            invoices = r.purchase_ids.invoice_ids.filtered(lambda x: x.state == 'posted')
            if invoices:
                r.purchase_invoice_ids = invoices.ids
                r._get_purchase_lines()
            else:
                r.purchase_invoice_ids = invoices

    def _get_purchase_lines(self):
        for r in self:
            for p in r.purchase_invoice_ids:
                for line in p.invoice_line_ids:
                    line.update({
                        'operation_purchase_id': r.id,
                    })

    @api.depends('sale_ids')
    def _compute_sale_invoice(self):
        for r in self:
            invoices = r.sale_ids.invoice_ids.filtered(lambda x: x.state == 'posted')
            if invoices:
                r.sale_invoice_ids = invoices.ids
                r._get_sale_lines()
            else:
                r.sale_invoice_ids = invoices

    def _get_sale_lines(self):
        for r in self:
            for p in r.sale_invoice_ids:
                for line in p.invoice_line_ids:
                    line.update({
                        'operation_sale_id': r.id,
                    })

    @api.depends('invoice_line_purchase_ids')
    def _compute_purchase_lines(self):
        for r in self:
            lines = r.invoice_line_purchase_ids
            base = 0
            tax = 0
            total = 0
            for l in lines:
                base += l.price_total
                tax += (l.price_total - l.price_subtotal)
                total += base - tax
            r.purchase_amount_base = base
            r.purchase_amount_tax = tax
            r.purchase_amount_total = total + tax

    @api.depends('invoice_line_sale_ids')
    def _compute_sale_lines(self):
        for r in self:
            lines = r.invoice_line_sale_ids
            base = 0
            tax = 0
            total = 0
            for l in lines:
                base += l.price_total
                tax += (l.price_total - l.price_subtotal)
                total += base - tax
            r.sale_amount_base = base
            r.sale_amount_tax = tax
            r.sale_amount_total = total + tax

    @api.depends('invoice_line_purchase_ids', 'invoice_line_sale_ids')
    def _compute_rentability(self):
        for r in self:
            r._compute_purchase_lines()
            r._compute_sale_lines()
            if r.purchase_amount_total and r.purchase_amount_total > 0:
                rentability = (r.sale_amount_total / r.purchase_amount_total) * 100
            else:
                rentability = 0
            r.rentability = rentability

    def action_process(self):
        for r in self:
            r.state = 'process'

    def action_confirm(self):
        for r in self:
            r.state = 'posted'
            for ip in r.purchase_invoice_ids:
                ip.operation_id = r and r.id or False
            for ip in r.sale_invoice_ids:
                ip.operation_id = r and r.id or False
            move_obj = self.env['account.move']
            journal = self.env.ref('zrd_delta.transient_account_journal')
            plines = r.invoice_line_purchase_ids.filtered(lambda x: x.is_transitory == False)
            for pline in plines:
                line1 = {
                    'name': u'Cuenta Transitoria',
                    'debit': 0,
                    'credit': pline.price_subtotal,
                    'account_id': pline.account_id.id,
                    'analytic_account_id': r.analytic_account_id.id,
                }
                line2 = {
                    'name': 'Cuenta Transitoria',
                    'debit': pline.price_subtotal,
                    'credit': 0,
                    'account_id': pline.product_id.categ_id.property_account_transient_expense_categ_id and pline.product_id.categ_id.property_account_transient_expense_categ_id.id or False,
                    'analytic_account_id': r.analytic_account_id.id,
                }
                line = [(0, 0, line1), (0, 0, line2)]
                move_vals = {
                    'ref': r.name,
                    'move_type': 'entry',
                    'line_ids': line,
                    'journal_id': journal.id,
                    'date': datetime.date.today(),
                    'narration': '',
                    'operation_id': r and r.id or False,
                }
                move = move_obj.create(move_vals)
                move.post()
                pline.is_transitory = True
            slines = r.invoice_line_sale_ids.filtered(lambda x: x.is_transitory == False)
            for sline in slines:
                line1 = {
                    'name': u'Cuenta Transitoria',
                    'debit': sline.price_subtotal,
                    'credit': 0,
                    'account_id': sline.account_id.id,
                    'analytic_account_id': r.analytic_account_id.id,
                }
                line2 = {
                    'name': 'Cuenta Transitoria',
                    'debit': 0,
                    'credit': sline.price_subtotal,
                    'account_id': sline.product_id.categ_id.property_account_transient_income_categ_id and sline.product_id.categ_id.property_account_transient_income_categ_id.id or False,
                    'analytic_account_id': r.analytic_account_id.id,
                }
                line = [(0, 0, line1), (0, 0, line2)]
                move_vals = {
                    'ref': r.name,
                    'move_type': 'entry',
                    'line_ids': line,
                    'journal_id': journal.id,
                    'date': datetime.date.today(),
                    'narration': '',
                    'operation_id': r and r.id or False,
                }
                move = move_obj.create(move_vals)
                move.post()
                sline.is_transitory = True

    def action_open(self):
        for r in self:
            r.state = 'process'

    def action_view_purchases(self):
        for r in self:
            if r.state == 'posted':
                create = 0
            else:
                create = 1
            return {
                'name': 'Compras',
                'domain': [('operation_id', '=', r.id)],
                'res_model': 'purchase.order',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'tree,form',
                'view_type': 'form',
                'context': {
                    'create': create,
                    'default_operation_id': r.id,
                    'default_analytic_account_id': r.analytic_account_id and r.analytic_account_id.id or False,
                },
            }

    def action_view_sales(self):
        for r in self:
            if r.state == 'posted':
                create = 0
            else:
                create = 1
            return {
                'name': 'Ventas',
                'domain': [('operation_id', '=', r.id)],
                'res_model': 'sale.order',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'tree,form',
                'view_type': 'form',
                'context': {
                    'create': create,
                    'default_operation_id': r.id,
                    'default_analytic_account_id': r.analytic_account_id and r.analytic_account_id.id or False,
                },
            }

    def action_sale_invoices(self):
        return {
            'name': 'Asientos Contables',
            'domain': [('operation_id', '=', self.id), ('move_type', '=', 'out_invoice')],
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'views': [[self.env.ref('account.view_out_invoice_tree').id, 'tree'],
                      [self.env.ref('account.view_move_form').id, 'form']],
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {
                'create': 0,
            },
        }

    def action_purchase_invoices(self):
        return {
            'name': 'Asientos Contables',
            'domain': [('operation_id', '=', self.id), ('move_type', '=', 'in_invoice')],
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'views': [[self.env.ref('account.view_in_invoice_tree').id, 'tree'],
                      [self.env.ref('account.view_move_form').id, 'form']],
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {
                'create': 0,
            },
        }

    def action_moves(self):
        return {
            'name': 'Asientos Contables',
            'domain': [('operation_id', '=', self.id), ('move_type', '=', 'entry')],
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'views': [[self.env.ref('account.view_move_tree').id, 'tree'],
                      [self.env.ref('account.view_move_form').id, 'form']],
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': {
                'create': 0,
            },
        }
