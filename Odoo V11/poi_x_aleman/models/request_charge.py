# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
import odoo.addons.decimal_precision as dp
import re


class OpRequestCharge(models.Model):
    _name = "op.request.charge"
    _order = "create_date desc"

    @api.depends('line_ids.check', 'advanced_ids')
    @api.multi
    def _compute_amount_total(self):
        for s in self:
            s.amount_total = 0
            s.pension_amount_total = 0
            s.pension_amount_total_kinder = 0
            s.pension_amount_total_comercio = 0
            s.amount_untaxed = 0
            kinder = self.env.ref('poi_x_aleman.student_case_active_5').id
            com1 = self.env.ref('poi_x_aleman.student_case_active_6').id
            com2 = self.env.ref('poi_x_aleman.student_case_active_7').id
            for l in s.line_ids.filtered(lambda x: x.check is True):
                s.amount_total += l.charge_id.amount_diff
                s.amount_tax += l.charge_id.amount_tax
                s.amount_untaxed += l.charge_id.amount_untaxed
                if l.type == 'pension':
                    if l.student_id.case_id.id == kinder:
                        s.pension_amount_total_kinder += l.charge_id.amount_diff
                    elif l.student_id.case_id.id in [com1, com2]:
                        s.pension_amount_total_comercio += l.charge_id.amount_diff
                    else:
                        s.pension_amount_total += l.charge_id.amount_diff
                if l.type == 'material':
                    s.material_amount_total += l.charge_id.amount_diff
                if l.type == 'due':
                    s.due_amount_total += l.charge_id.amount_diff
            for a in s.advanced_ids:
                s.amount_total += a.amount
                if a.type == 'pension':
                    if a.student_id.case_id.id == kinder:
                        s.pension_amount_total_kinder += a.amount
                    elif a .student_id.case_id.id in [com1, com2]:
                        s.pension_amount_total_comercio += a.amount
                    else:
                        s.pension_amount_total += a.amount
                if a.type == 'material':
                    s.material_amount_total += a.amount
                if a.type == 'due':
                    s.due_amount_total += a.amount

    @api.multi
    @api.depends('responsable_id')
    def _compute_partner_id(self):
        for s in self:
            if s.responsable_id:
                if s.responsable_id.partner_id:
                    s.partner_id = s.responsable_id.partner_id.id
                else:
                    raise Warning(
                        'Atención! Necesita que el Responsable de Pago del Estudiante tenga parametrizado un contacto en su dato maestro.')

    @api.multi
    @api.depends('year_id')
    def _compute_currency_id(self):
        period_obj = self.env['op.school.period']
        for s in self:
            if s.year_id:
                period_ids = period_obj.search([('year_id', '=', s.year_id.id)])
                if period_ids:
                    period_id = period_ids[0]
                    s.currency_id = period_id.currency_id.id
                    s.period_id = period_id.id

    name = fields.Char(string='Nro.', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    # student_id = fields.Many2one('op.student', 'Alumno', readonly=True, states={'draft': [('readonly', False)]}, required=True)
    responsable_id = fields.Many2one('op.parent.contact', 'Responsable de Pago', readonly=True, states={'draft': [('readonly', False)]})
    code_family = fields.Many2one('op.family', 'Código de Familia', readonly=True, states={'draft': [('readonly', False)]})
    student_code = fields.Char('Código de Alumno', readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date('Fecha', default=fields.Datetime.now, readonly=True, states={'draft': [('readonly', False)]},
                       required=True)
    date_due = fields.Date('Fecha de Vencimiento', default=fields.Datetime.now, readonly=True,
                           states={'draft': [('readonly', False)]}, required=True)
    year_id = fields.Many2one('op.year', 'Gestion Escolar', default=lambda self: self.env['op.school.period'].search(
        [('state', '=', 'active')]).year_id.id)
    period_id = fields.Many2one('op.school.period', 'Periodo', compute="_compute_currency_id", store=True,
                                readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one("res.currency", "Moneda", compute="_compute_currency_id", store=True, readonly=True,
                                  states={'draft': [('readonly', False)]})
    invoice_id = fields.Many2one('account.invoice', 'Factura')
    payment_id = fields.Many2one('account.payment', 'Pago')
    amount_untaxed = fields.Float("Base Imponible", compute="_compute_amount_total", store=True)
    amount_tax = fields.Float("Impuestos", compute="_compute_amount_total", store=True)
    amount_total = fields.Float('Monto Total', compute="_compute_amount_total", store=True)
    partner_id = fields.Many2one('res.partner', 'Contacto', compute="_compute_partner_id")

    line_ids = fields.One2many('op.request.charge.line', 'request_id', 'Cargos')
    pension_ids = fields.One2many('op.request.pension.line', 'request_id', 'Pensiones Pagadas', readonly=True)
    group_ids = fields.One2many('op.request.group', 'request_id', 'Grupos')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirm', 'Confirmado'),
        ('done', 'Pagado'),
        ('cancel', 'Cancelado'),
        ('web_service', 'Servicio Web'),
    ], string="Estado", default="draft")
    # pension = fields.Boolean("Pensiones", default=False)
    # pension_amount_pay = fields.Float("Monto a Pagar Pension", default=0)
    pension_amount_untaxed = fields.Float("Pension Base Imponible", default=0, digits=dp.get_precision('Servicios_Web'))
    pension_amount_tax = fields.Float("Pension Impuesto", default=0, digits=dp.get_precision('Servicios_Web'))
    pension_amount_total = fields.Float("Pension Deuda Total", default=0, computed="_compute_amount_total", store=True, digits=dp.get_precision('Servicios_Web'))
    pension_amount_total_kinder = fields.Float("Pension Deuda Total Kinder", default=0, computed="_compute_amount_total", store=True, digits=dp.get_precision('Servicios_Web'))
    pension_amount_total_comercio = fields.Float("Pension Deuda Total Comercio", default=0, computed="_compute_amount_total", store=True, digits=dp.get_precision('Servicios_Web'))
    material_amount_total = fields.Float('Monto Total Material', computed="_compute_amount_total", store=True, digits=dp.get_precision('Servicios_Web'))
    due_amount_total = fields.Float('Monto Total Mora', computed="_compute_amount_total", store=True, digits=dp.get_precision('Servicios_Web'))
    amount_rest = fields.Float('Monto total Abierto')
    bank_id = fields.Many2one('res.bank', 'Banco')
    invoiced = fields.Boolean('Facturar', default=True)
    advanced_ids = fields.One2many('op.request.advanced', 'request_id', 'Adelantos y Saldos')
    web_service = fields.Boolean('Servicio Web', default=True)
    transaction_number = fields.Char('Numero de Transaccion')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('op.request.charge') or _('New')
        result = super(OpRequestCharge, self).create(vals)
        return result

    @api.onchange('code_family')
    def onchange_student_id(self):
        bob_currency_id = self.env.ref('base.BOB')
        if self.code_family:
            period_ids = self.env['op.school.period'].search([('state', '=', 'active')])
            if not len(period_ids) > 0:
                raise Warning("No existe una Gestión Escolar en estado 'Activo'")
            self.year_id = period_ids[0].year_id.id
            charge_obj = self.env['account.op.charge']
            charge_ids = charge_obj.search(
                [('student_id.family_code', '=', self.code_family.id), ('state', '=', 'wait')])
            data = []
            pension_amount = 0
            material_amount_total = 0
            due_amount_total = 0
            self.line_ids = False
            self.advanced_ids = False
            invoiced = True
            self.responsable_id = self.code_family.parents_ids.filtered(lambda x: x.child_ids).ids[0]
            data2 = []
            data3 = []
            ndata = []
            type2 = ['pension', 'due', 'material']
            student_ids2 = self.env['op.student'].search(
                [('family_code', '=', self.code_family.id), ('state', '=', 'activo')])
            student_ids3 = student_ids2
            student_ids = charge_ids.mapped('student_id')
            for c in charge_ids:
                if c.product_id.concept_type != 'pension':
                    data.append([0, 0, {
                        'charge_id': c.id,
                    }])
                elif c.product_id.concept_type == 'pension':
                    pension_amount += c.amount_diff
                    data.append([0, 0, {
                        'charge_id': c.id,
                    }])
                if not c.invoiced:
                    invoiced = False
            for s in student_ids2:
                for t in type2:
                    total = 0
                    cids = ''
                    c22 = charge_ids.filtered(lambda x: x.student_id.id == s.id and x.product_id.concept_type == t)
                    for c2 in c22:
                        c2._compute_amount_diff()
                        total += c2.amount_diff
                        stundent_id = c2.student_id.id
                        cids = cids + str(c2.id) + ','
                    if c22:
                        data2.append([0, 0, {
                            'student_id': stundent_id,
                            'type': t,
                            'amount_bs': self.currency_id.compute(total, bob_currency_id),
                            'amount_sus': total,
                            'cids': cids[:-1]
                        }])
                    elif t == 'pension' and not c22:
                        data2.append([0, 0, {
                            'student_id': s.id,
                            'type': 'pension',
                            'amount_bs': 0,
                            'amount_sus': 0,
                            'cids': False,
                        }])
            for s in student_ids3:
                data3.append([0, 0, {
                    'student_id': s.id,
                    'type': 'pension',
                }])
            if not self.group_ids:
                flag = False
            else:
                for g in self.group_ids:
                    g.amount_bs = 0
                    g.amount_sus = 0
                    g.cids = ''
                flag = True

            for d2 in data2:
                d = d2[2]
                g_id = self.group_ids.filtered(lambda x: x.student_id.id == d['student_id'] and x.type == d['type'])
                if g_id:
                    g_id.amount_bs = d['amount_bs']
                    g_id.amount_sus = d['amount_sus']
                    g_id.cids = d['cids']
                else:
                    ndata.append(d2)
            g_ids = self.group_ids.filtered(lambda x: x.amount_bs == 0 and x.amount_sus == 0 and x.type != 'pension')
            if g_ids and flag:
                g_ids.unlink()
            self.invoiced = invoiced
            self.line_ids = data
            self.line_ids._compute_charge_id()
            self.line_ids._compute_charge_id2()
            self.group_ids = ndata
            self.advanced_ids = data3

    @api.multi
    def action_confirm_charge(self):
        for s in self:
            # if s.pension and s.pension_amount_pay > s.pension_amount_total:
            #     raise Warning("Pensiones, No se puede Pagar un Monto Mayor al de la Deuda.")
            s._compute_amount_total()
            if not s.amount_total > 0:
                raise Warning("Debe seleccionar al menos un cargo a pagar o realizar algun adelanto")
            s.generate_payment(s)
            if s.invoiced:
                data = s.prepare_data_invoice()
                s.invoice_id = s.create_invoice(data)
                s.action_update_state_charge()
            s.state = 'confirm'
        return

    @api.multi
    def generate_payment(self, request_id=False):
        period_id = self.env['op.school.period'].search([('state', '=', 'active')])
        paid_obj = self.env['op.request.charge']
        charge_obj = self.env['account.op.charge']
        date = ""
        if period_id:
            count = 1
            for c in period_id.charge_ids:
                if c.auto:
                    if count == 2:
                        date = c.date
                    count = count + 1
        if fields.datetime.strptime(request_id.date, '%Y-%m-%d').date() < fields.datetime.strptime(date, '%Y-%m-%d').date():
            if request_id and date:
                paids = paid_obj.search(
                    [('state', '=', 'done'), ('year_id', '=', period_id.year_id.id), ('date', '<', date),
                     ('code_family', '=', request_id.code_family.id)])
                adelantos = {}
                if paids:
                    for p in paids:
                        prepaids = p.advanced_ids
                        for pr in prepaids:
                            if pr.student_id.id in adelantos:
                                adelantos[pr.student_id.id].update({
                                    'adelanto': adelantos[pr.student_id.id]['adelanto'] + pr.amount_rest,
                                    'paid': pr
                                })
                            else:
                                adelantos.update({
                                    pr.student_id.id: {
                                        'adelanto': pr.amount_rest,
                                        'student': pr.student_id,
                                        'paid': pr,
                                    }
                                })
                advanced_ids = request_id.advanced_ids
                for ad in advanced_ids:
                    if ad.student_id.id in adelantos:
                        adelantos[ad.student_id.id].update({
                            'adelanto': adelantos[ad.student_id.id]['adelanto'] + ad.amount,
                            'paid': ad,
                        })
                    else:
                        adelantos.update({
                            ad.student_id.id: {
                                'adelanto': ad.amount,
                                'student': ad.student_id,
                                'paid': ad,
                            }
                        })
                for a in adelantos:
                    student = adelantos[a]['student']
                    amount = adelantos[a]['adelanto']
                    paid = adelantos[a]['paid']
                    if student.first_pension:
                        total = (student.first_pension * 10) - 50
                        if not student.scholarship_id:
                            if not student.prepaid:
                                if amount >= total:
                                    month_obj = self.env['op.month']
                                    date = fields.datetime.now()
                                    month_ids = month_obj.search([('sequence', '=', date.month)])
                                    if month_ids:
                                        month_id = month_ids[0].id
                                    account = self.env['account.invoice.line'].get_invoice_line_account('out_invoice', period_id.product_abono_id,
                                                                             False, self.env.user.company_id)
                                    paid.amount_bono = (period_id.product_abono_id.lst_price * -1)
                                    charge = charge_obj.create({
                                        'type_charge': self.env.ref('poi_x_aleman.type_charge_pension').id,
                                        'student_id': student.id,
                                        'month_id': month_id,
                                        'year_id': period_id.year_id.id,
                                        'date': str(fields.datetime.now().date()),
                                        'date_due': str(fields.datetime.now().date()),
                                        'product_id': period_id.product_abono_id.id,
                                        'name': period_id.product_abono_id.name,
                                        'amount': period_id.product_abono_id.lst_price,
                                        'account_id': account and account.id or False,
                                        'analytic_id': student.course_id.level_id.analytic_id.id or False,
                                    })
                                    charge.onchange_product_id()
                                    line = []
                                    line.append([0, 0, {
                                        'check': True,
                                        'charge_id': charge.id,
                                    }])
                                    request_id.line_ids = line
                                    request_id._compute_amount_total()
                                    student.prepaid = True

    @api.multi
    def prepare_data_invoice(self):
        nit = False
        if self.env.context.get('nit', False):
            nit = self.env.context.get('nit').strip()
            nit = re.sub("[^0-9]", "", nit)
        invoice_line_data = []
        line_ids = self.line_ids.filtered(lambda l: l.check is True and l.type != 'pension')
        #if not line_ids and self.pension_amount_total <= 0:
        #       raise Warning("Debe seleccionar al menos un Cargo A Pagar")
        for line in line_ids:
            invoice_line_data.append([0, 0, {
                'product_id': line.charge_id.product_id.id,
                'account_analytic_id': line.charge_id.analytic_id.id,
                'quantity': 1,
                'invoice_line_tax_ids': [(6, 0, [x.id for x in line.charge_id.taxes_id])],
                'price_unit': line.amount_detail,
                'name': line.charge_id.product_id.name,
                'account_id': line.charge_id.account_id.id,
            }])

        if self.pension_amount_total:
            invoice_line_data.append([0, 0, {
                'product_id': self.period_id.product_pension_id.id,
                # 'account_analytic_id': line.charge_id.analytic_id.id,
                'quantity': 1,
                'invoice_line_tax_ids': [(6, 0, [x.id for x in self.period_id.product_pension_id.taxes_id])],
                'price_unit': self.pension_amount_total,
                'name': self.period_id.product_pension_id.name,
                'account_id': self.period_id.product_pension_id.property_account_income_id.id or self.period_id.product_pension_id.categ_id.property_account_income_categ_id.id,
                'type': 'out_invoice',
            }])
        if self.pension_amount_total_kinder:
            invoice_line_data.append([0, 0, {
                'product_id': self.period_id.product_kinder_pension_id.id,
                # 'account_analytic_id': line.charge_id.analytic_id.id,
                'quantity': 1,
                'invoice_line_tax_ids': [(6, 0, [x.id for x in self.period_id.product_kinder_pension_id.taxes_id])],
                'price_unit': self.pension_amount_total_kinder,
                'name': self.period_id.product_kinder_pension_id.name,
                'account_id': self.period_id.product_kinder_pension_id.property_account_income_id.id or self.period_id.product_kinder_pension_id.categ_id.property_account_income_categ_id.id,
                'type': 'out_invoice',
            }])
        if self.pension_amount_total_comercio:
            invoice_line_data.append([0, 0, {
                'product_id': self.period_id.product_comercio_pension_id.id,
                # 'account_analytic_id': line.charge_id.analytic_id.id,
                'quantity': 1,
                'invoice_line_tax_ids': [(6, 0, [x.id for x in self.period_id.product_comercio_pension_id.taxes_id])],
                'price_unit': self.pension_amount_total_comercio,
                'name': self.period_id.product_comercio_pension_id.name,
                'account_id': self.period_id.product_comercio_pension_id.property_account_income_id.id or self.period_id.product_comercio_pension_id.categ_id.property_account_income_categ_id.id,
                'type': 'out_invoice',
            }])
        if self.due_amount_total > 0:
            total = 0
            for d in self.advanced_ids.filtered(lambda x: x.type == 'due'):
                total += d.amount_type
            if total > 0:
                invoice_line_data.append([0, 0, {
                    'product_id': self.period_id.product_due_id.id,
                    # 'account_analytic_id': line.charge_id.analytic_id.id,
                    'quantity': 1,
                    'invoice_line_tax_ids': [(6, 0, [x.id for x in self.period_id.product_due_id.taxes_id])],
                    'price_unit': total,
                    'name': self.period_id.product_due_id.name,
                    'account_id': self.period_id.product_due_id.property_account_income_id.id or self.period_id.product_due_id.categ_id.property_account_income_categ_id.id,
                    'type': 'out_invoice',
                }])

        if self.state == 'web_service':
            date = fields.Date.today()
            date_due = date
        else:
            date = self.date
            date_due = self.date_due
        invoice_data = {
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'nit': nit or self.partner_id.nit,
            'date_invoice': date,
            'date_due': date_due,
            'invoice_line_ids': invoice_line_data,
            'charge_request_id': self.id,
            'tipo_fac': '7',
            'account_id': self.partner_id.property_account_receivable_id.id,
            # 'company_id': self.env.user.company_id.id,
        }
        return invoice_data


    @api.multi
    def action_update_state_charge(self):
        line_ids = self.line_ids.filtered(lambda l: l.check is True)
        for line in line_ids:
            line.charge_id.state = 'send'


    @api.multi
    def create_invoice(self, invoice_data):
        invoice_obj = self.env['account.invoice']
        invoice_id = invoice_obj.create(invoice_data)
        return invoice_id.id


    @api.multi
    def action_pay_charge(self):
        context = dict(self.env.context or {})
        if self.invoice_id:
            context['active_id'] = self.invoice_id.id
            context['default_amount'] = self.amount_total
            context['default_charge_request_id'] = self.id
            context['default_invoice_ids'] = [(4, self.invoice_id.id, None)]
            context['default_partner_id'] = self.partner_id.id
            context['default_currency_id'] = self.currency_id.id
            return {
                'name': _('Registrar Pago'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.payment',
                'view_id': self.env.ref('account.view_account_payment_invoice_form').id,
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new'
            }
        else:
            context['default_amount'] = self.amount_total
            context['default_charge_request_id'] = self.id
            context['default_partner_id'] = self.partner_id.id
            context['default_currency_id'] = self.currency_id.id
            return {
                'name': _('Registrar Pago'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.payment',
                'view_id': self.env.ref('account.view_account_payment_form').id,
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new'
            }


    @api.multi
    def action_done_charge(self):
        charge_obj = self.env['account.op.charge']
        for s in self:
            data = []
            line_ids = s.line_ids.filtered(lambda l: l.check is True)
            for line in line_ids:
                line.charge_id.state = 'done'
                line.charge_id.pension_amount_pay += line.amount_total
                data.append([0, 0, {
                    'charge_id': line.charge_id.id,
                    'amount_pay': line.amount_total,
                }])
            if s.pension_amount_total > 0:
                for a in s.advanced_ids.filtered(lambda l: l.amount > 0):
                    charge_ids = charge_obj.search([('student_id', '=', a.student_id.id), ('state', '=', 'wait'),
                                                    ('product_id.concept_type', '=', 'pension')], order="date asc")
                    pay_amount = a.amount
                    for c in charge_ids:
                        if c.amount_diff > pay_amount:
                            c.pension_amount_pay += pay_amount
                            if c.amount_diff == 0:
                                c.state = 'done'
                            data.append([0, 0, {
                                'charge_id': c.id,
                                'amount_pay': pay_amount
                            }])
                            pay_amount = 0
                            break
                        else:
                            diff = pay_amount - c.amount_diff
                            data.append([0, 0, {
                                'charge_id': c.id,
                                'amount_pay': c.amount_diff
                            }])
                            c.pension_amount_pay += c.amount_diff
                            c.state = 'done'
                            pay_amount = diff
                    a.amount_rest = pay_amount
            s.pension_ids = data
            s.state = 'done'

    @api.multi
    def button_validate(self):
        for s in self:
            return s.picking_id.button_validate()

    @api.model
    def service_get_charges(self, code_family):
        family_obj = self.env['op.family']
        code_family_ids = family_obj.search([('name', '=', code_family)])
        charges = []
        msg = ''
        error = False
        request_id = False
        invoiced = False
        if code_family_ids:
            code_family_id = code_family_ids[0]
            request_ids = self.search([('code_family', '=', code_family_id.id), ('state', '=', 'web_service')])
            if request_ids:
                request_id = request_ids[0]
                request_id.onchange_student_id()
                request_id._compute_partner_id()
                request_id._compute_currency_id()
            else:
                request_id = self.create({
                    'code_family': code_family_id.id,
                    'date': fields.Date.today(),
                    'date_due': fields.Date.today(),
                    'state': 'web_service',
                    # 'warehouse_id': self.env.user.shop_assigned and self.env.user.shop_assigned.id or False
                })
                request_id.onchange_student_id()
                request_id._compute_partner_id()
                request_id._compute_currency_id()
            invoiced = request_id.invoiced
            for g in request_id.group_ids:
                charges.append({
                    'cargo_id': g.id,
                    'NombreEstudiante_id': g.student_id.name,
                    'Tipo': g.type,
                    'MontoBs': g.amount_bs,
                    'MontoUs': g.amount_sus,
                })
        else:
            msg = 'Estudiante no Encontrado'
            error = True
        res = {
            'error': error,
            'mensaje': msg,
            'NombreDeudor': request_id.responsable_id.name,
            'request_id': request_id and request_id.id or False,
            'cargos': charges,
            'facturar': invoiced,
        }
        return res

    @api.model
    def service_pay_charges(self, request_id, currency, data, nr_transaccion, nit=False, razon=False, nrfactura=False, date=False, nrautorizacion=False,
                            nrcodcontrol=False):
        group_obj = self.env['op.request.group']
        request_ids = self.search([('id', '=', request_id)])
        charges = []
        msg = ''
        error = False
        bob_currency_id = self.env.ref('base.BOB')
        usd_currency_id = self.env.ref('base.USD')
        if request_ids:
            request_id = request_ids[0]
            if request_id.state == 'done':
                res = {
                    'error': True,
                    'mensaje': 'El request_id utilizado ya ha sido pagado. Solicite uno nuevo por serice_get_charges',
                    'request_id': request_id.id,
                }
                return res
            if currency == 'bs':
                currency_id = bob_currency_id
            elif currency == 'usd':
                currency_id = usd_currency_id
            else:
                currency_id = []
            period_id = self.env['op.school.period'].search([('state', '=', 'active')])
            if period_id:
                school_bank_id = self.env['op.school.bank'].search([('period_id', '=', period_id.id), ('user_id', '=', self.env.user.id), ('currency_id', '=', currency_id.id)])
            else:
                res = {
                    'error': True,
                    'mensaje': 'No se cuenta con una gestion escolar activa para realizar pagos',
                }
                return res
            if school_bank_id:
                school_bank_id = school_bank_id[0]
                payment_methods = school_bank_id.journal_id.inbound_payment_method_ids or school_bank_id.journal_id.outbound_payment_method_ids
                journal_id = school_bank_id.journal_id or False
                bank_id = school_bank_id.bank_id or False
            else:
                res = {
                    'error': True,
                    'mensaje': 'El usuario que esta utilizando no se encuentra habilitado para realizar esta operacion',
                }
                return res

            #if currency == 'usd':
            #    payment_methods = request_id.period_id.journal_usd_id.inbound_payment_method_ids or request_id.period_id.journal_usd_id.outbound_payment_method_ids
            #    journal_id = request_id.period_id.journal_usd_id or request_id.period_id.journal_usd_id.id
            #elif currency == 'bs':
            #    payment_methods = request_id.period_id.journal_bs_id.inbound_payment_method_ids or request_id.period_id.journal_bs_id.outbound_payment_method_ids
            #    journal_id = request_id.period_id.journal_bs_id or request_id.period_id.journal_bs_id.id
            #else:
            #    payment_methods = []
            #    journal_id = []
            request_id.onchange_student_id()
            request_id._compute_partner_id()
            request_id._compute_currency_id()
            #user_id = self.env.user.id
            #if user_id == 91:
            #    bank_id = self.env['res.bank'].search([('bic', '=', 'BCP')])
            #elif user_id == 92:
            #    bank_id = self.env['res.bank'].search([('bic', '=', 'BISA')])
            #else:
            #    bank_id = False
            request_id.bank_id = bank_id and bank_id.id or False
            for d in data:
                for g in request_id.group_ids.filtered(lambda x: x.id == int(d['cargo_id'])):
                    if g.type == 'material':
                        if d.get('montoUs', False) and g.amount_sus != float(d['montoUs']) and currency == 'usd':
                            error = True
                            msg = "Se debe pagar por completo la deuda de Material"
                        elif d.get('montoBs', False) and g.amount_bs != float(d['montoBs']) and currency == 'bs':
                            error = True
                            msg = "Se debe pagar por completo la deuda de Material"
                        elif not d.get('montoBs', False) and not d.get('montoUs', False):
                            error = True
                            msg = "NO se Introdujo ningun valor para los montos ya se en Us o Bs."
                        elif not error:
                            cids = '[' + g.cids + ']'
                            cids = eval(cids)
                            g.pay = True
                            for c in request_id.line_ids.filtered(lambda x: x.charge_id.id in cids):
                                c.check = True
                            request_id._compute_amount_total()
                    if g.type == 'due':
                        if d.get('montoUs', False) and g.amount_sus != float(d['montoUs']) and currency == 'usd':
                            error = True
                            msg = "Se debe pagar por completo la deuda de Tipo Mora"
                        elif d.get('montoBs', False) and g.amount_bs != float(d['montoBs']) and currency == 'bs':
                            error = True
                            msg = "Se debe pagar por completo la deuda de Material"
                        elif not d.get('montoBs', False) and not d.get('montoUs', False):
                            error = True
                            msg = "NO se Introdujo ningun valor para los montos ya se en Us o Bs."
                        elif not error:
                            cids = '[' + g.cids + ']'
                            cids = eval(cids)
                            g.pay = True
                            for c in request_id.line_ids.filtered(lambda x: x.charge_id.id in cids):
                                c.check = True
                            request_id._compute_amount_total()
                    if g.type == 'pension':
                        for a in request_id.advanced_ids.filtered(lambda x: x.student_id.id == g.student_id.id):
                            if not d.get('montoBs', False) and not d.get('montoUs', False):
                                error = True
                                msg = "NO se Introdujo ningun valor para los montos ya se en Us o Bs."
                            if not error:
                                if currency == 'usd':
                                    if float(d['montoUs']) <= 0:
                                        error = True
                                        msg = "El Monto debe ser Mayor a 0 para proceder con el pago."
                                    else:
                                        a.amount_type = float(d['montoUs'])
                                elif currency == 'bs':
                                    if float(d['montoBs']) <= 0:
                                        error = True
                                        msg = "El Monto debe ser Mayor a 0 para proceder con el pago."
                                    else:
                                        a.amount_type = bob_currency_id.compute(float(d['montoBs']), request_id.currency_id)
                                request_id._compute_amount_total()
            if error:
                res = {
                    'error': error,
                    'mensaje': msg,
                    'request_id': request_id and request_id.id or False,
                }
            else:
                request_id.transaction_number = nr_transaccion
                if request_id.invoiced:
                    request_id.action_confirm_charge()
                    request_id.invoice_id.cc_dos = self.env.ref('poi_x_aleman.dosif_default')
                    request_id.invoice_id._onchange_partner_id()
                    if nit:
                        request_id.invoice_id.nit = nit
                    if razon:
                        request_id.invoice_id.razon = razon
                    if date:
                        request_id.invoice_id.date_invoice = date
                    if nrfactura:
                        request_id.invoice_id.cc_nro = nrfactura
                    if nrautorizacion:
                        request_id.invoice_id.cc_aut = nrautorizacion
                    if nrcodcontrol:
                        request_id.invoice_id.cc_cod = nrcodcontrol
                    else:
                        request_id.invoice_id.onchange_cc_dos()
                    for il in request_id.invoice_id.invoice_line_ids:
                        il.price_unit = request_id.invoice_id.currency_id.compute(il.price_unit, currency_id)
                    request_id.invoice_id.currency_id = currency_id.id
                    request_id.invoice_id._onchange_invoice_line_ids()
                    request_id.invoice_id._compute_amount()
                    request_id.invoice_id.action_invoice_open()
                    request_id.payment_id = request_id.payment_id.with_context(
                        active_id=request_id.invoice_id.id,
                        default_amount=request_id.amount_total,
                        default_charge_request_id=request_id.id,
                        default_invoice_ids=[(4, request_id.invoice_id.id, None)],
                        default_currency_id=currency_id.id,
                        active_model='account.invoice').create({
                            'payment_type': 'inbound',
                            'partner_id': request_id.partner_id.id,
                            'amount': request_id.currency_id.compute(request_id.amount_total, currency_id),
                            'journal_id': journal_id.id or False,
                            'payment_date': request_id.date,
                            'payment_method_id': payment_methods and payment_methods[0].id or False,
                            'partner_type': 'customer',
                        })
                    request_id.payment_id.with_context(
                        active_id=request_id.invoice_id.id,
                        default_amount=request_id.currency_id.compute(request_id.amount_total, currency_id),
                        default_charge_request_id=request_id.id,
                        default_invoice_ids=[(4, request_id.invoice_id.id, None)],
                        default_currency_id=currency_id.id,
                        active_model='account.invoice').action_validate_invoice_payment()
                else:
                    payment_data = {
                        'payment_type': 'inbound',
                        'partner_type': 'customer',
                        'partner_id': request_id.partner_id.id,
                        'amount': request_id.currency_id.compute(request_id.amount_total, currency_id),
                        'journal_id': journal_id.id or False,
                        'payment_date': request_id.date,
                        'payment_method_id': payment_methods and payment_methods[0].id or False,
                    }
                    payment_id = payment_obj.create(payment_data)
                    payment_id.post()
                res = {
                    'error': error,
                    'mensaje': 'Pago se realizo exitosamente',
                    'request_id': request_id and request_id.id or False,
                }
        else:
            res = {
                'error': True,
                'mensaje': 'No es posible encontrar los códigos enviados, Esta seguro que son correctos.',
            }
        return res

    @api.model
    def service_annul_invoice(self, request_id):
        request_ids = self.search([('id', '=', request_id)])
        if request_ids:
            if request_ids[0].state != 'cancel':
                request_ids[0].action_cancel_payment()
                res = {
                    'error': False,
                    'mensaje': 'Se anulo exitosamente la Factura.',
                }
            elif request_ids[0].state == 'cancel':
                res = {
                    'error': True,
                    'mensaje': 'La Factura Ya se Encuentra Anulada.',
                }
        else:
            res = {
                'error': True,
                'mensaje': 'No se Encuentra la Factura en el Sistema.',
            }
        return res

    @api.model
    def service_update_invoice(self, request_id, nit, razon, nrfactura, date, nrautorizacion, nrcodcontrol):
        requests_id = self.search([('id', '=', request_id)])
        error = False
        if requests_id:
            requests_id.invoice_id.nit = nit
            requests_id.invoice_id.razon = razon
            requests_id.invoice_id.date_invoice = date
            requests_id.invoice_id.cc_nro = nrfactura
            requests_id.invoice_id.cc_aut = nrautorizacion
            requests_id.invoice_id.cc_cod = nrcodcontrol
            res = {
                'error': error,
                'mensaje': 'Información guardada exitosamente',
                'request_id': requests_id and requests_id.id or False,
            }
        else:
            res = {
                'error': True,
                'mensaje': 'No se pudo realizar el registro de la factura.',
            }
        return res

    @api.multi
    def action_cancel_payment(self, date=False):
        period_id = self.env['op.school.period'].search([('state', '=', 'active')])
        refund_obj = self.env['account.invoice.refund']
        for s in self:
            if s.state != 'cancel':
                if s.payment_id:
                    s.payment_id.cancel()
                if s.invoice_id:
                    if s.invoice_id.state in ('open', 'paid'):
                        refund_id = refund_obj.create({
                            'filter_refund': 'cancel',
                            'description': 'Cancelación de Factura',
                            'date_invoice': date or fields.Date.today(),
                        })
                        refund_id.with_context(active_ids=[s.invoice_id.id]).invoice_refund()
                    elif s.invoice_id.state in ('draft'):
                        s.invoice_id.action_invoice_cancel()
                    s.state = 'cancel'
                for p in s.pension_ids:
                    if p.charge_id.product_id.id == period_id.product_abono_id.id:
                        p.charge_id.state = 'cancel'
                    else:
                        p.charge_id.state = 'wait'
                        p.charge_id.pension_amount_pay -= p.amount_pay
                s.state = 'cancel'
            else:
                raise Warning('Ya se Encuentra Cancelado el Pago de Cargos')


class OpRequestChargeLine(models.Model):
    _name = "op.request.charge.line"

    @api.depends('charge_id')
    @api.multi
    def _compute_charge_id(self):
        for s in self:
            if s.charge_id:
                s.product_id = s.charge_id.product_id and s.charge_id.product_id.id or False
                s.date = s.charge_id.date
                s.date_due = s.charge_id.date_due
                if s.product_id:
                    s.type = s.product_id.concept_type
                s.amount_untaxed = s.charge_id.amount_untaxed
                s.amount_tax = s.charge_id.amount_tax
                s.amount_total = s.charge_id.amount_diff
                s.student_id = s.charge_id.student_id.id

    @api.depends('request_id')
    @api.multi
    def _compute_charge_id2(self):
        for s in self:
            if s.charge_id and s.request_id and s.request_id.state in ('draft', 'web_service'):
                s.amount_detail = s.charge_id.amount_diff

    request_id = fields.Many2one('op.request.charge', 'Solicitud')
    student_id = fields.Many2one('op.student', 'Alumno', compute="_compute_charge_id")
    check = fields.Boolean('.', default=False)
    charge_id = fields.Many2one('account.op.charge', 'Cargo')
    product_id = fields.Many2one('product.product', 'Producto', compute="_compute_charge_id")
    date = fields.Date('Fecha', compute="_compute_charge_id")
    date_due = fields.Date('Fecha de vencimiento', compute="_compute_charge_id")
    type = fields.Char('Concepto', compute="_compute_charge_id")
    amount_untaxed = fields.Float('Base Imponible', compute="_compute_charge_id", digits=dp.get_precision('Servicios_Web'))
    amount_tax = fields.Float('Impuesto', compute="_compute_charge_id", digits=dp.get_precision('Servicios_Web'))
    amount_total = fields.Float('Total', compute="_compute_charge_id", digits=dp.get_precision('Servicios_Web'))
    amount_detail = fields.Float('Total', compute="_compute_charge_id2", store=True, digits=dp.get_precision('Servicios_Web'))


class OpRequestPensionLine(models.Model):
    _name = "op.request.pension.line"

    @api.depends('charge_id')
    @api.multi
    def _compute_charge_id(self):
        for s in self:
            if s.charge_id:
                s.product_id = s.charge_id.product_id and s.charge_id.product_id.id or False
                s.date = s.charge_id.date
                s.student_id = s.charge_id.student_id.id
                if s.product_id:
                    s.type = s.product_id.concept_type
                s.amount_untaxed = s.charge_id.amount_untaxed
                s.amount_tax = s.charge_id.amount_tax
                s.amount_total = s.charge_id.amount_total

    request_id = fields.Many2one('op.request.charge', 'Solicitud')
    charge_id = fields.Many2one('account.op.charge', 'Cargo')
    product_id = fields.Many2one('product.product', 'Producto', compute="_compute_charge_id")
    date = fields.Date('Fecha', compute="_compute_charge_id")
    student_id = fields.Many2one('op.student', 'Estudiante', compute="_compute_charge_id")
    type = fields.Selection([
        ('pension', 'Pensiones'),
        ('due', 'Mora'),
        ('material', 'Material'),
    ], string="Tipo")
    amount_untaxed = fields.Float('Base Imponible', compute="_compute_charge_id", digits=dp.get_precision('Servicios_Web'))
    amount_tax = fields.Float('Impuesto', compute="_compute_charge_id", digits=dp.get_precision('Servicios_Web'))
    amount_total = fields.Float('Total', compute="_compute_charge_id", digits=dp.get_precision('Servicios_Web'))
    amount_pay = fields.Float('Monto Pagado', digits=dp.get_precision('Servicios_Web'))

    # Funcion temporal para actualizar informacion
    @api.model
    def update_info(self):
        data = self.env['op.request.pension.line'].search([])
        for d in data:
            d._compute_charge_id()

class OpRequestGroup(models.Model):
    _name = "op.request.group"

    @api.depends('charge_id')
    @api.multi
    def _compute_charge_id(self):
        for s in self:
            if s.charge_id:
                s.product_id = s.charge_id.product_id and s.charge_id.product_id.id or False
                s.date = s.charge_id.date
                s.date_due = s.charge_id.date_due
                if s.product_id:
                    s.type = s.product_id.concept_type
                s.amount_untaxed = s.charge_id.amount_untaxed
                s.amount_tax = s.charge_id.amount_tax
                s.amount_total = s.charge_id.amount_total

    request_id = fields.Many2one('op.request.charge', 'Solicitud')
    student_id = fields.Many2one('op.student', 'Estudiante')
    type = fields.Selection([
        ('pension', 'Pensiones'),
        ('due', 'Mora'),
        ('material', 'Material'),
    ], string="Tipo")
    amount_bs = fields.Float('Monto Bs.', digits=dp.get_precision('Servicios_Web'))
    amount_sus = fields.Float('Monto $us.', digits=dp.get_precision('Servicios_Web'))
    cids = fields.Char('Cargosids')
    amount_pay = fields.Float('Monto Pagado', digits=dp.get_precision('Servicios_Web'))
    amount_rest = fields.Float('Monto residual', digits=dp.get_precision('Servicios_Web'))
    pay = fields.Boolean('Pagado', default=False)


class OpRequestAdvanced(models.Model):
    _name = "op.request.advanced"

    @api.depends('amount_type', 'amount_bono')
    @api.multi
    def _compute_amount_bono(self):
        for s in self:
            s.amount = s.amount_type + s.amount_bono

    request_id = fields.Many2one('op.request.charge', 'Solicitud')
    student_id = fields.Many2one('op.student', 'Estudiante')
    date = fields.Date('Fecha', related="request_id.date")
    type = fields.Selection([
        ('pension', 'Pensiones'),
        ('due', 'Mora'),
        ('material', 'Material'),
    ], string="Tipo", default="pension")
    state = fields.Selection('Estado', related="request_id.state")
    amount = fields.Float('Monto Total', compute='_compute_amount_bono', store=True, digits=dp.get_precision('Servicios_Web'))
    amount_rest = fields.Float('Monto residual', digits=dp.get_precision('Servicios_Web'))
    amount_bono = fields.Float('Monto de Abono', digits=dp.get_precision('Servicios_Web'))
    amount_type = fields.Float('Monto', digits=dp.get_precision('Servicios_Web'))
