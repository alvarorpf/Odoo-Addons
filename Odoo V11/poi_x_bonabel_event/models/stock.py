# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"

    regalos_line_id = fields.Many2one('regalos.line', 'Linea del evento')
    item = fields.Integer(string=u'N° item')
#     @api.model
#     def _prepare_merge_moves_distinct_fields(self):
#         distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
#         distinct_fields.append('regalos_line_id')
#         return distinct_fields
#
#     @api.model
#     def _prepare_merge_move_sort_method(self, move):
#         move.ensure_one()
#         keys_sorted = super(StockMove, self)._prepare_merge_move_sort_method(move)
#         keys_sorted.append(move.sale_line_id.id)
#         return keys_sorted
#
#     @api.model
#     def _action_done(self):
#         result = super(StockMove, self)._action_done()
#         for line in result.mapped('regalos_line_id').sudo():
#             line.qty_delivered = line._get_delivered_qty()
#         return result
#
#     @api.multi
#     def write(self, vals):
#         res = super(StockMove, self).write(vals)
#         if 'product_uom_qty' in vals:
#             for move in self:
#                 if move.state == 'done':
#                     sale_order_lines = self.filtered(
#                         lambda move: move.sale_line_id and move.product_id.expense_policy == 'no').mapped(
#                         'regalos_line_id')
#                     for line in sale_order_lines.sudo():
#                         line.qty_delivered = line._get_delivered_qty()
#         return res
#
# class ProcurementGroup(models.Model):
#     _inherit = 'procurement.group'
#
#     event_id = fields.Many2one('create.event', 'Evento')
#
# class ProcurementRule(models.Model):
#     _inherit = 'procurement.rule'
#
#     @api.model
#     def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
#         result = super(ProcurementRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
#         if values.get('regalos_line_id', False):
#             result['regalos_line_id'] = values['regalos_line_id']
#         return result
#
# class StockPicking(models.Model):
#     _inherit = 'stock.picking'
#
#     event_id = fields.Many2one(related="group_id.event_id", string="Evento", store=True)
