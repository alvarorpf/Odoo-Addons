# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OpStudent(models.Model):
    _inherit = 'op.student'

    def action_view_book_loan(self):
        return {
            'name': 'Prestamos de Libro',
            'domain': [('student_id', '=', self.id)],
            'res_model': 'op.book.loan',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 20
        }