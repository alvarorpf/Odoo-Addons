from odoo import models, fields, api
from datetime import date, datetime


class ReportAccountWiz(models.TransientModel):
    _name = "report.account.wizard"

    family_id = fields.Many2one('op.family', 'Codigo de familia', required=True)
    parent_id = fields.Many2one('op.parent.contact', 'Responsable de Pago')
    year_id = fields.Many2one('op.year', 'Gestion Escolar', default=lambda self: self.env['op.school.period'].search(
        [('state', '=', 'active')]).year_id.id, required=True)
    date_from = fields.Date('Fecha de Corte', default=fields.Date.today(), help="Selecciona los cargos en la fecha de corte.", required=True)

    @api.onchange('family_id')
    def get_parents(self):
        for r in self:
            parents = []
            if r.family_id:
                for parent in r.family_id.parents_ids:
                    if parent.child_ids:
                        parents.append(parent.id)
            return {
                'domain': {
                    'parent_id':
                        [
                            ('id', 'in', parents)
                        ]
                }
            }

    @api.multi
    def action_view_report(self):
        data = self.read()[0]
        return self.env.ref('poi_x_aleman.report_account_report_2_template').report_action(self, data=data)
