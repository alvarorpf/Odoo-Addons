from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentType(models.Model):
    _name = "document.type"

    name = fields.Char('Nombre', required=True)
    # is_father = fields.Boolean('Es Padre')
    downloadable = fields.Boolean('Descargable')
    # template_id = fields.Many2one('document.template.circuit', string='Circuito de Autorización', required=False)
    web_page = fields.Boolean('Es Página Web')
    is_guide = fields.Boolean('Es Guía')
    code = fields.Char('Código', required=True)
