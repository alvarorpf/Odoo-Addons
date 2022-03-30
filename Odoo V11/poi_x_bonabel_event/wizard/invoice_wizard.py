# -*- coding: utf-8 -*-
##############################################################################
#   Copyright (C) 2018 Poiesis Consulting (<http://www.poiesisconsulting.com>).
#   by jory
##############################################################################

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError


class ListInvoiceWizard(models.Model):
    _name = 'listinvoicewizard'

    # order_id = fields.Many2one('sale.order', string='Order Reference', index=True, copy=False)
    # name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence')
    event_id = fields.Many2one('create.event', 'Evento')
    # product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    # product_image = fields.Binary('Product Image', related="product_id.image", store=False)


class InvoiceWizard(models.TransientModel):
    _name = 'invoice.wizard'
    _description = 'Entregar Factura'

    @api.model
    def _event_req(self):
        event_id = self._context.get('active_id')
        return event_id

    cliente_id = fields.Many2one('res.partner', 'Cliente', required=True)
    event_id = fields.Many2one('create.event', 'Evento', readonly=True, default=_event_req)
    invoice_line = fields.Many2many('regalos.line', 'tab_invoice_lines', 'event_id', 'user_id',
                                    string=u'Items a Facturar')
    # invoice_line = fields.One2many('regalos.line', 'event_id', string='invoice lines', copy=True, auto_join=True)
    # invoice_line = fields.Many2one('regalos.line', string='invoice lines', copy=True, auto_join=True)
    # picking_id = fields.Many2one('stock.picking', string=u'Entregado')
    checked_conentrega = fields.Boolean('Recogido')
    price_unit = fields.Integer(string=u'precio unitario')
    estado = fields.Char(string=u'Estado')

    @api.multi
    def facturar_evento(self):
        inv_ref = self.env['account.invoice']
        inv_ids = []
        event_id = self._context.get('active_id')
        event_data = self.env['create.event'].browse(event_id)
        id_wizard = self.env['invoice.wizard'].browse(self.ids)
        checked_entrega = id_wizard[0]['checked_conentrega']
        cliente_id = id_wizard[0]['cliente_id']
        nit_cliente = id_wizard[0]['cliente_id'].nit
        if nit_cliente == False:
            nit_cliente = ''

        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': '',
            'origin': event_data.name,
            'type': 'out_invoice',
            'account_id': self.cliente_id.property_account_receivable_id.id,
            'partner_id': self.cliente_id.id,
            'partner_shipping_id': self.cliente_id.id,
            'journal_id': journal_id,
            'currency_id': event_data.pricelist_id.currency_id.id,
            'comment': '',
            'company_id': event_data.company_id.id,
            'user_id': self._uid,
        }
        invoice = inv_ref.create(invoice_vals)

        for line in event_data.invoice_line:
            res = {}
            account = line.product_id.property_account_income_id or line.product_id.categ_id.property_account_income_categ_id
            if not account:
                raise UserError(_('Please define income account for this product: "%s" (id:%d) - or for its category: "%s".') %
                    (line.product_id.name, line.product_id.id, line.product_id.categ_id.name))

            res = {
                'name': line.product_id.name,
                'sequence': 1,
                'origin': event_data.name,
                'account_id': account.id,
                'price_unit': line.price_unit,
                'quantity': 1,
                'discount': 0,
                'uom_id': line.product_id.uom_id.id,
                'product_id': line.product_id.id or False,
                'invoice_id': invoice.id,
            }
            inv_id = self.env['account.invoice.line'].create(res)
            inv_id = inv_id.id

            for order1 in line.invoice_line:
                inv_ids = []
                inv_line_ref = self.env['account.invoice.line']
                product_obj = self.env['product.product']
                #inv_ids.append(inv_id)
                if order1.factura:
                    inv_ids.append(order1.factura.id)
                ir_conf_pool = self.env['ir.config_parameter']
                #product_service = ir_conf_pool.get_param(cr, uid, 'product_service', None, context=context)
                if (order1.product_id):
                    acc = order1.product_id.property_stock_account_input.id
                    if not acc:
                        acc = order1.product_id.product_tmpl_id.categ_id.property_account_income_categ_id.id
                        if not acc:
                            raise UserError(_('Por favor defina la cuenta de ingreso de este Producto: "%s" (id:%d) - o para su categoría: "%s".') %
                                (order1.product_id.name, order1.product_id.id, order1.product_id.categ_id.name))
                inv_line = {
                    #'invoice_id': inv_id,
                    'product_id': order1.product_id.id,  # product_abono_id.id,
                    'account_id': acc,
                    'quantity': order1.product_uom_qty,
                    'price_unit': order1.price_unit,
                    'name': order1.event_id.name  # product_abono_id.id
                }
                inv_line.update(inv_line_ref.product_id_change([],
                                                               order1.product_id.id,
                                                               order1.product_id.uom_id.id,
                                                               1, partner_id=id_wizard[0]['cliente_id'].id,
                                                               fposition_id=id_wizard[0]['cliente_id'].property_account_position.id)['value'])

                inv_line['invoice_line_tax_id'] = [(6, 0, [x.id for x in order1.product_id.taxes_id])]
                #inv_line_ref.create(cr, uid, inv_line, context=context)
                #inv_ids.append(inv_id)
                self.env['regalos.line'].write(order1.id, {'factura': inv_id})
                self.env['regalos.line'].write(order1.id, {'partner_id': cliente_id})
                self.env['create.event'].write([self.event_cli.id], {'actualizar_func': '.'})

                id_wizard = self.pool.get('facturar.wizard').browse(self.ids)
                checked_entrega = id_wizard[0]['checked_conentrega']
                if checked_entrega == False:
                    self.pool.get('regalos.line').write(order1.id, {'estado': 'vendido'})

            mod_obj = self.env['ir.model.data']
            res = mod_obj.get_object_reference('account', 'invoice_form')
            res_id = res and res[1] or False