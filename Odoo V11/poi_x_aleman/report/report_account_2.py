#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
import datetime

class ReportReportMora(models.AbstractModel):
    _name = 'account.report.2'
    _auto = False

    date = fields.Date('')
    name = fields.Char('')
    pension = fields.Float('')
    other = fields.Float('')
    pago = fields.Float('')
    responsable_id = fields.Many2one('res.partner')
    invoice = fields.Integer('')
    bank_id = fields.Many2one('res.bank')
    family_id = fields.Many2one('op.family')
    student_id = fields.Many2one('op.student')
    year_id = fields.Many2one('op.year')
    month_id = fields.Many2one('op.month')
    type = fields.Char()
    concept = fields.Char('')
    state = fields.Char('')
    payed = fields.Float('')

    def _select(self):
        select_str = """
        (select 
            a.date as date, 
            a.name as name,
            case
                when t.concept_type = 'pension' and t.charge_type = 'charge' then a.amount_total
            end as pension,
            case
                when t.concept_type != 'pension' and t.charge_type = 'charge' then a.amount_total
            end as other,
            case
                when t.concept_type = 'pension' and t.charge_type = 'payment' then a.amount_total
            end as pago,
            a.partner_id as responsable_id,
            Null as invoice,
            Null as bank_id,
            f.id as family_id,
            s.id as student_id,
            a.year_id as year_id,
            a.month_id as month_id,
            t.charge_type as type,
            t.concept_type as concept,
            a.state as state,
            a.amount_diff as payed
        from account_op_charge as a
        left join product_product as p on a.product_id=p.id
        left join product_template as t on p.product_tmpl_id = t.id
        left join op_family as f on a.family_id=f.id
        left join op_month as m on a.month_id = m.id
        left join op_student as s on a.student_id = s.id
        where a.state in ('wait', 'send', 'done'))
        union all
        (select 
            p.payment_date as date,
            case 
                when p.payment_date < date_trunc('year',current_date) then 'Saldo Gestion Anterior'
                else ('Pago en Banco ' || coalesce( to_char(p.payment_date,'DD/MM/YYYY')))
            end as name,
            0.00 as pension,
            0.00 as other,
            case
                when p.currency_id = 3 then p.amount
                else p.amount * usd.rate
            end as pago,
            p.partner_id as responsable_id,
            i.cc_nro as invoice,
            b.id as bank_id,
            f.id as family_id,
            Null as student_id,
            r.year_id as year_id,
            Null as month_id,
            '' as type,
            'pago' as concept,
            p.state as state,
            0 as payed
        from account_payment as p
        left join op_request_charge as r on p.charge_request_id = r.id
        left join account_invoice as i on r.invoice_id = i.id
        left join res_bank as b on r.bank_id=b.id
        left join op_family as f on r.code_family = f.id
        left outer join (
                        select 	   
                            cr.name::date as date,
                            cr.rate			
                        from res_currency_rate cr where cr.currency_id=3 order by name desc limit 1
                        ) usd on usd.date <= current_date
        where r.state = 'done')
        order by date asc
        """
        return select_str

    @api.model_cr
    def init(self):
        table = "account_report_2"
        self.env.cr.execute("""
                DROP VIEW IF EXISTS account_report_2;
                CREATE OR REPLACE VIEW account_report_2 as (
                SELECT row_number() over() as id, *
                    FROM(
                    %s) as asd
                )""" % (self._select()))


class ReportSedes(models.AbstractModel):
    _name = 'report.poi_x_aleman.report_account_2_template'

    @api.multi
    def get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('poi_x_aleman.report_account_2_template')
        #parent_id = self.env['op.parent.contact'].search([('id', '=', data['parent_id'][0])])
        year_id = self.env['op.year'].search([('id', '=', data['year_id'][0])])
        family_id = self.env['op.family'].search([('id', '=', data['family_id'][0])])
        docs = []
        if family_id:
            docs = self.env[report.model].search([('year_id', '=', year_id.id), ('family_id', '=', family_id.id)])
        prec = self.env['decimal.precision'].precision_get('Product Price')
        first_day = datetime.date(datetime.datetime.now().year, 1, 1)
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'data': data,
            'family_id': family_id or False,
            'year_id': year_id or False,
            'prec': prec,
            'first_day': first_day
        }
