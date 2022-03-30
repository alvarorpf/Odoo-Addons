from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class DocumentSequence(models.Model):
    _name = "document.sequence"

    @api.multi
    @api.depends('type_id', 'process_id', 'system_id')
    def _compute_code(self):
        for s in self:
            if s.type_id and s.type_id.code:
                if s.type_id.is_guide:
                    if s.system_id and s.system_id.name:
                        s.code = s.code_start + s.type_id.code + s.system_id.name
                else:
                    if s.process_id and s.process_id.code:
                        s.code = s.code_start + s.type_id.code + s.process_id.code

    code_start = fields.Char('Prefijo Inicial', default="S", required=True)
    type_id = fields.Many2one('document.type', 'Tipo de Documento')
    process_id = fields.Many2one('document.process', 'Proceso')
    system_id = fields.Many2one('document.system', 'Sistema')
    number_increment = fields.Integer('Incremento', default=1)
    next_number = fields.Integer('Proximo Numero', default=1)
    code = fields.Char('Código', compute="_compute_code", store=True)
    is_guide = fields.Boolean('Es Guía', related="type_id.is_guide")

    @api.multi
    def generate(self, domain):
        sequence_id = self.search(domain)
        if sequence_id:
            return sequence_id._generate_code()
        else:
            return False

    @api.multi
    def _generate_code(self):
        self._compute_code()
        number = self.next_number
        self.next_number += self.number_increment
        code = self.code + str(number)
        return code
