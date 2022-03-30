from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from datetime import datetime
import collections


class DocumentAddArea(models.TransientModel):
    _name = 'doc.add.area'
    _description = 'Añadir Area al Documento'

    doc_id = fields.Many2one('muk_quality_docs.document', 'Documento')
    type = fields.Selection([
        ('add', 'Añadir'),
        ('remove', 'Eliminar')
    ], default='add')
    area_ids = fields.Many2many('hr.department', string='Areas')
    area_remove_ids = fields.Many2many('hr.department', string="Areas")

    @api.multi
    def action_process(self):
        if self.type == 'add':
            area = []
            for a in self.area_ids:
                area.append([4, a.id])
                partner_ids = self.env['res.partner'].search([('department_id', '=', a.id)])
                if partner_ids:
                    obj = self.env['document.mandatory.reader']
                    for p in partner_ids:
                        obj.create({'document_id': self.doc_id.id, 'partner_id': p.id})
            self.doc_id.area_ids = area
        if self.type == 'remove':
            area = []
            limit = len(self.doc_id.area_ids) - len(self.area_remove_ids)
            if limit == 0:
                raise UserError('No se pueden eliminar todas las areas de un documento.')
            else:
                for a in self.area_remove_ids:
                    area.append([3, a.id])
                    obj = self.env['document.mandatory.reader']
                    partners = obj.search([('document_id', '=', self.doc_id.id), ('area_id', '=', a.id)])
                    for p in partners:
                        p.unlink()
                self.doc_id.area_ids = area

    @api.onchange('type')
    def onchage_type(self):
        area_ids = self.doc_id.area_ids.ids
        if self.type == 'add':
            return {'domain': {'area_ids': [('id', 'not in', area_ids)]},}
        elif self.type == 'remove':
            return {'domain': {'area_remove_ids': [('id', 'in', area_ids)]}, }
        else:
            return
