# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OpFaculty(models.Model):
    _name = 'op.faculty'
    _inherit = ['op.faculty', 'mail.thread', 'mail.activity.mixin']
    _description = 'Profesor'
    _rec_name = 'full_name'

    @api.multi
    @api.depends('first_name', 'last_name', 'last_name2')
    def _compute_full_name(self):
        for record in self:
            name = str(record.last_name or '') + ' ' + str(record.last_name2 or '') + ' ' + str(
                record.first_name or '')
            record.name = name
            record.full_name = name

    initials = fields.Char('Sigla')
    first_name = fields.Char('Nombres', required=True)
    last_name2 = fields.Char('Apellido Materno')
    full_name = fields.Char('Nombre Completo', compute='_compute_full_name', store=True)

    ci = fields.Char('CI')
    issued_ci = fields.Selection(
        [('lp', 'LP'), ('or', 'OR'), ('pt', 'PT'), ('cb', 'CB'), ('ch', 'CH'), ('tj', 'TJ'), ('pa', 'PA'), ('bn', 'BN'),
         ('sc', 'SC')])
    extension_ci = fields.Char('Extension')
    passport = fields.Char('Nº Pasaporte')
    due_date_visa = fields.Date('Fecha Vencimiento VISA')
    foreign_id = fields.Char('ID Extranjero')
    due_date_foreign_id = fields.Date('Fecha Vencimiento ID Extranjero')
    classification_id = fields.Many2one('op.teacher.classification', 'Clasificacion')

    @api.model
    def create(self, values):
        values['name'] = str(values['last_name'] or '') + ' ' + str(values['last_name2'] or '') + ' ' + str(values['first_name'] or '')
        record = super(OpFaculty, self).create(values)
        return record

    @api.multi
    def name_get(self):
        return [(template.id, '%s%s' % (template.full_name, template.initials and '[%s] ' % template.initials or ''))
                for template in self]
