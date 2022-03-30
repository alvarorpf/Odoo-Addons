# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
import odoo.addons.decimal_precision as dp


# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
import odoo.addons.decimal_precision as dp


class OpRequestImport(models.Model):
    _name = "op.request.import"

    name = fields.Char('Descripción')
    date = fields.Date('Fecha de Importación', default=fields.Date.today())
    currency_origin = fields.Selection([
        ('bs', 'Bolivianos(Bs.)'),
        ('usd', 'Dolares($us.)')
    ], string='Moneda Origen', help="moneda en la que se esta importando el archivo")
    currency = fields.Selection([
        ('bs', 'Bolivianos(Bs.)'),
        ('usd', 'Dolares($us.)')
    ], string='Moneda Destino', help="Moneda en la que se registrara el pago y la factura.")
    tc = fields.Float('Tasa de Cambio', help="tasa de cambio usado para la moneda de destino")
    line_ids = fields.One2many('op.request.import.line', 'import_id', 'Importación')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirm', 'Confirmado'),
        ('done', 'Realizado'),
    ], default="draft", string="Estado")
    user_id = fields.Many2one('res.users', 'Usuario')

    @api.multi
    def action_set_currency(self):
        for s in self:
            for l in s.line_ids:
                l.currency = s.currency
                l.tc = s.tc

    @api.multi
    def action_confirm(self):
        self.action_set_currency()
        for s in self:
            s.state = 'confirm'

    @api.multi
    def action_done(self):
        for s in self:
            s.create_request()
            if not s.line_ids.filtered(lambda l: l.state == 'no_process'):
                s.state = 'done'

    @api.multi
    def create_request(self):
        invoice_obj = self.env['account.invoice']
        family_obj = self.env['op.family']
        charge_obj = self.env['account.op.charge']
        request_obj = self.env['op.request.charge']
        bob_currency_id = self.env.ref('base.BOB')
        usd_currency_id = self.env.ref('base.USD')
        if self.currency == 'bs':
            currency_id = bob_currency_id
        elif self.currency == 'usd':
            currency_id = usd_currency_id

        tc = False
        if self.currency != self.currency_origin:
            tc = True

        period_ids = self.env['op.school.period'].search([('state', '=', 'active')], limit=1)
        if period_ids:
            period_id = period_ids[0]
            school_bank_ids = self.env['op.school.bank'].search([('period_id', '=', period_id.id), ('user_id', '=', self.user_id.id), ('currency_id', '=', currency_id.id)], limit=1)
        else:
            raise Warning('No se encuentra una gestión escolar activa, para completar el proceso.')
        if school_bank_ids:
            school_bank_id = school_bank_ids[0]
            payment_methods = school_bank_id.journal_id.inbound_payment_method_ids or school_bank_id.journal_id.outbound_payment_method_ids
            journal_id = school_bank_id.journal_id or False
            bank_id = school_bank_id.bank_id or False
        else:
            raise Warning('El usuario que esta utilizando no se encuentra habilitado para realizar esta operación')
        for s in self:
            for l in s.line_ids.filtered(lambda l: l.state == 'no_process'):
                if l.state == 'no_process':
                    date = datetime.strptime(l.date_invoice, '%Y%m%d')
                    date_invoice = date.strftime('%Y-%m-%d')
                    if invoice_obj.search([('cc_nro', '=', l.nro_fac), ('cc_aut', '=', l.cc_aut.strip()), ('date_invoice', '=', date_invoice), ('cc_cod', '=', l.cc_cod)]):
                        raise Warning('Se encontró que el numero de Factura %s, con fecha %s, nro de autorización %s y código de control %s, ya se encuentra en el sistema.' % (l.nro_fac, date_invoice, l.cc_aut.strip(), l.cc_cod))
                    domain = []
                    d = []
                    if l.note.strip() == 'PAGO PENSIONES':
                        domain = [('product_id.concept_type', '=', 'pension')]
                    elif l.note.strip() == 'MORA':
                        domain = [('product_id.concept_type', '=', 'due')]

                    family_ids = family_obj.search([('name', '=', l.code.strip())])
                    request_id = False
                    if family_ids:
                        family_id = family_ids[0]
                        d = [('family_id', '=', family_id.id), ('state', 'in', ['wait'])]
                        d += domain
                        charge_ids = charge_obj.search(d, order='date asc')

                        request_id = request_obj.create({
                            'code_family': family_id.id,
                            'date': fields.Date.context_today(self),
                            'date_due': fields.Date.context_today(self),
                            'state': 'draft',
                        })
                        request_id.onchange_student_id()
                        request_id._compute_partner_id()
                        request_id._compute_currency_id()
                        request_id.bank_id = bank_id and bank_id.id or False
                        if tc:
                            if self.currency_origin == 'bs' and self.currency == 'usd':
                                amount = l.amount_total / self.tc
                            elif self.currency_origin == 'usd' and self.currency == 'bs':
                                amount = l.amount_total * self.tc
                        else:
                            if self.currency_origin == 'bs' and self.currency == 'bs':
                                amount = l.amount_total / self.tc
                            else:
                                amount = l.amount_total
                        for c in charge_ids:
                            if amount <= c.amount_diff:
                                adv_ids = request_id.advanced_ids.filtered(lambda x: x.student_id.id == c.student_id.id)
                                if adv_ids:
                                    for a in adv_ids:
                                        a.amount_type += amount
                                else:
                                    request_id.advanced_ids = [(0, 0, {
                                        'student_id': c.student_id.id,
                                        'type': c.product_id.concept_type,
                                        'amount_type': amount,
                                    })]
                                amount = 0
                                break
                            elif amount >= c.amount_diff:
                                amount -= c.amount_diff
                                adv_ids = request_id.advanced_ids.filtered(lambda x: x.student_id.id == c.student_id.id)
                                if adv_ids:
                                    for a in adv_ids:
                                        a.amount_type += c.amount_diff
                                else:
                                    request_id.advanced_ids = [(0, 0, {
                                        'student_id': c.student_id.id,
                                        'type': c.product_id.concept_type,
                                        'amount_type': c.amount_diff,
                                    })]
                        if amount > 0:
                            amount /= len(request_id.advanced_ids.ids)
                            data = []
                            for a in request_id.advanced_ids:
                                if not l.note.strip() == 'MORA':
                                    a.amount_type += amount
                                else:
                                    data.append([0, 0, {
                                        'student_id': a.student_id.id,
                                        'type': 'due',
                                        'amount_type': amount,
                                    }])
                            request_id.advanced_ids = data
                        request_id.with_context(nit=l.nit).action_confirm_charge()
                        request_id.invoice_id.cc_dos = self.env.ref('poi_x_aleman.dosif_default')
                        # request_id.invoice_id._onchange_partner_id()

                        request_id.invoice_id.nit = l.nit
                        request_id.invoice_id.razon = l.razon
                        date = datetime.strptime(l.date_invoice, '%Y%m%d')
                        request_id.invoice_id.date_invoice = date.strftime('%Y-%m-%d')
                        request_id.invoice_id.onchange_cc_dos()
                        request_id.invoice_id.cc_nro = l.nro_fac
                        request_id.invoice_id.cc_aut = l.cc_aut.strip()
                        request_id.invoice_id.cc_cod = l.cc_cod
                        for il in request_id.invoice_id.invoice_line_ids:
                            if self.currency == 'bs':
                                il.price_unit = il.price_unit * self.tc
                            elif self.currency == 'usd':
                                il.price_unit = il.price_unit
                        request_id.invoice_id.currency_id = currency_id.id
                        request_id.invoice_id._onchange_invoice_line_ids()
                        request_id.invoice_id._compute_amount()
                        request_id.invoice_id.action_invoice_open()
                        request_id.invoice_id.cc_nro = l.nro_fac
                        request_id.invoice_id.cc_aut = l.cc_aut.strip()
                        request_id.invoice_id.cc_cod = l.cc_cod
                        request_id.payment_id = request_id.payment_id.with_context(
                            active_id=request_id.invoice_id.id,
                            default_amount=request_id.amount_total,
                            default_charge_request_id=request_id.id,
                            default_invoice_ids=[(4, request_id.invoice_id.id, None)],
                            default_currency_id=currency_id.id,
                            active_model='account.invoice').create({
                                'payment_type': 'inbound',
                                'partner_id': request_id.partner_id.id,
                                'amount': request_id.invoice_id.amount_total,
                                'journal_id': journal_id.id or False,
                                'payment_date': date.strftime('%Y-%m-%d'),
                                'payment_method_id': payment_methods and payment_methods[0].id or False,
                                'partner_type': 'customer',
                            })
                        request_id.payment_id.with_context(
                            active_id=request_id.invoice_id.id,
                            default_amount=request_id.invoice_id.amount_total,
                            default_charge_request_id=request_id.id,
                            default_invoice_ids=[(4, request_id.invoice_id.id, None)],
                            default_currency_id=currency_id.id,
                            active_model='account.invoice').action_validate_invoice_payment()
                        if l.estado_fac.strip() == 'A':
                            request_id.action_cancel_payment(date=date.strftime('%Y-%m-%d'))
                        l.request_id = request_id.id
                        l.state = 'process'
                        self.env.cr.commit()

    @api.multi
    def action_view_line_ids(self):
        context = dict(self.env.context or {})
        context['default_import_id'] = self.id
        return {
            'name': 'Lineas a Importar',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'op.request.import.line',
            'view_id': self.env.ref('poi_x_aleman.op_request_import_line_view_tree').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'domain': [('id', 'in', self.line_ids.ids)],
        }


class OpRequestImport(models.Model):
    _name = "op.request.import.line"

    import_id = fields.Many2one('op.request.import', 'Importacion')
    nit = fields.Char('Nro de Nit')
    razon = fields.Char('Razón')
    nro_fac = fields.Integer('Numero de Factura')
    cc_aut = fields.Char('Nro de Autorización')
    date_invoice = fields.Char('Fecha de Facturación')
    amount_total = fields.Float('Importe Total Facturado')
    ice = fields.Float('ICE')
    exentos = fields.Float('Importes Exentos')
    amount_iva = fields.Float('Importe Sujeto a Debito Fiscal')
    iva = fields.Float('Debito Fiscal')
    estado_fac = fields.Char('Estado de Facturación')
    cc_cod = fields.Char('Código de Control')
    code = fields.Char('Código de Recaudación')
    note = fields.Char("Descripción del Servicio")
    currency = fields.Char('Moneda')
    tc = fields.Float('Tasa de Cambio')
    state = fields.Selection([
        ('no_process', 'Sin Procesar'),
        ('process', 'Procesado')
    ], string="Estado", default="no_process")
    request_id = fields.Many2one('op.request.charge', 'Pago de Cargos')
