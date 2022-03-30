# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class OpStudentChangeStatus(models.TransientModel):
    _name = "create.unit"

    media_id = fields.Many2one('op.media', 'Estudiante')
    media_type_id = fields.Many2one('op.media.type', 'Tipo de Medio')
    quantity = fields.Integer('Cantidad')

    @api.multi
    def create_media_units(self):
        media_unit_obj = self.env['op.media.unit']
        count = 0
        for r in self:
            if r.media_id and r.quantity > 0:
                while count != r.quantity:
                    media_unit_obj.create({
                        'media_id': r.media_id.id,
                        'media_type_id': r.media_type_id.id,
                        'nro_unit': r.media_id.count,
                        'name': r.media_id.name + ' - ' + str(r.media_id.count)
                    })
                    r.media_id.count = r.media_id.count + 1
                    count = count + 1

