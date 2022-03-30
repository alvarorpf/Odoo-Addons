# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime
import odoo.addons.decimal_precision as dp


class AccountOpChargeLevel(models.Model):
    _name = "account.op.charge.level"
    _order = "sequence asc"

    name = fields.Char('Nivel de Hijo')
    sequence = fields.Integer('Secuencia')
    active = fields.Boolean('Activo', default=True)


class AccountOpChargeType(models.Model):
    _name = "account.op.charge.type"

    code = fields.Char('Codigo', required=True)
    name = fields.Char('Nombre', required=True)
    type = fields.Selection(
        string="Tipo",
        selection=[
            ('draft', 'Abono'),
            ('send', 'Cargo'),
        ])


class AccountOpCharge(models.Model):
    _name = "account.op.charge"
    _order = "date desc"

    @api.multi
    @api.depends("student_id")
    def _compute_data(self):
        for s in self:
            if s.student_id:
                s.family_id = s.student_id.family_code and s.student_id.family_code.id
                s.family_code = s.student_id.family_code.name
                s.course_level_id = s.student_id.level_id and s.student_id.level_id.id
                s.course_id = s.student_id.class_id and s.student_id.class_id.id
                s.year_id = s.student_id.year_id and s.student_id.year_id.id or False
                s.analytic_id = s.student_id.course_id.level_id and s.student_id.course_id.level_id.id or False

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

    @api.multi
    @api.depends('payment_responsable')
    def _compute_partner_id(self):
        for s in self:
            if s.payment_responsable:
                if s.payment_responsable.partner_id:
                    s.partner_id = s.payment_responsable.partner_id.id
                else:
                    raise Warning(
                        'Atención! Necesita que el Responsable de Pago del Estudiante tenga parametrizado un contacto en su dato maestro.')

    @api.one
    @api.depends('amount', 'currency_id', 'taxes_id')
    def _compute_amount(self):
        taxes = self.taxes_id.compute_all(self.amount, self.currency_id, 1, product=self.product_id,
                                          partner=self.partner_id)
        if 'taxes' in taxes:
            amount_untaxed = 0
            for t in taxes.get('taxes'):
                amount_untaxed += t['amount']
            self.amount_untaxed = taxes.get('total_excluded', 0.00)
            self.amount_tax = amount_untaxed
            self.amount_total = taxes.get('total_included', 0.00)

    @api.multi
    @api.depends('pension_amount_pay', 'amount_total')
    def _compute_amount_diff(self):
        for s in self:
            s.amount_diff = s.amount_total - s.pension_amount_pay
            if s.pension_amount_pay == 0:
                s.state_paid = 'no_paid'
            elif s.pension_amount_pay > 0 and s.amount_diff != 0:
                s.state_paid = 'partial'
            elif s.amount_diff == 0:
                s.state_paid = 'paid'

    @api.multi
    @api.depends('concept_type')
    def _compute_name(self):
        for s in self:
            if s.concept_type:
                if s.concept_type == 'pension' and s.product_id.charge_type == 'charge':
                    s.name = 'CP ' + str(s.family_id.name) + ' ' + str(s.student_id.student_code) + ' ' + str(s.student_id.full_name) + ' ' + '[' + str(s.month_id.initials) + ']'
                elif s.concept_type == 'pension' and s.product_id.charge_type == 'payment':
                    s.name = 'A ' + str(s.family_id.name) + ' ' + str(s.student_id.student_code) + ' Abono por pago adelantado de todo el año'
                elif s.concept_type == 'material':
                    s.name = 'MA ' + str(s.family_id.name) + ' ' + str(s.student_id.student_code) + ' ' + str(s.product_id.name)
                elif s.concept_type == 'due':
                    s.name = 'IM ' + str(s.family_id.name) + ' ' + str(s.student_id.student_code) + ' ' + 'INTERES POR MORA' + ' ' + '[' + str(s.month_id.initials) + ']'
                else:
                    s.name = ''

    student_id = fields.Many2one('op.student', 'Alumno', readonly=True, states={'draft': [('readonly', False)]},
                                 required=True)
    family_code = fields.Char('Codigo de Estudiante', compute="_compute_data")
    type_charge = fields.Many2one('account.op.charge.type', 'Tipo de Cargo', readonly=True,
                                  states={'draft': [('readonly', False)]}, required=True)
    date = fields.Date('Fecha', readonly=True, states={'draft': [('readonly', False)]}, required=True,
                       default=fields.Datetime.now)
    date_due = fields.Date('Fecha de Vencimiento', readonly=True, states={'draft': [('readonly', False)]},
                           required=True)
    year_id = fields.Many2one('op.year', 'Gestión Escolar',
                              default=lambda self: self.env['op.school.period'].search(
                                  [('state', '=', 'active')]).year_id.id, required=True)
    month_id = fields.Many2one('op.month', 'Mes', readonly=True, states={'draft': [('readonly', False)]}, required=True)
    family_id = fields.Many2one('op.family', 'Familia', compute="_compute_data", store=True)
    course_id = fields.Many2one('op.course', 'Clase', readonly=True, compute="_compute_data", store=True)
    course_level_id = fields.Many2one('op.course.level', 'Nivel de Curso', readonly=True, compute="_compute_data")

    product_id = fields.Many2one('product.product', 'Producto', readonly=True, states={'draft': [('readonly', False)]},
                                 required=True)
    analytic_id = fields.Many2one('account.analytic.account', 'Cuenta Analítica',
                                  states={'draft': [('readonly', False)]}, compute="_compute_data")
    name = fields.Char('Descripcion', compute='_compute_name', store=True)
    amount = fields.Float('Monto', readonly=True, states={'draft': [('readonly', False)]}, required=True)
    priority_id = fields.Many2one('op.priority', 'Prioridad', readonly=True, states={'draft': [('readonly', False)]})
    taxes_id = fields.Many2many('account.tax', string='Impuesto', readonly=True,
                                states={'draft': [('readonly', False)]})
    amount_untaxed = fields.Float('Base Imponible', compute="_compute_amount", store=True, digits=dp.get_precision('Servicios_Web'))
    amount_tax = fields.Float('Impuesto', compute="_compute_amount", store=True, digits=dp.get_precision('Servicios_Web'))
    amount_total = fields.Float('Monto Total', compute="_compute_amount", store=True, digits=dp.get_precision('Servicios_Web'))

    # invoice_id = fields.Many2one('account.invoice', 'Factura', readonly=True)
    # payment_id = fields.Many2one('account.payment', 'Pago', readonly=True)
    request_id = fields.Many2one('op.request.charge', 'Pago de Cargos')

    to_bank = fields.Boolean('Para Facturar en Banco', readonly=True, states={'draft': [('readonly', False)]})
    odoo_id = fields.Char('Id Odoo', readonly=True)
    currency_id = fields.Many2one("res.currency", "Moneda", compute="_compute_currency_id", store=True)
    payment_responsable = fields.Many2one('op.parent.contact', 'Responsable de Pago',
                                          related="student_id.payment_responsable", readonly=True)
    partner_id = fields.Many2one('res.partner', 'Contacto', compute="_compute_partner_id", store=True)
    account_id = fields.Many2one('account.account', 'Cuenta', readonly=True, states={'draft': [('readonly', False)]},
                                 required=True)
    picking_id = fields.Many2one('stock.picking', 'Albaran', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(
        string="Estado",
        selection=[
            ('draft', 'Borrador'),
            ('wait', 'En-Espera'),
            ('send', 'Confirmado'),
            ('done', 'Pagado'),
            ('cancel', 'Cancelado'),
        ], default='draft'
    )
    concept_type = fields.Selection(
        string='Concepto',
        selection=[
            ('material', 'Material'),
            ('due', 'Mora'),
            ('pension', 'Pension'),
        ], readonly=True, states={'draft': [('readonly', False)]},store=True)
    mora = fields.Boolean('Mora', default=False)

    pension_amount_pay = fields.Float('Monto Pagado', default=0, copy=False)
    amount_diff = fields.Float('Saldo', compute="_compute_amount_diff", store=True)
    state_paid = fields.Selection([
        ('partial', 'Pago Parcial'),
        ('no_paid', 'Sin Pago'),
        ('paid', 'Pagado'),
    ], string="Estado de Pago", default="no_paid", store=True, compute="_compute_amount_diff")
    warehouse_id = fields.Many2one('stock.warehouse', "Almacén", readonly=True, default=lambda self: self.env.user.shop_assigned and self.env.user.shop_assigned.id or False, states={'draft': [('readonly', False)]})

    invoiced = fields.Boolean('Facturar?', default=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.student_id:
            part = self.partner_id
            company = self.env.user.company_id
            currency = self.currency_id
            invoice_obj = self.env['account.invoice.line']
            if not part:
                warning = {
                    'title': _('Warning!'),
                    'message': _('Se Necesita Haber parametrizado el contacto del responsable de pago.!'),
                }
                return {'warning': warning}
            if part.lang:
                product = self.product_id.with_context(lang=part.lang)
            else:
                product = self.product_id

            self.name = product.partner_ref
            account = invoice_obj.get_invoice_line_account('out_invoice', product, False, company)
            if account:
                self.account_id = account.id

            if product.description_sale:
                self.name += '\n' + product.description_sale
            self.concept_type = self.product_id.concept_type
            if self.concept_type == 'pension' and product.charge_type == 'charge':
                if self.month_id.id == self.env.ref('poi_x_aleman.january').id:
                    self.amount = self.student_id.first_pension
                else:
                    self.amount = self.student_id.regular_pension
            elif self.concept_type == 'due':
                self.amount = self.amount
            else:
                self.amount = self.amount
        if self.product_id:
            self.taxes_id = self.product_id.taxes_id

    @api.onchange('date')
    def onchange_date(self):
        if self.date:
            month_obj = self.env['op.month']
            date = datetime.strptime(self.date, '%Y-%m-%d')
            month_ids = month_obj.search([('sequence', '=', date.month)])
            if month_ids:
                self.month_id = month_ids[0].id

    @api.multi
    def action_send(self):
        self.state = 'wait'
        self.action_search_request_open()
        if self.concept_type == 'material':
            self.action_create_picking()

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.multi
    def action_cancel(self):
        detail_obj = self.env['op.request.pension.line']
        for s in self:
            if s.state not in ('cancel'):
                detail_ids = detail_obj.search([('charge_id', '=', s.id)])
                for d in detail_ids:
                    if d.product_id.concept_type == 'pension':
                        for a in d.request_id.advanced_ids.filtered(lambda x: x.student_id.id == d.student_id.id and x.type == 'pension'):
                            a.amount_rest += d.amount_pay
                    elif d.product_id.concept_type == 'material':
                        material_ids = d.request_id.advanced_ids.filtered(lambda x: x.student_id.id == d.student_id.id and x.type == 'material')
                        if material_ids:
                            for a in material_ids:
                                a.amount_rest += d.amount_pay
                        else:
                            d.request_id.advanced_ids = [(0, 0, {
                                'student_id': d.student_id,
                                'type': 'material',
                                'amount_type': d.amount_pay,
                                'amount_rest': d.amount_pay,
                            })]
                    elif d.product_id.concept_type == 'due':
                        material_ids = d.request_id.advanced_ids.filtered(lambda x: x.student_id.id == d.student_id.id and x.type == 'due')
                        if material_ids:
                            for a in material_ids:
                                a.amount_rest += d.amount_pay
                        else:
                            d.request_id.advanced_ids = [(0, 0, {
                                'student_id': d.student_id,
                                'type': 'due',
                                'amount_type': d.amount_pay,
                                'amount_rest': d.amount_pay,
                            })]
                    d.amount_pay = 0
                s.pension_amount_pay = 0
                s.state = 'cancel'


    @api.multi
    def create_invoice(self):
        invoice_obj = self.env['account.invoice']
        invoice_line_data = [(0, 0, {
            'product_id': self.product_id.id,
            'account_analytic_id': self.analytic_id.id,
            'quantity': 1,
            'price_unit': self.amount_total,
            'name': self.product_id.name,
            'account_id': self.account_id.id,
        })]
        invoice_data = {
            'partner_id': self.payment_responsable.partner_id.id,
            # 'currency_id': self.currency_id.id,
            'nit': 123,
            'date_invoice': self.date,
            'date_due': self.date_due,
            'invoice_line_ids': invoice_line_data,
            # 'company_id': self.env.user.company_id.id,
            'tipo_fact': '7',
            'type': 'out_invoice',
            'account_id': self.payment_responsable.partner_id.property_account_receivable_id.id,
        }
        invoice_id = invoice_obj.create(invoice_data)
        self.invoice_id = invoice_id.id

    @api.multi
    def action_generate_due(self):
        month_obj = self.env['op.month']
        invoice_obj = self.env['account.invoice.line']
        date = datetime.strptime(self.env.context.get('date'), '%Y-%m-%d')
        month_ids = month_obj.search([('sequence', '=', date.month)])
        if month_ids:
            month_id = month_ids[0].id
        count = 0
        account = invoice_obj.get_invoice_line_account('out_invoice', self.env.context.get('product_id', False), False,
                                                       self.env.user.company_id)
        amount = self.env.context.get('amount', 0)
        if amount > 0:
            charge_id = self.create({
                'type_charge': self.env.ref('poi_x_aleman.type_charge_mora').id,
                'student_id': self.env.context.get('student_id', False),
                'month_id': month_id,
                'year_id': self.env.context.get('year_id', False),
                'date': self.env.context.get('date', False),
                'date_due': self.env.context.get('date_due', False),
                'product_id': self.env.context.get('product_id', False).id,
                'name': self.env.context.get('product_id', False).name,
                'amount': amount * (self.env.context.get('surcharge', 0) / 100),
                'mora': True,
                'account_id': account and account.id or False,
            })
            charge_id.onchange_product_id()
            charge_id.action_send()
            charge_id.amount = amount * (self.env.context.get('surcharge', 0) / 100)
            count += 1
        return count

    @api.multi
    def action_search_request_open(self):
        request_obj = self.env['op.request.advanced']
        for s in self:
            advanced_ids = request_obj.search([('student_id', '=', s.student_id.id), ('state', '=', 'done'), ('amount_rest', '>', 0), ('type', '=', s.product_id.concept_type)], order="date asc")
            for a in advanced_ids:
                data = []
                pay_amount = a.amount_rest
                if s.amount_diff > pay_amount:
                    s.pension_amount_pay += pay_amount
                    if s.amount_diff == 0:
                        s.action_done()
                    data.append([0, 0, {
                        'charge_id': s.id,
                        'amount_pay': pay_amount
                    }])
                    pay_amount = 0
                else:
                    diff = pay_amount - s.amount_diff
                    data.append([0, 0, {
                        'charge_id': s.id,
                        'amount_pay': s.amount_diff
                    }])
                    s.pension_amount_pay += s.amount_diff
                    s.action_done()
                    pay_amount = diff
                a.amount_rest = pay_amount
                a.request_id.pension_ids = data
                s._compute_amount_diff()
                if s.amount_diff == 0:
                    break

    @api.multi
    def create_payment(self):
        #Pasar los IDs de cargos a ser pagados
        action_next = {
            'name': 'Asistente de pago de cargos',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.op.charge.pay',
            'target': 'new',
            'context': {'charge_ids': [a.id for a in self]},
            'type': 'ir.actions.act_window',
        }
        return action_next

    @api.one
    def action_open_requests(self):

        request_line = self.env['op.request.charge.line']
        requests = request_line.read_group([('charge_id','=',self.id)], ['request_id'], ['request_id'])
        req_ids = []
        for req in requests:
            req_ids.append(req['request_id'][0])

        if len(req_ids) == 0:
            raise Warning("No se ha encontrado ningún Pago de cargo registrado.")
        elif len(req_ids) == 1:
            # Abrir formulario
            views = [(self.env.ref('poi_x_aleman.op_request_charge_view_form').id, 'form'),
                     (self.env.ref('poi_x_aleman.op_request_charge_view_tree').id, 'tree')]
            action_result = {
                'type': 'ir.actions.act_window',
                'name': 'Pago de cargo',
                #'view_type': 'form',
                'view_mode': 'form',
                'views': [(self.env.ref('poi_x_aleman.op_request_charge_view_form').id, 'form')],
                #'view_id': False,
                'res_model': 'op.request.charge',
                'res_id': req_ids[0],
                'flags': {'form': {'action_buttons': True}},
            }
            return action_result

        elif len(req_ids) >= 1:
            # Abrir listado
            views = [(self.env.ref('poi_x_aleman.op_request_charge_view_tree').id, 'tree'),
                     (self.env.ref('poi_x_aleman.op_request_charge_view_form').id, 'form')]
            action_result = {
                'name': 'Pago de cargo',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'views': views,
                'res_model': 'op.request.charge',
                'target': 'current',
                'domain': [('id','in',req_ids)],
                'type': 'ir.actions.act_window',
            }
            print(action_result)
            return action_result

    @api.multi
    def action_pay(self):
        return

    @api.multi
    def action_pay_invoice(self):
        pass

    @api.model
    def service_get_invoices(self, student_code):
        if not student_code:
            return {
                'Estado': "Error",
                'Mensaje': "Error, no se envió el código de Estudiante.",
            }
        material = {}
        due = {}
        pension = {}
        charges = []
        charge_ids = self.search([('family_code', '=', student_code)])
        for c in charge_ids:
            if c.concept_type == 'material':
                if material:
                    material.update({
                        'MontoBs': material['MontoBs'] + c.amount_total,
                        'MontoUs': material['MontoUs'] + c.amount_total,
                    })
                else:
                    material.update({
                        'Descripcion': 'Material',
                        'MontoBs': c.amount_total,
                        'MontoUs': c.amount_total,
                    })
                    charges.append(material)
            elif c.concept_type == 'pension':
                if pension:
                    pension.update({
                        'MontoBs': pension['MontoBs'] + c.amount_total,
                        'MontoUs': pension['MontoUs'] + c.amount_total,
                    })
                else:
                    pension.append({
                        'Descripcion': 'Pension',
                        'MontoBs': c.amount_total,
                        'MontoUs': c.amount_total,
                    })
                    charges.append(pension)
            elif c.concept_type == 'due':
                if due:
                    due.update({
                        'MontoBs': due['MontoBs'] + c.amount_total,
                        'MontoUs': due['MontoUs'] + c.amount_total,
                    })
                else:
                    due.append({
                        'Descripcion': 'Deuda',
                        'MontoBs': c.amount_total,
                        'MontoUs': c.amount_total,
                    })
                    charges.append(due)
        res = {
            'error': False,
            'mensaje': False,
            'data': charges,
        }

    @api.model
    def service_pay_invoice(self, charge_id):
        if not charge_id:
            return {
                'error': True,
                'mensaje': "Error, no se envió el Id de Cargo.",
            }
        charge_id = self.browse(charge_id)
        charge_id.action_pay_invoice()

    @api.multi
    def action_create_picking(self):
        picking_obj = self.env['stock.picking']
        for s in self:
            if s.product_id.type == 'product':
                move_lines = []
                move_lines.append([0, 0, {
                    'name': s.product_id.name,
                    'product_id': s.product_id.id,
                    'product_uom_qty': 1,
                    'product_uom': s.product_id.uom_id and s.product_id.uom_id.id or False,
                    'quantity_done': 1,
                }])
                picking_id = picking_obj.create({
                    # 'name': 'new',
                    'partner_id': s.partner_id.id,
                    'origin': s.name,
                    'picking_type_id': s.warehouse_id.out_type_id and s.warehouse_id.out_type_id.id or False,
                    'move_lines': move_lines,
                    'location_id': s.warehouse_id.out_type_id and s.warehouse_id.out_type_id.default_location_src_id and s.warehouse_id.out_type_id.default_location_src_id.id or False,
                    'location_dest_id': s.warehouse_id.out_type_id and s.warehouse_id.out_type_id.default_location_dest_id and s.warehouse_id.out_type_id.default_location_dest_id.id or False,
                })
                s.picking_id = picking_id.id

    @api.model
    def update_info(self):
        charge_obj = self.env['account.op.charge']
        charges = charge_obj.search([])
        for charge in charges:
            charge.date = '2019-01-18'
            charge.onchange_date()
            charge._compute_name()

    @api.multi
    def service_get_charges(self, fields=False):
        partner_id = self.env.user.partner_id
        contact_obj = self.env['op.parent.contact']
        contact_id = contact_obj.search([('partner_id', '=', partner_id.id)])
        if contact_id:
            family_ids = contact_id.family_id.mapped('id')
        else: 
            return []
        charge_ids = self.search([('family_id', 'in', family_ids)])

        result = charge_ids.read(fields)
        if len(result) <= 1:
            return result

        # reorder read
        index = {vals['id']: vals for vals in result}
        return [index[record.id] for record in charge_ids if record.id in index]
