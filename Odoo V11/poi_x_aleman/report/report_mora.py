#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class ReportReportMora(models.AbstractModel):
    _name = 'report.poi_x_aleman.report_mora'

    @api.multi
    def get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('poi_x_aleman.report_mora')
        domain = []
        if data.get('type', False) == 'student':
            domain.append(['student_id', '=', data.get('student_id')[0]])
        elif data.get('type', False) == 'code':
            domain.append(['family_code', '=', data.get('code_family_id')[1]])
        elif data.get('type', False) == 'parent':
            domain.append(['payment_responsable', '=', data.get('parent_id')[0]])
        if data.get('year_id', False):
            domain.append(['year_id', '=', data.get('year_id')[0]])
        domain.append(['state', 'in', ['wait', 'send']])
        charges_ids = self.env[report.model].search(domain)
        charges_ids = sorted(charges_ids, key=lambda r: r.amount_total or r.amount_diff, reverse=True)
        charges = {}
        if charges_ids:
            for c in charges_ids:
                if c.amount_diff > 0 or c.amount_total > 0:
                    if c.student_id.id in charges:
                        pension = charges[c.student_id.id]['pension']
                        material = charges[c.student_id.id]['material']
                        due = charges[c.student_id.id]['due']
                        if c.product_id.concept_type == 'pension':
                            pension = pension + (c.amount_diff or c.amount_total)
                        elif c.product_id.concept_type == 'material':
                            material = material + (c.amount_diff or c.amount_total)
                        elif c.product_id.concept_type == 'due':
                            due = due + (c.amount_diff or c.amount_total)
                        charges[c.student_id.id].update({
                            'pension': pension,
                            'material': material,
                            'due': due,
                            'total': charges[c.student_id.id]['total'] + (c.amount_diff or c.amount_total)
                        })
                    else:
                        pension = 0
                        material = 0
                        due = 0
                        if c.product_id.concept_type == 'pension':
                            pension = pension + (c.amount_diff or c.amount_total)
                        elif c.product_id.concept_type == 'material':
                            material = material + (c.amount_diff or c.amount_total)
                        elif c.product_id.concept_type == 'due':
                            due = due + (c.amount_diff or c.amount_total)
                        charges.update({
                            c.student_id.id: {
                                'code': c.family_code,
                                'name': c.student_id.name,
                                'parent': c.payment_responsable.name,
                                'phone': str(c.payment_responsable.phone or '') + ' - ' + str(c.payment_responsable.cellphone or ''),
                                'pension': pension,
                                'material': material,
                                'due': due,
                                'total': c.amount_diff or c.amount_total
                            }
                        })
        prec = self.env['decimal.precision'].precision_get('Product Price')

        return {
            'doc_ids': self.env.user.id,
            'doc_model': report.model,
            'docs': self.env.user,
            'charges': charges,
            'prec': prec,
            'year_id': data.get('year_id', False),
            'date': data.get('date', False),
        }
