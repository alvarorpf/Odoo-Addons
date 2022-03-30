# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
import calendar
import datetime


class OpSchoolCharge(models.Model):
    _name = 'op.school.charge'
    _description = "Gestion Escolar, Cargos"

    period_id = fields.Many2one('op.school.period', 'Gestion Escolar')
    year_id = fields.Many2one('op.year', 'Gestion Escolar')
    month_id = fields.Many2one('op.month', 'Mes')
    auto = fields.Boolean('Generar Cargo Automatico')
    auto_due = fields.Boolean('Generar Mora Automatico')
    date = fields.Date('Fecha de Generacion')
    count_charge = fields.Integer('Cargos Generados')


class OpSchoolNivel(models.Model):
    _name = 'op.school.nivel'
    _description = "Gestion Escolar, Niveles"

    period_id = fields.Many2one('op.school.period', 'Gestion Escolar')
    level_id = fields.Many2one('account.op.charge.level', 'Nivel')
    amount_first_fee = fields.Float('Monto Primera Pension')
    amount_regular_fee = fields.Float('Monto Pension Regular')
    discount_prepayment = fields.Float('Descuento por Pago Adelantado')


class OpSchoolChargeAuto(models.Model):
    _name = 'op.school.chargeauto'
    _description = "Gestion Escolar, Cargos"

    period_id = fields.Many2one('op.school.period', 'Gestion Escolar')
    year_id = fields.Many2one('op.year', 'Gestion Escolar')
    month_id = fields.Many2one('op.month', 'Mes')
    auto = fields.Boolean('Generar Cargo Automatico')
    date = fields.Date('Fecha de Generacion')
    count_charge = fields.Integer('Cargos Generados')


class OpSchoolBank(models.Model):
    _name = 'op.school.bank'
    _description = "Gestion Escolar, Cargos"

    period_id = fields.Many2one('op.school.period', 'Gestion Escolar')
    bank_id = fields.Many2one('res.bank', 'Banco')
    user_id = fields.Many2one('res.users', 'Usuario', required=True)
    currency_id = fields.Many2one("res.currency", "Moneda", required=True)
    journal_id = fields.Many2one('account.journal', 'Diario de Pago')

    _sql_constraints = [('unique_bank', 'unique(user_id, currency_id)',
                         'No puede configurar la misma moneda para este usuario.')]


