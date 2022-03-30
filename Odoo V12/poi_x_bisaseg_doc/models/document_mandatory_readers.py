from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentMandatoryReaded(models.Model):
    _name = "document.mandatory.reader"

    document_id = fields.Many2one('muk_quality_docs.document', string='Documento')
    partner_id = fields.Many2one('res.partner', string='Lector')
    area_id = fields.Many2one('hr.department', related='partner_id.department_id', store=True)
