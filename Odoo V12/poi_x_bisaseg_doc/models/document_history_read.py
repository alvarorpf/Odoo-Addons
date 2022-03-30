from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentHistoryRead(models.Model):
    _name = 'document.history.read'

    document_id = fields.Many2one('muk_quality_docs.document', 'Documento')
    version = fields.Char('Versión')
    user_id = fields.Many2one('res.users', 'Usuario', default=lambda self: self.env.user)
    date = fields.Datetime('Fecha de Registro', default=fields.Datetime.now())
