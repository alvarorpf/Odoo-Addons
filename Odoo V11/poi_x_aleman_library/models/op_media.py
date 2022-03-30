from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class OpMedia(models.Model):
    _name = 'op.media'
    _description = 'Libro'
    _inherit = ['op.media', 'mail.thread', 'mail.activity.mixin']

    image = fields.Binary('Imagen', attachment=True)
    year_edition = fields.Integer('Año de Edición')
    media_subtype_id = fields.Many2one('op.subtype', string='Subtipo')
    cdu_code_id = fields.Many2one('op.cdu.code', string='Código CDU', required=True)
    author_type = fields.Char('Tipo (Autor)', required=True)
    data_title = fields.Char('Dato (Título)', required=True)
    color_tag = fields.Integer('Color Marbete', required=True)
    original_title = fields.Char('Título Original')
    language_ids = fields.Many2many('res.lang', string='Lenguajes', required=True)
    publisher_place_id = fields.Many2one('op.publisher.place','Lugar de Edición')
    page_number = fields.Integer('Nro de Páginas')
    translate = fields.Char('Traductor')
    ref_price = fields.Float('Precio Referencial')
    ref_currency = fields.Many2one('res.currency', 'Moneda')
    level_id = fields.Many2one('op.course.level', 'Nivel')
    count = fields.Integer('Contador de Ejemplares', default=1)
    cursos_ids = fields.Many2many('op.batch', string='Cursos')
