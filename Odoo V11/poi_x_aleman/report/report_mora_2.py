# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ReportMora2(models.Model):
    _name = "report.mora.2"
    _auto = False

    code = fields.Char('Familia')
    student = fields.Char('Alumno')
    parent = fields.Char('Responsable')
    phone = fields.Char('Telefono')
    cellphone = fields.Char('Celular')
    concept = fields.Char('Concepto')
    total = fields.Float('Total')

    def _select(self):
        select_str = """
            select  f.name as code,
                    ('[' || coalesce(s.student_code, '') || ']' || ' ' || coalesce(s.full_name, '')) as student,
                    ('[' || coalesce(f.name, '') || ']' || ' ' || coalesce(c.name, '')) as parent,
                    c.phone as phone, 
                    c.cellphone as cellphone, 
                    CASE
                        WHEN t.concept_type = 'pension' THEN 'Pension'
                        WHEN t.concept_type = 'material' THEN 'Material'
                        WHEN t.concept_type = 'due' THEN 'Mora'
                    END as concept, 
                    CASE 
                        WHEN a.amount_diff > 0 THEN a.amount_diff
                        ELSE a.amount_total
                    END as total
        """
        return select_str

    def _from(self):
        select_str = """
            from account_op_charge as a
            inner join product_product as p on a.product_id = p.id
            inner join product_template as t on p.product_tmpl_id = t.id
            inner join op_student as s on a.student_id=s.id
            inner join op_parent_contact as c on s.payment_responsable = c.id
            inner join op_family as f on s.family_code = f.id
          """
        return select_str

    def _where(self):
        select_str = """
            where a.state in ('wait','send') and a.amount_diff > 0 or a.amount_total > 0
            order by total desc
          """
        return select_str

    @api.model_cr
    def init(self):
        table = "report_mora_2"
        self.env.cr.execute("""
                DROP VIEW IF EXISTS report_mora_2;
                CREATE OR REPLACE VIEW report_mora_2 as (
                SELECT row_number() over() as id, *
                    FROM(
                    %s 
                    %s
                    %s) as asd
                )""" % (self._select(), self._from(), self._where()))
