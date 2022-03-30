from odoo import models, fields, api
from datetime import datetime, date, time, timedelta


class OpBookLoan(models.Model):
    _name = 'op.book.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Prestamo de Libro'

    @api.multi
    @api.depends('loan_term_id', 'broadcast_date')
    def _compute_due_date(self):
        for r in self:
            if r.loan_term_id:
                due_date = datetime.strptime(r.broadcast_date, '%Y-%m-%d') + timedelta(r.loan_term_id.days_available)
                r.due_date = due_date.date()

    @api.multi
    @api.depends('type', 'student_id', 'teacher_id', 'employee_id')
    def _compute_lender(self):
        for r in self:
            if r.type == 'student':
                r.lender_name = r.student_id.full_name
                r.code = r.student_id.student_code
                r.teacher_id = ''
                r.employee_id = ''
            if r.type == 'teacher':
                r.lender_name = r.teacher_id.full_name
                r.code = r.teacher_id.initials
                r.student_id = ''
                r.employee_id = ''
            if r.type == 'employee':
                r.lender_name = r.employee_id.name
                r.student_id = ''
                r.teacher_id = ''

    @api.multi
    @api.depends('student_id')
    def _compute_class(self):
        for record in self:
            if record.student_id and record.student_id.class_id:
                record.level_id = (
                                          record.student_id.class_id.course_id and record.student_id.class_id.course_id.level_id.id) or False

    name = fields.Char('Nombre', size=64, required=True, default='Nuevo')
    lender_name = fields.Char(compute="_compute_lender", store=True, string='Alumno/Profesor/Empleado')
    state = fields.Selection(
        [('draft', 'Borrador'), ('issued', 'Emitido'), ('late', 'Atrasado'), ('returned', 'Devuelto')], 'Estado',
        default='draft')
    media_id = fields.Many2one('op.media', 'Libro')
    media_unit_id = fields.Many2one('op.media.unit', 'Unidad')
    media_type_id = fields.Many2one(related='media_unit_id.media_type_id', readonly=True, store=True,
                                    string='Tipo de Medio')
    barcode = fields.Char('Código de Barras', size=20)
    type = fields.Selection([('student', 'Alumno'), ('teacher', 'Profesor'), ('employee', 'Empleado')], string="Tipo")
    code = fields.Char('Código', compute="_compute_lender")
    loan_term_id = fields.Many2one('op.loan.term', 'Plazo de Préstamo')
    broadcast_date = fields.Date('Fecha de Emisión', default=fields.Datetime.now)
    due_date = fields.Date('Fecha de Vencimiento', compute='_compute_due_date', store=True)
    return_date = fields.Date('Fecha de Retorno')
    days_late = fields.Integer('Dias de Retraso')
    student_id = fields.Many2one('op.student', 'Alumno')
    level_id = fields.Many2one('op.course.level', compute='_compute_class', string="Nivel de Curso")
    teacher_id = fields.Many2one('op.faculty', 'Profesor')
    employee_id = fields.Many2one('hr.employee', 'Administrativo')

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'sequence.book.loan') or '/'
        return super(OpBookLoan, self).create(vals)

    @api.onchange('barcode')
    def search_unit(self):
        for r in self:
            if r.barcode:
                media_unit_obj = self.env['op.media.unit']
                media_unit_id = media_unit_obj.search([('barcode', '=', r.barcode), ('state', '=', 'available')])
                if media_unit_id:
                    r.media_id = media_unit_id.media_id.id
                    r.media_unit_id = media_unit_id.id

    @api.onchange('media_id')
    def get_units(self):
        for record in self:
            if record.media_id:
                return {
                    'domain': {
                        'media_unit_id':
                            [
                                ('media_id', '=', (self.media_id and self.media_id.id) or False),
                                ('state', '=', 'available')
                            ]
                    }
                }

    @api.onchange('loan_term_id')
    def get_terms(self):
        for record in self:
            if record.loan_term_id:
                return {
                    'domain': {
                        'loan_term_id':
                            [
                                ('active', '=', True),
                            ]
                    }
                }

    @api.onchange('media_unit_id')
    def get_info(self):
        for r in self:
            if r.media_unit_id:
                r.media_type_id = r.media_unit_id.media_type_id.id
                if not r.barcode:
                    r.barcode = r.media_unit_id.barcode

    @api.multi
    def issue_book(self):
        for r in self:
            if r.media_unit_id:
                r.media_unit_id.state = 'borrowed'
                r.state = 'issued'

    @api.model
    def _cron_overdue(self):
        unit_obj = self.env['op.book.loan']
        units = unit_obj.search([('state', 'in', ['issued', 'late'])])
        if units:
            for u in units:
                if u.due_date < fields.Date.today():
                    if u.state == 'issued':
                        u.state = 'late'
                        u.media_unit_id.state = 'overdue'
                        u.days_late = u.days_late + 1
                    else:
                        u.days_late = u.days_late + 1
                if u.loan_term_id.user_reminder_id and u.loan_term_id.user_reminder_id.id:
                    msg = "Prestamo de Libro %s venció su fecha de retorno. @(%s) verificar." % (u.name, u.loan_term_id.user_reminder_id.login)
                    new_msg = u.message_post(body=msg, partner_ids=[(4, u.loan_term_id.user_reminder_id.id)])
                    new_msg.sudo().write({'needaction_partner_ids': [(4, u.loan_term_id.user_reminder_id.id)]})

