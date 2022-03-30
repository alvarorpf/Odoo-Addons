# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import datetime
SELECTION = [
    ('b', 'Bueno'),
    ('r', 'Regular'),
    ('m', 'Malo')]


class SecurityInspection(models.Model):
    _name = "security.inspection"

    name = fields.Char("Nombre", default="Nuevo")
    state = fields.Selection([('draft', 'Borrador'), ('finished', 'Completado')], string="Estado", default='draft')
    task_id = fields.Many2one('project.task', 'Tarea')
    project_id = fields.Many2one('project.project', "Centro de costo")
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company.id)
    date = fields.Date('Fecha', default=datetime.date.today())
    type = fields.Selection([('inspection', 'Inspeccion'), ('observation', 'Observacion')], string='Tipo de Inspeccion')
    datetime = fields.Datetime('Fecha y Hora', default=datetime.datetime.now())
    planned_hours = fields.Float("Tiempo Ocupado")
    inspector = fields.Char('Inspeccionado Por')
    charge = fields.Char('Cargo')

    order = fields.Selection(SELECTION, string="Orden")
    clean = fields.Selection(SELECTION, string="Aseo")
    storage = fields.Selection(SELECTION, string="Almacenamiento")
    tools = fields.Selection(SELECTION, string="Herramientas")
    escape = fields.Selection(SELECTION, string="Vias de Evacuacion")
    signals = fields.Selection(SELECTION, string="Señaleticas")
    protect = fields.Selection(SELECTION, string="Protecciones")
    condition = fields.Selection(SELECTION, string="Condiciones Ambientales")
    machine = fields.Selection(SELECTION, string="Maquinas")
    protection = fields.Selection(SELECTION, string="Proteccion Incendios")
    surface = fields.Selection(SELECTION, string="Superficies")
    illumination = fields.Selection(SELECTION, string="Iluminacion")
    ergonomic = fields.Selection(SELECTION, string="Ergonomia")
    infrastructure = fields.Selection(SELECTION, string="Infraestructura")
    circulation = fields.Selection(SELECTION, string="Vias de Circulacion")
    other = fields.Selection(SELECTION, string="Otros")

    line_ids = fields.One2many('security.inspection.line', 'form_id', 'Lineas de formulario')

    signature = fields.Binary('Firma', copy=False)

    @api.model
    def create(self, vals):
        res = super(SecurityInspection, self).create(vals)
        if res.name == 'Nuevo':
            sequence = self.env['ir.sequence'].search([('code', '=', 'sequence.security.inspection.form')])
            res.name = sequence.next_by_id() or _('Nuevo')
        return res

    def action_confirm(self):
        for r in self:
            if not r.signature:
                raise UserError(_("Debe registrar la firma correspondiente del documento."))
            r.state = 'finished'
            if r.task_id:
                content, content_type = self.env.ref('project_task_form.action_report_security_inspection')._render(r.id)
                self.env['ir.attachment'].create({
                    'name': r.task_id.name and _(r.name + " - %s.pdf", r.task_id.name) or _(
                        "Formulario Inspeccion de Seguridad.pdf"),
                    'type': 'binary',
                    'datas': base64.encodebytes(content),
                    'res_model': r.task_id._name,
                    'res_id': r.task_id.id
                })

    class SecurityInspectionLine(models.Model):
        _name = "security.inspection.line"

        form_id = fields.Many2one('security.inspection', 'Formulario de Inspeccion')
        condition = fields.Char('Condicion Detectada')
        probability = fields.Selection([('b', 'Baja'), ('m', 'Media'), ('a', 'Alta')], string="Probabilidad")
        gravity = fields.Selection([('l', 'Ligeramente Dañino'), ('d', "Dañino"), ('e', 'Extremadamente Dañino')], string='Gravedad')
        risk = fields.Selection([('tr', 'Trivial'), ('to', 'Tolerable'), ('mo', 'Moderado'), ('im', 'Importante'), ('in', 'Intolerable')], string='Riesgo')
        action = fields.Char('Accion Correctiva')
        responsible = fields.Char('Responsable')
        date = fields.Date('Fecha Limite', required=True, default=datetime.date.today())




