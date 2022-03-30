from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentStage(models.Model):
    _inherit = "muk_quality_docs.stage"

    register_discharge_date = fields.Boolean('Registro de Fecha de Baja', help='Si se encuentra Marcado este campo cuando un documento entre en esta etapa se registra la fecha de baja del documento.')