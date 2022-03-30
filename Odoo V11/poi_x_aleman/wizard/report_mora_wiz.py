from odoo import models, fields, api
from datetime import date, datetime


class ReportMoraWiz(models.TransientModel):
    _name = "report.mora.wiz"

    type = fields.Selection(
        string="Tipo",
        selection=[
            ('student', 'Alumno'),
            # ('code', 'Código de Familia'),
            ('parent', 'Responsable de Pago'),
        ])
    year_id = fields.Many2one('op.year', 'Gestión')
    student_id = fields.Many2one('op.student', 'Estudiante')
    code_family_id = fields.Many2one('op.family', 'Código de Familia')
    parent_id = fields.Many2one('op.parent.contact', 'Responsable de Pago')
    date = fields.Date('Fecha de Corte', default=fields.Date.today(), help="Selecciona los cargos en la fecha de corte.", required=True)

    @api.multi
    def action_view_report(self):
        data = self.read()[0]
        return self.env.ref('poi_x_aleman.report_mora_report').report_action(self, data=data)