class OpSchoolPeriod(models.Model):
    _name = 'op.school.period'
    _description = "Gestion Escolar"

    @api.multi
    @api.depends('year_id')
    def _compute_name(self):
        for s in self:
            s.name = s.year_id and s.year_id.name or ''

    name = fields.Char('Descripcion', compute="_compute_name")
    year_id = fields.Many2one('op.year', 'Gestion Escolar', copy=False)
    currency_id = fields.Many2one('res.currency', 'Moneda')
    date_from = fields.Date('Fecha de Incio')
    date_to = fields.Date('Fecha de Cierre')
    date_delivery = fields.Date("Fecha de Entrega")
    date_fm = fields.Date('Fecha entrega F.M.')

    surcharge = fields.Float('Recargo por pension retrasada(%)')
    amount_limit = fields.Float('Monto Limite para Promocionar')
    # discount_childs = fields.Float('Descuento por pago anual  por Hijo')
    day_initial = fields.Integer('Dia del mes para generar cargo')
    product_due_id = fields.Many2one('product.product', 'Producto a Generar Mora',
                                     help="Selecciona el producto que se generara en caso de Mora de Cargos.")
    product_pension_id = fields.Many2one('product.product', 'Producto a Generar Pension',
                                         help="Selecciona el producto que se generara en Cargos.")
    product_abono_id = fields.Many2one('product.product', 'Producto a Generar Abono',
                                         help="Selecciona el producto que se un abono a favor del responsable de pago.")
    #journal_usd_id = fields.Many2one('account.journal', 'Diario $')
    #journal_bs_id = fields.Many2one('account.journal', 'Diario Bs')
    days_due = fields.Integer('Dias de Vencimiento de Pension',
                              help="Coloque los dias que tomara a un cargo vencer para generar un mora.")
    visit_cost = fields.Float('Costo de Visita')
    first_fee = fields.Float('Primera Cuota')
    supplies_cost = fields.Float('Material Escolar')
    amount_camera = fields.Float('Monto Camara')
    day_initial_camera = fields.Integer('Dia del mes para generar cargo de comercio')
    product_kinder_pension_id = fields.Many2one('product.product', 'Producto Pensiones Kinder Proxima Gestion',
                                         help="Selecciona el producto que se generara pensiones kinder proxima gestion.")
    product_comercio_pension_id = fields.Many2one('product.product', 'Producto a Generar Pension Comercio',
                                         help="Selecciona el producto que se generara en Cargos de Comercio.")

    charge_ids = fields.One2many('op.school.charge', 'period_id', 'Cargos/Pensiones')
    nivel_ids = fields.One2many('op.school.nivel', 'period_id', 'Nivel')
    chargeauto_ids = fields.One2many('op.school.chargeauto', 'period_id', 'Cargos Automaticos')
    bank_ids = fields.One2many('op.school.bank', 'period_id', 'Bancos')
    state = fields.Selection(string="Estado",
                             selection=[
                                 ('draft', 'Inicial'),
                                 ('active', 'Activo'),
                                 ('archive', 'Archivado'),
                             ], default='draft', readonly=True, states={'draft': [('readonly', False)]}
                             )

    _sql_constraints = [
        ('year_id_uniq', 'unique (year_id)',
         'La Gestion Escolar es Unica !')
    ]

    @api.multi
    def unlink(self):
        for period in self:
            if period.state in ('active', 'archive'):
                raise Warning(
                    _('No puede eliminar un periodo escolar que este en estado Activo o Archivado.'))
            return models.Model.unlink(self)

    @api.onchange('year_id')
    def onchange_year_id(self):
        if not self.charge_ids and self.year_id:
            month_obj = self.env['op.month']
            month_ids = month_obj.search([('active', '=', True)])
            charge_data = []
            for month in month_ids:
                data_charge = {
                    'year_id': self.year_id.id,
                    'month_id': month.id,
                }
                charge_data.append([0, 0, data_charge])

            self.charge_ids = charge_data
            self.chargeauto_ids = charge_data
        elif self.charge_ids and self.year_id:
            for charge in self.charge_ids:
                charge.year_id = self.year_id.id

    @api.onchange('day_initial')
    def onchange_day_initial(self):
        if self.charge_ids and self.year_id and self.day_initial:
            for charge in self.charge_ids:
                day = self.day_initial
                day = self.check_day_month(charge.year_id.name, charge.month_id.name, day)
                charge.date = charge.year_id.name + "-" + charge.month_id.name + "-" + str(day)

    @api.onchange('day_initial_camera')
    def onchange_day_initial_camera(self):
        if self.chargeauto_ids and self.year_id and self.day_initial_camera:
            for charge in self.chargeauto_ids:
                day = self.day_initial_camera
                day = self.check_day_month(charge.year_id.name, charge.month_id.name, day)
                charge.date = charge.year_id.name + "-" + charge.month_id.name + "-" + str(day)

    def check_day_month(self, year, month, day):
        date = calendar.monthrange(int(year), int(month))
        if day > date[1]:
            return date[1]
        return day

    @api.onchange("nivel_ids")
    def _onchange_nivel_ids(self):
        level_obj = self.env['account.op.charge.level']
        level_ids = level_obj.search([])
        for i, s in enumerate(self.nivel_ids):
            try:
                s.level_id = level_ids[i].id
            except IndexError:
                s.level_id = False

    @api.multi
    def action_continue_open_period(self):

        return {
            'name': _('Promocionar Alumnos'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'op.period.open',
            'target': 'new',
            'view_id': self.env.ref('poi_x_aleman.op_period_open_wiz2_view_form').ids,
            'type': 'ir.actions.act_window',
            'context': {
                'default_new_year_id': self.year_id.id
            },
        }

    @api.multi
    def action_activate_period(self):
        return {
            'name': _('Activar Periodo Escolar'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'op.activate.period',
            'target': 'new',
            'view_id': self.env.ref('poi_x_aleman.op_activate_period_view_form').ids,
            'type': 'ir.actions.act_window',
            'context': {
                'default_period_id': self.id
            }
        }

    # Generación de Cargos Automaticos
    @api.model
    def _cron_generate_charges(self):
        period_id = self.search([('state', '=', 'active')])
        kinder = self.env.ref('poi_x_aleman.student_case_active_5').id
        com1 = self.env.ref('poi_x_aleman.student_case_active_6').id
        com2 = self.env.ref('poi_x_aleman.student_case_active_7').id
        today = fields.Date.from_string(fields.Date.context_today(self))
        month = today.month
        charges = []
        count = 0
        if period_id:
            period_id = period_id[0]
            for c in period_id.charge_ids:
                if c.auto:
                    charges.append(c.id)
            date = fields.Date.today()
            date_due = ""
            charge_obj = self.env['account.op.charge']
            student_obj = self.env['op.student']
            student_ids = student_obj.search([('state', '=', 'activo'), ('case_id', 'not in', [com1, com2, kinder])])
            period_charge_id = period_id.charge_ids.filtered(lambda x: x.date == date and x.auto is True)
            due_charge_id = period_id.charge_ids.filtered(lambda x: x.auto_due is True and x.date == date)
            if due_charge_id:
                for student in student_ids:
                    charge_ids = charge_obj.search(
                        [('state', 'in', ['wait', 'send']), ('product_id.concept_type', '=', 'pension'), ('student_id', '=', student.id)])
                    if charge_ids:
                        amount = 0
                        for charge in charge_ids:
                            amount = amount + charge.amount_diff
                        charge_obj.with_context(
                            date_due=str(datetime.date(datetime.datetime.now().year, 11, 30)),
                            year_id=period_id.year_id.id,
                            date=date,
                            product_id=period_id.product_due_id,
                            surcharge=period_id.surcharge,
                            student_id=student.id,
                            amount=amount,
                        ).action_generate_due()
            if period_charge_id:
                dd = charges.index(period_charge_id.id)
                if dd < len(charges) - 1:
                    charge_id = self.env['op.school.charge'].search([('id', '=', charges[dd + 1])])
                    date_due = charge_id.date
                elif dd == len(charges) - 1:
                    last_day = calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]
                    date_due = str(datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, last_day))
                period_charge_id = period_charge_id[0]
                count += student_ids.with_context(
                    date=date,
                    year_id=period_id.year_id.id,
                    date_due=date_due,
                    product_id=period_id.product_pension_id,
                    surcharge=period_id.surcharge,
                ).action_generate_charges()
                period_charge_id.count_charge = count


    # Generación de Cargos Automaticos
    @api.model
    def _cron_generate_charges_com(self):
        period_id = self.search([('state', '=', 'active')])
        com1 = self.env.ref('poi_x_aleman.student_case_active_6').id
        com2 = self.env.ref('poi_x_aleman.student_case_active_7').id
        charges = []
        count = 0
        if period_id:
            period_id = period_id[0]
            for c in period_id.chargeauto_ids:
                if c.auto:
                    charges.append(c.id)
            date = fields.Date.today()
            date_due = ""
            student_obj = self.env['op.student']
            student_ids = student_obj.search(
                [('state', '=', 'activo'), ('case_id', 'in', [com1, com2])])
            period_charge_id = period_id.chargeauto_ids.filtered(lambda x: x.date == date and x.auto is True)
            if period_charge_id:
                dd = charges.index(period_charge_id.id)
                if dd < len(charges) - 1:
                    charge_id = self.env['op.school.charge'].search([('id', '=', charges[dd + 1])])
                    date_due = charge_id.date
                elif dd == len(charges) - 1:
                    last_day = calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]
                    date_due = str(datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, last_day))
                period_charge_id = period_charge_id[0]
                count += student_ids.with_context(
                    date=date,
                    year_id=period_id.year_id.id,
                    date_due=date_due,
                    product_id=period_id.product_comercio_pension_id,
                    surcharge=period_id.surcharge,
                ).action_generate_charges()
                period_charge_id.count_charge = count
