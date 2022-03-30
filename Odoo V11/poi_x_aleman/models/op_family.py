# -*- coding: utf-8 -*-

from odoo import models, fields, api


class opFamily(models.Model):
    _name = 'op.family'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Familia'

    @api.multi
    def _compute_son_number(self):
        for s in self:
            s.son_number = len(s.childs_ids)

    name = fields.Char("Codigo de Familia", required=True, default='Nuevo')
    #Campos quitados del diseño segun observacion del equipo funcional
    #nit = fields.Char('NIT')
    #social_reason = fields.Char('Razon Social')
    start_date = fields.Date('Fecha de Entrada', default=fields.Datetime.now)
    end_date = fields.Date('Fecha de Salida')

    parents_ids = fields.Many2many('op.parent.contact', ondelete='cascade', string='Familiares')
    childs_ids = fields.One2many('op.student', 'family_code', ondelete='cascade', string='Hijos')
    son_number = fields.Integer('Numero de hijos', compute='_compute_son_number')

    notes = fields.Text('Notas')

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
         'El Codigo de Familia es Unica !')
    ]

    @api.multi
    def action_view_family_charges(self):
        return {
            'name': 'Cargos de Familia',
            'domain': [('family_id', '=', self.id)],
            'res_model': 'account.op.charge',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 20
        }
