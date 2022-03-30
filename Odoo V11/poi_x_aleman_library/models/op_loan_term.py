from odoo import models, fields


class OpLoanTerm(models.Model):
    _name = 'op.loan.term'
    _description = 'Terminos de Prestamo'

    name = fields.Char('Nombre', size=64, required=True)
    days_available = fields.Integer('Nro Dias Permitidos', required=True)
    days_reminder = fields.Integer('Nro Dias Recordatorio', required=True)
    user_reminder_id = fields.Many2one('res.users', 'Usuario de Recordatorio')
    active = fields.Boolean('Activo', default=True)
