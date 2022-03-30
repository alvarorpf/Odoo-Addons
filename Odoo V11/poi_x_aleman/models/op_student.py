# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
import calendar
from dateutil import parser
from odoo.exceptions import ValidationError, UserError


class OpStudent(models.Model):
    _name = 'op.student'
    _description = 'Alumno'
    _inherit = ['op.student', 'mail.thread', 'mail.activity.mixin']

    # FUNCIONES
    # Calculo de Edad

    @api.multi
    @api.depends('class_id')
    def _compute_class(self):
        for record in self:
            if record.class_id:
                record.course_id = (
                                           record.class_id.course_id and record.class_id.course_id.id) or False
                record.level_id = (
                                          record.class_id.course_id and record.class_id.course_id.level_id.id) or False

    @api.multi
    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                now = datetime.datetime.now()
                year = now.year
                birth_date = parser.parse(record.birth_date)
                age = year - birth_date.year
                record.age = age

    @api.multi
    @api.depends('first_name', 'middle_name', 'last_name', 'last_name2')
    def _compute_full_name(self):
        for record in self:
            name = str(record.last_name or '') + ' ' + str(record.last_name2 or '') + ' ' + str(
                record.first_name or '') + ' ' + str(record.middle_name or '')
            record.name = name
            record.full_name = name

    @api.multi
    @api.depends('family_code')
    def _compute_family(self):
        for record in self:
            if record.family_code:
                record.order_family()
                record.pension_calculation()

    @api.multi
    @api.depends('son_level_id', 'forced_level_id')
    def _compute_level(self):
        for r in self:
            if r.forced_level_id:
                r.oficial_level = r.forced_level_id.name
            if r.son_level_id and not r.forced_level_id:
                r.oficial_level = r.son_level_id.name

    state = fields.Selection([('activo', 'Activo'), ('inactivo', 'Inactivo')], 'Estado', required=True,
                             default='activo')
    case_id = fields.Many2one('op.student.case', 'Caso', required=True,
                              default=lambda self: self.env.ref('poi_x_aleman.student_case_active_2').id)
    student_code = fields.Char('Código de Alumno', default='Nuevo', required=True)
    family_code = fields.Many2one('op.family', 'Código de Familia', required=True)
    first_name = fields.Char('Primer Nombre', required=True)
    middle_name = fields.Char('Segundo  Nombre')
    last_name = fields.Char('Primer Apellido', required=True)
    last_name2 = fields.Char('Segundo Apellido')
    full_name = fields.Char('Nombre', compute='_compute_full_name', store=True)

    # INFORMACION GENERAL
    # Datos generales
    gender = fields.Selection([('m', 'Masculino'), ('f', 'Femenino'), ('o', 'Otro')], 'Género', required=True)
    first_nationality = fields.Many2one('res.country', 'Primera Nacionalidad', required=True)
    second_nationality = fields.Many2one('res.country', 'Segunda Nacionalidad')
    third_nationality = fields.Many2one('res.country', 'Tercera Nacionalidad')
    country_birth = fields.Many2one('res.country', 'País de Nacimiento')
    city_birth = fields.Char('Lugar de Nacimiento')
    religion = fields.Many2one('op.religion', 'Religión')
    # Datos de Identificacion
    ci = fields.Char('CI')
    issued_ci = fields.Selection(
        [('lp', 'LP'), ('or', 'OR'), ('pt', 'PT'), ('cb', 'CB'), ('ch', 'CH'), ('tj', 'TJ'), ('pa', 'PA'), ('be', 'BE'),
         ('sc', 'SC')])
    extension_ci = fields.Char('Extension')
    passport = fields.Char('Pasaporte')
    foreign_id = fields.Char('ID Extranjero')
    # Datos de Edad
    birth_date = fields.Date('Fecha de Nacimiento', required=True)
    age = fields.Integer('Edad', compute='_compute_age', store=True)
    # Datos de Contacto
    phone = fields.Char('Telefono')
    cellphone = fields.Char('Celular')
    email = fields.Char('Email')
    notes = fields.Text('Notas')

    # DATOS FAMILIARES
    parent_ids = fields.One2many('op.student.parents', 'student_id', string='Familiares')
    # family = fields.Many2many('op.parent.contact', related='family_code.parents_ids', readonly=True)

    # DATOS DE EDUCACION
    class_id = fields.Many2one('op.course', 'Clase')
    course_id = fields.Many2one('op.batch', compute='_compute_class', store=True, string='Curso')
    level_id = fields.Many2one('op.course.level', compute='_compute_class', store=True, string='Nivel de Curso')
    rude = fields.Char('Registro RUDE')
    # son_level = fields.Char('Nivel de Hijo', readonly=True, store=True, compute='_compute_family')
    # forced_level = fields.Char('Nivel Forzado', readonly=True, store=True, compute='_compute_family')
    son_level_id = fields.Many2one('account.op.charge.level', compute='_compute_family', string='Nivel de Hijo')
    oficial_level = fields.Char("Nivel de Hijo Oficial", compute="_compute_level", store=True)
    forced_level_id = fields.Many2one('account.op.charge.level', string='Nivel Forzado')
    high_date = fields.Date('Fecha de Alta', required=True, default=fields.datetime.now())
    low_date = fields.Date('Fecha de Baja', )
    kinder = fields.Boolean('Kinder Proxima Gestión')

    # DATOS DE PAGO
    scholarship_id = fields.Many2one('op.scholarship', 'Tipo de Beca/Descuento')
    payment_responsable = fields.Many2one('op.parent.contact', 'Responsable de Pago', required=True)
    discount = fields.Float('Descuento', related='scholarship_id.discount', readonly=True)
    discount_total = fields.Float('Descuento Total', related='scholarship_id.discount_total', readonly=True)
    apply_first = fields.Boolean('Aplica Primera Pension',
                                 related='scholarship_id.apply_first', readonly=True)
    apply_regular = fields.Boolean('Aplica Pension Regular',
                                   related='scholarship_id.apply_regular', readonly=True)
    first_pension = fields.Float('Primera Pension', compute='_compute_family')
    regular_pension = fields.Float('Pension Regular', compute='_compute_family')

    year_id = fields.Many2one('op.year', 'Gestión Escolar')
    charge_ids = fields.Many2one('acccount.op.charge', 'Cargos')
    pay_total_year = fields.Boolean('Pago Todo el Año', default=False)
    amount_discount = fields.Float('Descuento, Pago Año Adelantado')
    amount_year = fields.Float('Monto total Anual', compute='_compute_family', store=True)
    prepaid = fields.Boolean('Pago Anticipado', default=False)

    @api.model
    def create(self, values):
        values['name'] = str(values['last_name'] or '') + ' ' + str(values['last_name2'] or '') + ' ' + str(
            values['first_name'] or '') + ' ' + str(values['middle_name'] or '')
        if values['birth_date']:
            now = datetime.datetime.now()
            year = now.year
            birth_date = parser.parse(values['birth_date'])
            age = year - birth_date.year
            values['age'] = age
        record = super(OpStudent, self).create(values)
        return record

    @api.multi
    def unlink(self):
        for student in self:
            charge_obj = self.env['account.op.charge']
            medical_obj = self.env['op.medical.file']
            clinical_obj = self.env['op.clinical.record']
            exit_obj = self.env['op.exit.authorization']
            if student.state in 'activo':
                raise ValidationError(_("No puede eliminar un alumno en Activo."))
            charge_ids = charge_obj.search([('student_id', '=', student.id)])
            medical_ids = medical_obj.search([('student_id', '=', student.id)])
            clinical_ids = clinical_obj.search([('student_id', '=', student.id)])
            exit_ids = exit_obj.search([('student_id', '=', student.id)])
            if charge_ids or medical_ids or clinical_ids or exit_ids:
                raise ValidationError(_("No puede eliminar un alumno que cuente con registros en el sistema."))
            return models.Model.unlink(self)

    @api.constrains('birth_date')
    def _check_birthdate(self):
        for record in self:
            if record.birth_date:
                if record.birth_date > fields.Date.today():
                    raise ValidationError(_(
                        "Birth Date can't be greater than current date!"))

    @api.onchange('scholarship_id')
    def calculate_discount(self):
        for record in self:
            record.pension_calculation()

    @api.multi
    def order_family(self):
        order = []
        level = 1
        levels = {}
        schoolyear = self.env['op.school.period'].search([('state', '=', 'active')])
        com1 = self.env.ref('poi_x_aleman.batch_com1').id
        com2 = self.env.ref('poi_x_aleman.batch_com2').id
        if schoolyear:
            for s in schoolyear[0].nivel_ids:
                levels[int(s.level_id.name)] = s
            for record in self:
                if record.family_code.childs_ids:
                    sons = record.family_code.childs_ids
                    for son in sons:
                        if son.class_id:
                            if son.course_id.id != com1 and son.course_id.id != com2:
                                order.append(son)
                    a = sorted(order, key=lambda r: r.course_id.grade_id.sequence, reverse=True)
                    for b in a:
                        if b.state != 'inactivo':
                            if level in levels:
                                b.son_level_id = levels[level].level_id.id
                            level = level + 1
                else:
                    if self.state != 'inactivo':
                        if level in levels:
                            record.son_level_id = levels[level].level_id.id

    @api.multi
    def pension_calculation(self):
        for record in self:
            levels = {}
            level = []
            schoolyear = self.env['op.school.period'].search([('state', '=', 'active')])
            com1 = self.env.ref('poi_x_aleman.batch_com1').id
            com2 = self.env.ref('poi_x_aleman.batch_com2').id
            kinder = self.env.ref('poi_x_aleman.batch_grade_k1').id
            if schoolyear:
                for s in schoolyear.nivel_ids:
                    levels[int(s.level_id.name)] = s
                if record.forced_level_id:
                    if int(record.forced_level_id.name) in levels:
                        level = levels[int(record.forced_level_id.name)]
                else:
                    if int(record.son_level_id.name) in levels:
                        level = levels[int(record.son_level_id.name)]

                if record.course_id.id == com1 or record.course_id.id == com2:
                    record.first_pension = schoolyear.amount_camera
                    record.regular_pension = schoolyear.amount_camera
                elif level:
                    if record.course_id.grade_id.id == kinder:
                        record.first_pension = schoolyear.first_fee
                        record.regular_pension = level.amount_regular_fee
                    else:
                        record.first_pension = level.amount_first_fee
                        record.regular_pension = level.amount_regular_fee
                # record.amount_discount = level.discount_prepayment
                record.amount_year = (record.regular_pension * 9) + record.first_pension
                discount_first = 0
                discount_regular = 0
                if record.scholarship_id:
                    if record.scholarship_id.discount:
                        discount = (record.scholarship_id.discount / 100)
                        discount_first = record.first_pension * discount
                        discount_regular = record.regular_pension * discount
                    elif record.scholarship_id.discount_total:
                        discount_first = record.scholarship_id.discount_total
                        discount_regular = record.scholarship_id.discount_total
                    if record.scholarship_id.apply_first:
                        record.first_pension = record.first_pension - discount_first
                    if record.scholarship_id.apply_regular:
                        record.regular_pension = record.regular_pension - discount_regular

    @api.multi
    def promote_student(self, year_id):
        history_obj = self.env['op.course.history']
        charge_obj = self.env['account.op.charge']
        schoolyear = self.env['op.school.period'].search([('state', '=', 'active')])
        com1 = self.env.ref('poi_x_aleman.batch_com1').id
        com2 = self.env.ref('poi_x_aleman.batch_com2').id
        kin = self.env.ref('poi_x_aleman.student_case_active_5').id
        scholarship1 = self.env.ref('poi_x_aleman.scholarship_1').id
        scholarship2 = self.env.ref('poi_x_aleman.scholarship_2').id
        for s in self:
            history_obj.create({'student_id': s.id, 'course_id': s.class_id.id})
            if s.course_id.id == com1 or s.course_id.id == com2:
                if s.course_id.last_batch:
                    s.case_id = self.env.ref('poi_x_aleman.student_case_inactive_4').id
                    s.state = 'inactivo'
                else:
                    s.case_id = self.env.ref('poi_x_aleman.student_case_active_7').id
                    s.year_id = year_id.id
                    class_id = self.env['op.course'].search([('course_id', '=', com2), ('year_id', '=', year_id.id)])
                    if class_id:
                        s.class_id = class_id.id
            elif s.case_id.id == kin:
                class_id = self.env['op.course'].search([('course_id.name', '=', 'K1A'), ('year_id', '=', year_id.id)])
                s.class_id = class_id.id
                s.case_id = self.env.ref('poi_x_aleman.student_case_active_2').id
                s.year_id = year_id.id
            elif s.course_id.last_batch:
                s.case_id = self.env.ref('poi_x_aleman.student_case_inactive_1').id
                s.state = 'inactivo'
            else:
                charge_ids = charge_obj.search(
                    [('student_id', '=', s.id), ('state', '=', 'wait'), ('date_due', '<', fields.Date.today())])
                if charge_ids:
                    amount_due = sum(charge_ids.mapped('amount_total'))
                    if amount_due > schoolyear.amount_limit:
                        s.case_id = self.env.ref('poi_x_aleman.student_case_active_1').id
                    else:
                        s.case_id = self.env.ref('poi_x_aleman.student_case_active_2').id
                else:
                    s.case_id = self.env.ref('poi_x_aleman.student_case_active_2').id
                s.year_id = year_id.id
                class_id = s.class_id.promote_course(year_id)
                if class_id:
                    s.class_id = class_id.id
                if s.scholarship_id.id != scholarship1 or s.scholarship_id.id != scholarship2:
                    s.scholarship_id = None

    @api.onchange('family_code')
    def get_payment_responsable(self):
        for record in self:
            record.forced_level_id = False
            if 'default_family_code' in record._context:
                return {
                    'domain': {
                        'payment_responsable':
                            [
                                ('family_id', '=', record._context['default_family_code'] or False)
                            ]
                    }
                }
            elif record.family_code:
                return {
                    'domain': {
                        'payment_responsable':
                            [
                                ('family_id', '=', (self.family_code and self.family_code.id) or False)
                            ]
                    }
                }

    @api.model
    def actualizar_edad(self):
        alumnos = self.env['op.student'].search([])
        for alumno in alumnos:
            if alumno.birth_date:
                alumno._compute_age()

    @api.model
    def actualizar_niveles(self):
        alumnos = self.env['op.student'].search([])
        level = self.env['account.op.charge.level']
        for alumno in alumnos:
            if alumno.son_level:
                level_id = level.search([('name', '=', str(alumno.son_level))])
                alumno.son_level_id = level_id

    @api.multi
    def name_get(self):
        return [(template.id, '%s%s' % (template.name, template.student_code and '[%s] ' % template.student_code or ''))
                for template in self]

    def action_view_charges(self):
        return {
            'name': 'Cargos del Alumno',
            'domain': [('student_id', '=', self.id)],
            'res_model': 'account.op.charge',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 20
        }

    def action_view_courses(self):
        return {
            'name': 'Historial de Cursos',
            'domain': [('student_id', '=', self.id)],
            'res_model': 'op.course.history',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 20
        }

    @api.multi
    def action_create_charges(self):
        charge_obj = self.env['account.op.charge']
        invoice_obj = self.env['account.invoice.line']
        charge_ids = []
        base = calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]
        first_day = str(datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1))
        last_day = str(datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, base))
        for s in self:
            if s.case_id.apply_charge:
                charge = charge_obj.search(
                    [('student_id', '=', s.id), ('state', '!=', 'cancel'), ('date', '>=', first_day),
                     ('date', '<=', last_day), ('product_id.concept_type', '=', 'pension')])
                product_id = self.env.context.get('product_id', False)
                if product_id.concept_type != 'pension' or product_id.charge_type == 'payment':
                    month_obj = self.env['op.month']
                    date = datetime.datetime.strptime(self.env.context.get('date'), '%Y-%m-%d')
                    month_ids = month_obj.search([('sequence', '=', date.month)])
                    if month_ids:
                        month_id = month_ids[0].id
                    account = invoice_obj.get_invoice_line_account('out_invoice',
                                                                   self.env.context.get('product_id', False),
                                                                   False, self.env.user.company_id)
                    analytic_id = s.course_id.level_id.analytic_id.id
                    charge_id = charge_obj.create({
                        'type_charge': self.env.context.get('type_charge', False),
                        'student_id': s.id,
                        'month_id': month_id,
                        'year_id': self.env.context.get('year_id', False),
                        'date': self.env.context.get('date', False),
                        'date_due': self.env.context.get('date_due', False),
                        'product_id': self.env.context.get('product_id', False).id,
                        'name': self.env.context.get('product_id', False).name,
                        'amount': self.env.context.get('amount', 0),
                        'account_id': account and account.id or False,
                        'analytic_id': analytic_id or False,
                    })
                    charge_id.onchange_product_id()
                    charge_id.action_send()
                    charge_ids.append(charge_id.id)
                    return charge_ids
                elif not charge:
                    month_obj = self.env['op.month']
                    date = datetime.datetime.strptime(self.env.context.get('date'), '%Y-%m-%d')
                    month_ids = month_obj.search([('sequence', '=', date.month)])
                    if month_ids:
                        month_id = month_ids[0].id
                    account = invoice_obj.get_invoice_line_account('out_invoice',
                                                                   self.env.context.get('product_id', False),
                                                                   False, self.env.user.company_id)
                    analytic_id = self.env.context.get('product_id', False).id,
                    if not analytic_id:
                        analytic_id = s.course_id.level_id.analytic_id.id
                    charge_id = charge_obj.create({
                        'type_charge': self.env.context.get('type_charge', False),
                        'student_id': s.id,
                        'month_id': month_id,
                        'year_id': self.env.context.get('year_id', False),
                        'date': self.env.context.get('date', False),
                        'date_due': self.env.context.get('date_due', False),
                        'product_id': self.env.context.get('product_id', False).id,
                        'name': self.env.context.get('product_id', False).name,
                        'amount': self.env.context.get('amount', 0),
                        'account_id': account and account.id or False,
                        'analytic_id': analytic_id or False,
                    })
                    charge_id.onchange_product_id()
                    charge_id._compute_amount_diff()
                    charge_id.action_send()
                    charge_ids.append(charge_id.id)
                    return charge_ids
                else:
                    raise UserError('Atención! Ya existe un cargo generado de pensiones para este mes.')

    @api.multi
    def action_generate_charges(self):
        charge_obj = self.env['account.op.charge']
        invoice_obj = self.env['account.invoice.line']
        count = 0
        base = calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]
        first_day = str(datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1))
        last_day = str(datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, base))
        for s in self:
            if s.case_id.apply_charge:
                charge = charge_obj.search(
                    [('student_id', '=', s.id), ('state', '!=', 'cancel'), ('date', '>=', first_day),
                     ('date', '<=', last_day), ('product_id.concept_type', '=', 'pension')])
                if not charge:
                    month_obj = self.env['op.month']
                    date = datetime.datetime.strptime(self.env.context.get('date'), '%Y-%m-%d')
                    month_ids = month_obj.search([('sequence', '=', date.month)])
                    if month_ids:
                        month_id = month_ids[0].id
                    account = invoice_obj.get_invoice_line_account('out_invoice',
                                                                   self.env.context.get('product_id', False),
                                                                   False, self.env.user.company_id)
                    analytic_id = s.course_id.level_id.analytic_id.id
                    charge_id = charge_obj.create({
                        'type_charge': self.env.ref('poi_x_aleman.type_charge_pension').id,
                        'student_id': s.id,
                        'month_id': month_id,
                        'year_id': self.env.context.get('year_id', False),
                        'date': self.env.context.get('date', False),
                        'date_due': self.env.context.get('date_due', False),
                        'product_id': self.env.context.get('product_id', False).id,
                        'name': self.env.context.get('product_id', False).name,
                        'amount': self.env.context.get('product_id', False).lst_price,
                        'account_id': account and account.id or False,
                        'analytic_id': analytic_id or False,
                    })
                    charge_id.onchange_product_id()
                    charge_id._compute_amount_diff()
                    charge_id.action_send()
                    count += 1
        return count

    @api.multi
    def service_get_students(self, fields=False):
        partner_id = self.env.user.partner_id
        contact_obj = self.env['op.parent.contact']
        contact_id = contact_obj.search([('partner_id', '=', partner_id.id)])
        if contact_id:
            family_ids = contact_id.family_id.mapped('id')
        else:
            return []
        charge_ids = self.search([('family_code', 'in', family_ids)])
    
        result = charge_ids.read(fields)
        if len(result) <= 1:
            return result

        # reorder read
        index = {vals['id']: vals for vals in result}
        return [index[record.id] for record in charge_ids if record.id in index]


class OpStudentP(models.Model):
    _name = 'op.student.parents'
    _description = 'Familiares'

    @api.multi
    def _compute_code_family(self):
        for r in self:
            if r.student_id:
                r.family_id = r.student_id.family_code.id

    student_id = fields.Many2one('op.student', 'Alumno')
    family_id = fields.Many2one('op.family', 'Familia', compute="_compute_code_family", store=True)
    parent_id = fields.Many2one('op.parent.contact', 'Familiar')
    relationship_id = fields.Many2one('op.relationship', 'Parentesco')

    @api.onchange('parent_id')
    def get_parents(self):
        for record in self:
            if 'family_id' in record._context:
                return {
                    'domain': {
                        'parent_id':
                            [
                                ('family_id', '=', record._context['family_id'] or False)
                            ]
                    }
                }
            elif record.student_id.family_code:
                return {
                    'domain': {
                        'parent_id':
                            [
                                ('family_id', '=',
                                 (record.student_id.family_code and record.student_id.family_code.id) or False)
                            ]
                    }
                }
