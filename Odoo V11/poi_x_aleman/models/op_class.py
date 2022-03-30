# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime
import datetime
import codecs
import os
import base64
import contextlib
import io
import csv
import re
# from cStringIO import StringIO
from io import StringIO

try:
    import xlwt
except ImportError:
    xlwt = None


class OpCourse(models.Model):
    _inherit = 'op.course'
    _rec_name = 'class_name'

    @api.multi
    @api.depends('course_id', 'year_id')
    def _compute_name(self):
        for record in self:
            if record.course_id and record.year_id:
                name = str(record.course_id.name or '') + '/' + str(record.year_id.name or '')
                record.name = name
                record.class_name = name

    code = fields.Char('Code', size=16, required=False)
    section = fields.Char('Section', size=32, required=False)
    # fees_term_id = fields.Many2one('op.fees.terms', required=False)
    state = fields.Selection([
        ('activo', 'Activo'),
        ('inactivo', 'inactivo'),
        ('historico', 'Histórico'),
    ], string='Estado', default='activo', index=True, readonly=True)

    class_name = fields.Char('Clase', compute='_compute_name', store=True)
    course_id = fields.Many2one('op.batch', 'Curso', required=True)
    year_id = fields.Many2one('op.year', 'Gestión Escolar', required=True)
    course_responsable_1 = fields.Many2one('op.faculty', 'Responsable de Curso 1', required=True)
    course_responsable_2 = fields.Many2one('op.faculty', 'Responsable de Curso 2')

    @api.multi
    def name_get(self):
        return [(template.id, '%s%s' % (template.course_id.name, template.year_id.name and '/%s' % template.year_id.name or ''))
                for template in self]

    @api.multi
    def change_status(self):
        if not self:
            return False
        elif self.state == 'activo':
            self.write({'state': 'inactivo'})
            return True
        else:
            self.write({'state': 'activo'})
            return True

    def action_view_all_students(self):
        return {
            'name': 'Estudiantes',
            'domain': [('class_id', '=', self.id)],
            'res_model': 'op.student',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 20
        }

    @api.multi
    def promote_course(self, year_id):
        grade_obj = self.env['op.batch.grade']
        course_id = False
        for s in self:
            s.state = 'historico'
            next_grade = grade_obj.search(
                [('sequence', '=', s.course_id.grade_id.sequence + 1)])
            course_id = s.search([('course_id', '=', s.course_id.next_batch(next_grade)), ('year_id', '=', year_id.id)])
            if not course_id:
                course_id = False
        return course_id

    @api.multi
    def action_export_contacts(self):
        for record in self:
            export_obj = self.env['report.export']
            context = {}
            student_obj = self.env['op.student']
            context.update({
                'tab': 'Contacto_Familiares',
                'title': 'Contacto Familiares',
            })
            headers = []
            cells = []

            students = student_obj.search([('class_id', '=', record.id)])

            if students:
                for student in students:
                    count = 0
                    for p in student.parent_ids:
                        if count == 0:
                            cells.append([
                                student and student.student_code or "",
                                student.family_code and student.family_code.name or "",
                                student and student.full_name or "",
                                student.class_id and student.class_id.name or "",
                                p.parent_id and p.parent_id.name or "",
                                p.relationship_id and p.relationship_id.name or "",
                                p.parent_id and p.parent_id.phone or "",
                                p.parent_id and p.parent_id.work_phone or "",
                                p.parent_id and p.parent_id.cellphone or "",
                                p.parent_id and p.parent_id.work_email or "",
                                p.parent_id and p.parent_id.email or "",
                            ])
                            count += 1
                        else:
                            cells.append([
                                "",
                                "",
                                "",
                                "",
                                p.parent_id and p.parent_id.name or "",
                                p.relationship_id and p.relationship_id.name or "",
                                p.parent_id and p.parent_id.phone or "",
                                p.parent_id and p.parent_id.work_phone or "",
                                p.parent_id and p.parent_id.cellphone or "",
                                p.parent_id and p.parent_id.work_email or "",
                                p.parent_id and p.parent_id.email or "",
                            ])
            outputxls = export_obj.gen_xls(headers, cells, context)
            output64 = base64.encodestring(outputxls)
            export_id = export_obj.create({
                'name': 'ReporteContactoPadres.xls',
                'filename': 'ReporteContactoPadres.xls',
                'file': output64
            })
            if export_id:
                return {
                    'name': 'Descargar Reporte',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': False,
                    'res_model': 'report.export',
                    'domain': [],
                    'res_id': export_id.id,
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }


class OpCourseHistory(models.Model):
    _name = "op.course.history"
    _description = 'Historial de Curso'

    course_id = fields.Many2one('op.course', 'Clase')
    student_id = fields.Many2one('op.student', 'Estudiante')
    class_id = fields.Many2one('op.batch', compute='_compute_class', string='Curso')
    level_id = fields.Many2one('op.course.level', compute='_compute_class', string='Nivel')
    year_id = fields.Many2one('op.year', compute='_compute_class', string='Año Escolar')

    @api.multi
    @api.depends('course_id')
    def _compute_class(self):
        for record in self:
            if record.course_id:
                record.class_id = (record.course_id.course_id and record.course_id.course_id.id) or False
                record.level_id = (record.course_id.course_id.level_id and record.course_id.course_id.level_id.id) or False
                record.year_id = (record.course_id.year_id and record.course_id.year_id.id) or False
