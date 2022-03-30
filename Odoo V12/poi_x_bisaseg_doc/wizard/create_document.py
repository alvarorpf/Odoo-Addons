from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import datetime


class CreateDocument(models.TransientModel):
    _name = 'create.document'
    _description = 'Creación Documento'

    request_id = fields.Many2one('request.document', 'Requerimiento')
    name = fields.Char('Nombre', required=True)
    norm_id = fields.Many2one('document.norm', 'Documento Relacionado', required=True)
    type_id = fields.Many2one('document.type', 'Tipo', required=True)
    process_id = fields.Many2one('document.process', 'Proceso')
    area_ids = fields.Many2many('hr.department', string='Areas Relacionadas', required=True)
    auth_template_id = fields.Many2one('document.template.circuit', string="Circuito de Autorización", required=True)

    def action_create_document(self):
        for r in self:
            if r.request_id:
                doc = self.env['muk_quality_docs.document']
                document = doc.with_context(request=True).create({
                    'request_id': r.request_id.id,
                    'name': r.name,
                    'norm_id': r.norm_id and r.norm_id.id or False,
                    'type_id': r.type_id.id,
                    'process_id': r.process_id and r.process_id.id or False,
                    'auth_template_id': r.auth_template_id and r.auth_template_id.id or False,
                    'is_new': True,
                })
                document.area_ids = r.area_ids
                document.onchange_template_id()
                for a in self.area_ids:
                    partner_ids = self.env['res.partner'].search([('department_id', '=', a.id)])
                    if partner_ids:
                        obj = self.env['document.mandatory.reader']
                        for p in partner_ids:
                            obj.create({'document_id': document.id, 'partner_id': p.id})
                r.request_id.state = 'elaboration'
