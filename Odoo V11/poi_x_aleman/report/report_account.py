#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class ReportReportMora(models.AbstractModel):
    _name = 'report.poi_x_aleman.report_account'

    @api.multi
    def get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        payment_obj = self.env['account.payment']
        report = report_obj._get_report_from_name('poi_x_aleman.report_account')
        domain = []
        if data.get('type', False) == 'student':
            domain.append(['student_id', '=', data.get('student_id')[0]])
            student_id = self.env['op.student'].browse(data.get('student_id')[0])
            partner_id = student_id.payment_responsable.partner_id
        elif data.get('type', False) == 'code':
            domain.append(['family_code', '=', data.get('code_family_id')[1]])
        elif data.get('type', False) == 'parent':
            domain.append(['payment_responsable', '=', data.get('parent_id')[0]])
            contact_id = self.env['op.parent.contact'].browse(data.get('parent_id')[0]).payment_responsable.partner_id
            partner_id = contact_id.partner_id

        if data.get('year_id', False):
            domain.append(['year_id', '=', data.get('year_id')[0]])
        domain.append(['date', '>=', data.get('date_from')])
        domain.append(['date', '<=', data.get('date_to')])
        domain.append(['state', 'in', ['wait', 'send', 'done']])
        charges_ids = self.env[report.model].search(domain)
        payment_ids = payment_obj.search([('partner_id', '=', partner_id.id), ('state', '=', 'posted')])
        data = []
        for c in charges_ids:
            pension = 0
            otros = 0
            if c.product_id.concept_type == 'pension':
                pension = c.amount_total
            else:
                otros = c.amount_total
            data.append({
                c.date: {
                    'bank_id': False,
                    'invoice_id': False,
                    'name': c.name,
                    'pesion': pension,
                    'otros': otros,
                    'pays': 0,
                }   
            })
        for p in payment_ids:
            pension = 0
            otros = 0
            data.append({
                p.payment_date: {
                    'bank_id': False,
                    'invoice_id': False,
                    'name': 'Pago',
                    'pesion': 0,
                    'otros': 0,
                    'pays': p.amount,
                }   
            })
        data = dict(sorted(data.items()))
        prec = self.env['decimal.precision'].precision_get('Product Price')
        return {
            'doc_ids': self.env.user.id,
            'doc_model': report.model,
            'docs': self.env.user,
            'data': data,
            'prec': prec,
            'year_id': False,
            'date_from': data.get('date_from', False),
            'date_to': data.get('date_to', False),
        }
