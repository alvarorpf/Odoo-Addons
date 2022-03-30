from odoo import fields, models, api
from odoo.exceptions import UserError


class EditDescription(models.TransientModel):
    _name = 'edit.description.wizard'
    _description = "Edición de Descripción"

    description = fields.Text('Descripción', required=True)

    def action_update_description(self):
        context = {}
        if 'invoice_line_id' in self.env.context and self.env.context['invoice_line_id']:
            invoice_line_id = self.env.context['invoice_line_id']
        else:
            return True
        for data in self.read():
            description = data['description']
            iline = self.env['account.move.line'].browse(invoice_line_id)[0]
            if iline.move_id.state != 'posted':
                raise UserError('No es posible editar la descripcion de una factura Factura en borrador.')
            else:
                iline.write({'name': description})
                return True
