from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentProcess(models.Model):
    _name = "document.process"

    name = fields.Char('Nombre', required=True)
    process_father_id = fields.Many2one('document.process', string='Proceso Padre')
    code = fields.Char('Código', required=True)
