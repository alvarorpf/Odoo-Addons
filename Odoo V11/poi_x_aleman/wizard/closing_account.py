# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime


class ClosingAccount(models.TransientModel):
    _name = "closing.account.wiz"

    account_id = fields.Many2one('account.account')

    @api.multi
    def closing_account(self):
        student_obj = self.env['op.student']
        charge_obj = self.env['account.op.charge']
        payment_obj = self.env['op.request.charge']
        student_ids = student_obj.search([('state', '=', 'activo')])
        adelantos = {}
        count = 0
        for s in student_ids:
            missing_charges = charge_obj.search([('student_id', '=', s.id), ('state', 'in', ['wait'])])
            paid_charge = payment_obj.search([('code_family', '=', s.family_code.id), ('state', '=', 'done')],
                                             order='id desc')
            if missing_charges:
                if paid_charge:
                    paid = paid_charge[0]
                else:
                    charges = []
                    charges_to_check = []
                    for charge in missing_charges:
                        charge_line = {
                            'check': True,
                            'charge_id': charge.id,
                            'product_id': charge.product_id and charge.product_id.id or False,
                            'date': charge.date,
                            'date_due': charge.date_due,
                            'type': charge.product_id and charge.product_id.concept_type or False,
                            'amount_untaxed': charge.amount_untaxed,
                            'amount_tax': charge.amount_tax,
                            'amount_total': charge.amount_total,
                        }
                        charges.append((0, 0, charge_line))
                        charges_to_check.append(charge.id)
                        student_id = charge.student_id.id
                        code_family = charge.family_id.id
                        responsable = charge.student_id.payment_responsable
                        year_id = charge.year_id.id
                        currency_id = charge.currency_id.id
                        charge.invoiced = False
                    request_charges = payment_obj.create({
                        'student_id': student_id,
                        'code_family': code_family,
                        'responsable_id': responsable.id,
                        'year_id': year_id,
                        'currency_id': currency_id,
                        'date': fields.datetime.now().date(),
                        'date_due': fields.datetime.now().date(),
                    })
                    request_charges.onchange_student_id()
                    request_charges._compute_partner_id()
                    request_charges._compute_currency_id()
                    for line in request_charges.line_ids:
                        if line.charge_id.id in charges_to_check:
                            line.write({'check': True})
                    request_charges._compute_amount_total()
                    request_charges.invoiced = True
                    request_charges.action_confirm_charge()
                    if request_charges.invoice_id:
                        request_charges.invoice_id._onchange_partner_id()
                        request_charges.invoice_id.action_invoice_open()

                    count = count + 1
            else:
                if paid_charge:
                    paid = paid_charge[0]
                    advanced_ids = paid.advanced_ids
                    for a in advanced_ids:
                        if a.student_id.id == s.id:
                            adelantos.update({
                                a.student_id.id: {'adelanto': a.amount}
                            })
                            if a.amount_rest > 0:
                                advanceds = []
                                advanced = {
                                    'student_id': s.id,
                                    'type': 'pension',
                                    'amount_type': a.amount_rest,
                                }
                                advanceds.append((0, 0, advanced))
                                date = datetime(fields.datetime.now().year, 12, 31).date()
                                request_id = payment_obj.create({
                                    'student_id': s.id,
                                    'code_family': s.family_code.id,
                                    'responsable_id': s.payment_responsable.id,
                                    'year_id': paid.year_id.get_next_year().id,
                                    'date': date,
                                    'date_due': date,
                                    'advanced_ids': advanceds
                                })
                                request_id.write({'currency_id': paid.currency_id.id})
                                request_id.invoiced = False
                                request_id._compute_amount_total()
                                request_id.action_confirm_charge()
                                journal_id = self.env['account.journal'].search(
                                    [('company_id', '=', self.env.user.company_id.id)], limit=1)
                                payment = self.env['account.payment'].create({
                                    'payment_type': 'inbound',
                                    'partner_type': 'customer',
                                    'payment_date': date,
                                    'journal_id': journal_id.id,
                                    'payment_method_id': journal_id.inbound_payment_method_ids and
                                                         journal_id.inbound_payment_method_ids[0].id or False,
                                    'amount': request_id.amount_total,
                                    'charge_request_id': request_id.id,
                                    'partner_id': request_id.partner_id.id,
                                    'currency_id': journal_id.currency_id.id or self.journal_id.company_id.currency_id.id,
                                    'communication': 'Adelanto de Pensiones',
                                })
                                payment.post()
                                request_id.write({'payment_id': payment.id})
                                count = count + 1

            if count >= 20:
                self.env.cr.commit()
                count = 0
            count = count + 1
