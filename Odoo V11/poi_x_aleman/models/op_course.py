# -*- coding: utf-8 -*-

from odoo import models, fields, api

class OpCourseLvel(models.Model):
    _name = 'op.course.level'

    name = fields.Char('Nombre', required=True)
    analytic_id = fields.Many2one('account.analytic.account', 'Cuenta Analítica', required=True)

class OPBatchGrade(models.Model):
    _name = "op.batch.grade"

    name = fields.Char('Grado')
    sequence = fields.Integer('Secuencia')
    last_batch = fields.Boolean('Ultima Clase', default=False)

class OpBatchParallel(models.Model):
    _name = "op.batch.parallel"

    name = fields.Char('Paralelo')
    sequence = fields.Integer('Secuencia')

class OpBatch(models.Model):
    _inherit = 'op.batch'

    @api.multi
    def _compute_last_batch(self):
        for s in self: 
            s.last_batch = s.grade_id.last_batch

    code = fields.Char('Code', size=16, required=False)
    start_date = fields.Date(required=False, default=fields.Date.today())
    end_date = fields.Date(required=False, default=fields.Date.today())
    course_id = fields.Many2one('op.course', 'Course', required=False)
    grade_id = fields.Many2one('op.batch.grade', 'Grado', required=False)
    last_batch = fields.Boolean('Ultima Clase', compute="_compute_last_batch")
    parallel_id = fields.Many2one('op.batch.parallel', 'Paralelo', required=False)
    level_id = fields.Many2one('op.course.level', 'Nivel de Curso')

    @api.multi
    def next_batch(self, grade_id):
        batch_ids = self.search([('grade_id', '=', grade_id.id), ('parallel_id', '=', self.parallel_id.id)])
        if batch_ids:
            batch_id = batch_ids[0]
            return batch_id.id
        else:
           return False
