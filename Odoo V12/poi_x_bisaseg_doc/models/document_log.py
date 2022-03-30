from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentLog(models.Model):
    _name = 'document.log'

    document_id = fields.Many2one('muk_quality_docs.document', 'Documento')
    user_id = fields.Many2one('res.users', 'Usuario', default=lambda self: self.env.user)
    date = fields.Date('Fecha de Registro', default=lambda self: fields.Date.context_today(self))
    activity = fields.Selection([
        ('create', 'Creación'),
        ('approve', 'Aprobación'),
        ('refuse', 'Rechazo'),
        ('stage', 'Cambio de Etapa'),
        ('state', 'Cambio de Estado'),
        ('suspend', 'Suspender'),
        ('continue', 'Continuar'),
        ('cancel', 'Cancelación'),
        ('suspension', 'Suspension'),
        ('restart', 'Reinicio'),
        ('import', 'Importación de Bizagi')], 'Actividad')
    state = fields.Selection(
        [('developing', 'Desarrollo'),
         ('approve', 'Aprobación'),
         ('pre_published', 'Pre Publicado'),
         ('published', 'Publicado'),
         ('suspend', 'Suspender'),
         ('cancel', 'Cancelado')], string='Estado')
    stage_id = fields.Many2one("muk_quality_docs.stage", string="Etapa")
    comment = fields.Char('Comentario')