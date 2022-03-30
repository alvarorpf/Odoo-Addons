# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ReturnBook(models.TransientModel):
    _name = "return.book"

    @api.multi
    @api.depends('book_loan_id')
    def _compute_book_loan(self):
        for r in self:
            if r.book_loan_id:
                r.media_unit_id = r.book_loan_id.media_unit_id.id
                r.barcode = r.book_loan_id.barcode

    book_loan_id = fields.Many2one('op.book.loan', 'Prestamo de Libro')
    media_unit_id = fields.Many2one('op.media.unit', 'Unidad de Libro', compute='_compute_book_loan')
    barcode = fields.Char('Código de Barras', compute='_compute_book_loan')
    returned_date = fields.Date('Fecha de Retorno', required=True, default=fields.Datetime.now)
    media_state_id = fields.Many2one('op.book.state', 'Estado de Libro')
    observations = fields.Text('Observaciones')

    @api.multi
    def return_unit(self):
        for r in self:
            history_obj = self.env['op.media.unit.history']
            if r.book_loan_id:
                r.book_loan_id.state = 'returned'
                r.media_unit_id.state = 'available'
                r.book_loan_id.return_date = r.returned_date
                history_obj.create({
                    'media_unit_id': r.media_unit_id.id,
                    'media_state_id': r.media_state_id.id,
                    'out_date': r.book_loan_id.broadcast_date,
                    'return_date': r.returned_date,
                    'observations': r.observations,
                    'student_id': r.book_loan_id.student_id and r.book_loan_id.student_id.id or False,
                    'teacher_id': r.book_loan_id.teacher_id and r.book_loan_id.teacher_id.id or False,
                    'employee_id': r.book_loan_id.employee_id and r.book_loan_id.employee_id.id or False,
                    'type': r.book_loan_id.type,
                })
