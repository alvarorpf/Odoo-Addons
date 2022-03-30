# coding=utf-8
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    valoration = fields.Selection([
        ('0', 'Ninguna Tarea'),
        ('1', '1-4 Tareas'),
        ('2', '4-8 Tareas'),
        ('3', '8-12 Tareas'),
        ('4', '12-16 Tareas'),
        ('5', '+16 Tareas')],
        string='Valoración',
        help='La valoración del usuario se la realiza en base a las tareas que termino')
    tag_ids = fields.Many2many('res.partner.tag', string='Etiquetas')


class PartnerTag(models.Model):
    _name = 'res.partner.tag'

    name = fields.Char('Nombre')
    color = fields.Integer('Color', default=0)