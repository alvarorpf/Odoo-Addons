# -*- coding: utf-8 -*-
##############################################################################
#   Copyright (C) 2018 Poiesis Consulting (<http://www.poiesisconsulting.com>).
#   by jory
##############################################################################

from odoo import models, fields, api, exceptions, _
from datetime import datetime, timedelta, time
from odoo import netsvc
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class TransferWizard(models.TransientModel):
    """
    For Traspaso
    """
    _name = "transfer.wizard"
    _description = "Traspaso wizard"

    @api.model
    def _event_req(self):
        event_id = self._context.get('active_id')
        return event_id

    event_id = fields.Many2one('create.event', 'Evento', readonly=True, default=_event_req)
    traspaso_lines = fields.Many2many('regalos.line', 'general_regalos_tras', 'event_id', 'user_id',
                                      string=u'Items a Traspasar')
    picking_id = fields.Many2one('stock.picking', 'Traspasado'),

    @api.multi
    def transfer_event(self):
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        active_id = self._context.get('active_id')
        create_event_pool = self.env['create.event']
        event_cli = create_event_pool.browse(active_id)
        picking_id = 0
        for order in self.browse(self.ids):
            for line in order.traspaso_lines:
                if picking_id == 0:
                    # addr = event_cli.partner_id.id and partner_obj.address_get([event_cli.partner_id.id], ['delivery']) or {}
                    company_id = self.env['res.users'].browse(self._uid).company_id.id
                    picking_id = picking_obj.create({
                        'origin': event_cli.name,
                        'partner_id': event_cli.partner_id.id,
                        'company_id': company_id,
                        'move_type': 'direct',
                        'state': 'done',
                        'invoice_state': 'none',
                        'auto_picking': True,
                    })
                    self.write([order.id], {'picking_id': picking_id})
                output_id = event_cli.shop_id.warehouse_id.lot_input_id.id
                product_tpml_id = self.env['product.product'].browse(self.line.product_id.id).product_tmpl_id.id
                standard_price = self.env['product.template'].browse(self.product_tpml_id).standard_price
                move_obj.create({
                    'name': line.product_id.name,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uos': line.product_id.uom_id.id,
                    'picking_id': picking_id,
                    'product_id': line.product_id.id,
                    'price_unit': standard_price,
                    'product_uom_qty': 1,
                    'product_qty': 1,
                    'state': 'done'
                })
                regalos_line_id = line.id
                self.env['regalos.line'].write([regalos_line_id], {'estado': 'traspasado'})
                self.env['create.event'].write([event_cli.id], {'actualizar_func': '.'})
            if order.traspaso_lines:
                return {'type': 'ir.actions.act_window_close'}
            else:
                raise Warning(_('Error!'), _('Debe almenos seleccionar un item para Traspasar'))
                return False
