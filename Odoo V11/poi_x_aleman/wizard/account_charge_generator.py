# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime, date, time, timedelta


class AccountCharge(models.TransientModel):
    _name = "account.op.charge.wiz"

    type = fields.Selection(
        string="Tipo",
        selection=[
            ('student', 'Alumno'),
            ('course', 'Clase'),
            ('grade', 'Grado'),
            ('level', 'Nivel'),
            ('all', 'Todos'),
        ], required=True)

    state = fields.Selection([('activo', 'Activo'), ('inactivo', 'Inactivo')], 'Estado', readonly=True,
                             default='activo')
    case_id = fields.Many2one('op.student.case', 'Caso', required=True, default=lambda self: self.env['op.student.case'].search([('name', '=', 'Inscrito')]))
    student_id = fields.Many2one('op.student', 'Alumno', domain="[('state', '=', 'activo')]")
    course_id = fields.Many2one('op.course', 'Curso')
    grade_id = fields.Many2one('op.batch.grade', 'Grado')
    level_id = fields.Many2one('op.course.level', 'Nivel de Curso')
    type_charge = fields.Many2one('account.op.charge.type', 'Tipo de Cargo', required=True)
    product_id = fields.Many2one('product.product', 'Producto', required=True)
    price = fields.Float('Precio', required=True)
    year_id = fields.Many2one('op.year', 'Año Escolar', default=lambda self: self.env['op.school.period'].search([('state', '=', 'active')]).year_id.id, readonly=True)
    date = fields.Date('Fecha', default=fields.Date.today(), required=True)
    date_due = fields.Date('Fecha de Vencimiento', default=fields.Date.today(), required=True)
    analytic_id = fields.Many2one('account.analytic.account', 'Cuenta Analítica')

    @api.multi
    def action_generate(self):
        student_obj = self.env['op.student']
        student_ids = student_obj.search([('state', '=', 'activo'), ('case_id', '=', self.case_id.id)])
        student_ids = student_ids.with_context(type_charge=self.type_charge.id, date=self.date, date_due=self.date_due, product_id=self.product_id, year_id=self.year_id.id, analytic_id=self.analytic_id, amount=self.price)
        if not self.type:
            raise UserError('Debe Seleccionar al menos un TIPO')
        if self.type == 'student':
            if not self.student_id:
                raise UserError('Debe seleccionar al menos un Alumno.')
            charge_ids = self.student_id.with_context(type_charge=self.type_charge.id, date=self.date, date_due=self.date_due, product_id=self.product_id, year_id=self.year_id.id, amount=self.price).action_create_charges()
        elif self.type == 'course':
            if not self.course_id:
                raise UserError('Debe seleccionar al menos un Curso.')
            students = student_ids.filtered(lambda s: s.class_id.id == self.course_id.id)
            for student in students:
                student.action_create_charges()
        elif self.type == 'grade':
            if not self.grade_id:
                raise UserError('Debe seleccionar al menos un Grado.')
            students = student_ids.filtered(lambda s: s.course_id.grade_id.id == self.grade_id.id)
            for student in students:
                student.action_create_charges()
        elif self.type == 'level':
            if not self.level_id:
                raise UserError('Debe seleccionar al menos un Nivel.')
            students = student_ids.filtered(lambda s: s.level_id.id == self.level_id.id)
            for student in students:
                student.action_create_charges()
        elif self.type == 'all':
            for student in student_ids:
                student.action_create_charges()

    @api.onchange('product_id')
    def product_price(self):
        for r in self:
            r.price = r.product_id.lst_price

    @api.onchange('type')
    def clear_ids(self):
        if self.type == 'student':
            self.course_id = False
            self.grade_id = False
            self.level_id = False
        elif self.type == 'course':
            self.student_id = False
            self.grade_id = False
            self.level_id = False
        elif self.type == 'grade':
            self.student_id = False
            self.course_id = False
            self.level_id = False
        elif self.type == 'level':
            self.student_id = False
            self.course_id = False
            self.grade_id = False
        elif self.type == 'all':
            self.student_id = False
            self.course_id = False
            self.grade_id = False
            self.level_id = False

    @api.onchange('student_id', 'course_id', 'grade_id', 'level_id')
    def analytic_account(self):
        self.analytic_id = False
        if self.student_id:
            self.analytic_id = self.student_id.course_id.level_id.analytic_id
        elif self.course_id:
            self.analytic_id = self.course_id.course_id.level_id.analytic_id
        elif self.grade_id:
            course = self.env['op.batch'].search([('grade_id', '=', self.grade_id.id)])
            self.analytic_id = course[0].level_id.analytic_id
        elif self.level_id:
            self.analytic_id = self.level_id.analytic_id

