from odoo import models, fields, api


class OpMediaType(models.Model):
    _inherit = 'op.media.unit'
    _description = 'Unidad de Libro'

    state = fields.Selection(
        [('available', 'Disponible'), ('borrowed', 'Prestado'), ('overdue', 'Atrasado'), ('inactive', 'Inactivo')],
        'Estado', default='available')
    nro_unit = fields.Integer('Nro de Ejemplar')
    state_unit_id = fields.Many2one('op.media.unit.state', 'Estado de Ejemplar')

    @api.multi
    def action_view_loans(self):
        return {
            'name': 'Histórico de Prestamos',
            'domain': [('media_unit_id', '=', self.id)],
            'res_model': 'op.media.unit.history',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 20
        }
