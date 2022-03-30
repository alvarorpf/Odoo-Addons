# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class OpParent(models.Model):
    _name = 'op.parent.contact'

    image = fields.Binary('Imagen', attachment=True)
    family_id = fields.Many2many('op.family', string='Codigo Familia', required=True)
    name = fields.Char('Nombre', required=True)
    #relationship_id = fields.Many2one('op.relationship', 'Parentesco', required=True)

    # Datos Generales
    first_nationality = fields.Many2one('res.country', '1ra Nacionalidad')
    second_nationality = fields.Many2one('res.country', '2da Nacionalidad')
    mother_language = fields.Selection(selection='_get_languages', string='Idioma Materno')
    religion = fields.Many2one('op.religion', 'Religion')
    family_tag_id = fields.Many2many('op.family.tag', string="Etiqueta Familiar")

    # Otra Informacion
    ex_student = fields.Boolean('Ex-Estudiante')
    clase = fields.Char('Clase')
    birthdate = fields.Date('Fecha de Nacimiento')

    # Datos de Identificacion
    ci = fields.Char('CI')
    issued_ci = fields.Selection(
        [('lp', 'LP'), ('sc', 'SC'), ('ben', 'BE'), ('cb', 'CB'), ('ch', 'CH'), ('or', 'OR'), ('pa', 'PA'),
         ('po', 'PT'), ('tj', 'TJ'), ('ex', 'Extranjero')])
    extension_ci = fields.Char('')
    passport = fields.Char('Pasaporte')
    foreign_id = fields.Char('ID Extranjero')
    nit = fields.Char('NIT', help=u"Número de Identificación Tributaria (o CI para facturación).")

    # Datos de Contacto
    phone = fields.Char('Telefono')
    cellphone = fields.Char('Celular')
    email = fields.Char('Email')

    # Datos de Labores
    profession_id = fields.Many2one('op.profession', 'Profesion')
    workplace = fields.Char('Lugar de Trabajo')
    job = fields.Char('Puesto de Trabajo')
    work_phone = fields.Char('Telefono de Trabajo')
    work_cellphone = fields.Char('Celular de Trabajo')
    work_email = fields.Char('Email de Trabajo')

    # Detale de Direccion
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state', 'Departamento')
    zone = fields.Char()
    country_id = fields.Many2one('res.country', 'Pais')

    child_ids = fields.One2many('op.student', 'payment_responsable', 'Responsable de Pago')

    color = fields.Integer('Color', compute='_compute_color')
    razon = fields.Char('Razon Social')
    partner_id = fields.Many2one('res.partner', 'Contacto', store=True)

    @api.model
    def create(self, values):
        record = super(OpParent, self).create(values)
        record.create_contact()
        return record

    @api.multi
    def unlink(self):
        for parent in self:
            raise ValidationError(_("No puede eliminar un familiar del sistema."))
            return models.Model.unlink(self)

    @api.onchange('family_tag_id')
    def _compute_color(self):
        for record in self:
            if record.family_tag_id:
                for r in record.family_tag_id:
                    record.color = r.color

    @api.multi
    def create_contact(self):
        contact = self.env['res.partner']
        for r in self:
            contact = contact.create(
                {
                    'name': r.name,
                    'ci': r.ci,
                    'ci_dept': r.issued_ci,
                    'extension': r.extension_ci,
                    'phone': r.phone,
                    'mobile': r.cellphone,
                    'email': r.email,
                    'razon': r.razon,
                    'street': r.street,
                    'street2': r.street2,
                    'city': r.city,
                    'nit': r.nit,
                    'state_id': r.state_id.id or False,
                    'country_id': r.country_id.id or False
                })
            r.write({'partner_id': contact.id})

    @api.model
    def _get_languages(self):
        langs = self.env['res.lang'].search([('translatable', '=', True)])
        return [(lang.code, lang.name) for lang in langs]

    @api.multi
    def _update_contacts(self):
        parents = self.env['op.parent.contact'].search([('partner_id', '=', False)])
        for parent in parents:
            if not parent.partner_id:
                parent.create_contact()

    @api.onchange('state_id')
    def __get_country(self):
        if self.state_id:
            self.country_id = self.state_id.country_id.id

    @api.onchange('country_id')
    def _get_states(self):
        return {
            'domain': {
                'state_id':
                    [
                        ('country_id', '=', (self.country_id and self.country_id.id) or False)
                    ]
            }
        }

    @api.onchange('name', 'ci', 'issued_ci', 'extension_ci', 'phone', 'cellphone', 'email', 'razon', 'job', 'street', 'street2', 'city', 'nit', 'state_id', 'country_id')
    def _onchange_info(self):
        for r in self:
            if r.partner_id:
                r.partner_id.write({
                    'name': r.name,
                    'ci': r.ci,
                    'ci_dept': r.issued_ci,
                    'extension': r.extension_ci,
                    'phone': r.phone,
                    'mobile': r.cellphone,
                    'email': r.email,
                    'razon': r.razon,
                    'street': r.street,
                    'street2': r.street2,
                    'city': r.city,
                    'nit': r.nit,
                    'state_id': r.state_id.id or False,
                    'country_id': r.country_id.id or False
                })




