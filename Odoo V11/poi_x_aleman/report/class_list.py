import time
from odoo import models, api, fields
from datetime import datetime


class ReportLibraryCardBarcode(models.AbstractModel):
    _name = 'report.poi_x_aleman.class_list'

    @api.model
    def get_report_values(self, docids, data=None):
        docs = self.env['op.course'].browse(docids)
        case = self.env.ref('poi_x_aleman.student_case_active_4').id
        clases = []
        for d in docs:
            clase = {}
            students = self.env['op.student'].search([('class_id', '=', d.id), ('state', '=', 'activo'), ('case_id', '=', case)], order='last_name')
            clase['responsable'] = d.course_responsable_1
            clase['clase'] = d.course_id
            clase['students'] = students
            clase['year'] = d.year_id
            clases.append(clase)
        date = fields.Datetime.context_timestamp(self,datetime.now())
        fecha = str(date.day)+'/'+str(date.month)+'/'+str(date.year)
        hora = str(date.hour)+':'+str(date.minute)
        docargs = {
            'doc_model': 'op.course',
            'docs': clases,
            'fecha': fecha,
            'hora': hora,
        }
        return docargs
