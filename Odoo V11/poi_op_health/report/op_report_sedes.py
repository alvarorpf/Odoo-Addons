# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class OpReportSedes(models.Model):
    _name = "op.report.sedes"
    _auto = False

    gender = fields.Char('')
    parameter = fields.Char('')
    value = fields.Char('')
    date = fields.Date('')
    age = fields.Integer('')

    def _select(self):
        select_str = """
            select  os.gender as gender, 
                    orp.name as parameter,
                    ovrp.name as value,
                    ocr.datetime_arrival::DATE as date,
                    os.age as age
        """
        return select_str

    def _from(self):
        select_str = """
            from op_clinical_record as ocr
            inner join op_student as os on ocr.student_id=os.id
            inner join op_clinical_report_parameters as ocrp on ocr.id=ocrp.id 
            inner join op_report_parameters as orp on ocrp.parameter_id=orp.id 
            inner join op_value_report_parameters as ovrp on ocrp.value_id=ovrp.id
          """
        return select_str

    def _where(self):
        select_str = """
            where ocr.type = 'student'
          """
        return select_str

    def _group_by(self):
        select_str = """
            group by gender,parameter,value, date
          """
        return select_str

    @api.model_cr
    def init(self):
        table = "op_report_sedes"
        self.env.cr.execute("""
                DROP VIEW IF EXISTS op_report_sedes;
                CREATE OR REPLACE VIEW op_report_sedes as (
                SELECT row_number() over() as id, *
                    FROM(
                    %s 
                    %s
                    %s) as asd
                )""" % (self._select(), self._from(), self._where()))


class ReportSedes(models.AbstractModel):
    _name = 'report.poi_op_health.op_report_sedes_template'

    @api.multi
    def get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('poi_op_health.op_report_sedes_template')
        docs = self.env[report.model].search([('date', '>=', data['start_date']), ('date', '<=', data['end_date'])])
        params = self.env['op.report.parameters'].search([])
        vals = self.env['op.value.report.parameters'].search([])
        parameters = {}
        for p in params:
            if p.name not in parameters:
                parameters[p.name] = {'param': p.name}
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'data': data,
            'values': vals,
            'parameters': parameters,
        }
