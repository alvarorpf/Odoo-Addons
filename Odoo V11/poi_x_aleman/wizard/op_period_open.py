# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError, Warning


class OpPeriodOpen(models.TransientModel):
    _name = "op.period.open"

    new_year_id = fields.Many2one('op.year', 'Nuevo Año Escolar')
    copy_year_id = fields.Many2one('op.year', 'Copiar de Año Escolar')
    account_kinder_pension_id = fields.Many2one('account.account', 'Pensiones Cobradas Gestion Anterior')
    account_kinder_material_id = fields.Many2one('account.account', 'Materiales Cobrados Gestion Anterior')
    account_excedente_id = fields.Many2one('account.account', 'Pensiones Colegio Anticipado')
    journal_id = fields.Many2one('account.journal', 'Diario')

    @api.onchange('new_year_id')
    def onchange_new_year_id(self):
        if self.new_year_id:
            last_year_id = self.new_year_id.get_last_year()
            if last_year_id:
                self.copy_year_id = last_year_id.id
            else:
                self.copy_year_id = False

    @api.multi
    def action_create_period(self):
        period_obj = self.env['op.school.period']
        course_obj = self.env['op.course']
        period_ids = period_obj.search([('year_id', '=', self.copy_year_id.id), ('state', 'in', ['draft', 'active'])])
        charge_ids = []
        nivel_ids = []
        chargeauto_ids = []
        if period_ids:
            period_id = period_ids[0]
            new_period_id = period_id.copy()
            new_period_id.date_from = ""
            new_period_id.date_to = ""
            new_period_id.date_fm = ""
            new_period_id.day_initial = ""
            new_period_id.day_initial_camera = ""
            new_period_id.year_id = self.new_year_id.id
            for c in period_id.charge_ids:
                charge_ids.append([0, 0, {
                    'year_id': self.new_year_id.id,
                    'month_id': c.month_id,
                    'auto': c.auto,
                    'date': "",
                }])
            new_period_id.charge_ids = charge_ids
            for n in period_id.nivel_ids:
                nivel_ids.append([
                    0, 0, {
                        'level_id': n.level_id.id,
                        'amount_first_fee': n.amount_first_fee,
                        'amount_regular_fee': n.amount_regular_fee,
                        'discount_prepayment': n.discount_prepayment,
                    }
                ])
            new_period_id.nivel_ids = nivel_ids
            for ca in period_id.chargeauto_ids:
                chargeauto_ids.append([
                    0, 0, {
                        'year_id': self.new_year_id.id,
                        'month_id': ca.month_id,
                        'auto': ca.auto,
                    }
                ])
            new_period_id.chargeauto_ids = chargeauto_ids
        course_ids = course_obj.search([('year_id', '=', self.copy_year_id.id), ('state', 'in', ['activo'])])
        if course_ids:
            for course_id in course_ids:
                new_course_id = course_id.copy()
                new_course_id.year_id = self.new_year_id.id
                course_id.state = 'historico'
            period_id.state = 'archive'
            return {
                'name': _('Dato Maestro Gestion Escolar'),
                'domain': [('id', '=', new_period_id.id)],
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'op.school.period',
                # 'target': 'new',
                'view_id': False,
                'type': 'ir.actions.act_window',
            }

    @api.multi
    def action_promote_students(self):
        student_obj = self.env["op.student"]
        student_ids = student_obj.search([('state', '=', 'activo')])
        for student_id in student_ids:
            student_id.promote_student(self.new_year_id)
        period_obj = self.env['op.school.period'].search([('year_id', '=', self.new_year_id.id)])
        if period_obj:
            period_obj.state = 'active'
        return {
            'name': _('Finalizar Asistente de Apertura'),
            # 'domain': [('id', '=', new_period_id.id)],
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'op.period.open',
            'target': 'new',
            'view_id': self.env.ref('poi_x_aleman.op_period_open_wiz4_view_form').ids,
            'type': 'ir.actions.act_window',
            'context': {'copy_year_id': self.copy_year_id.id},
        }

    @api.multi
    def action_accounting_opening(self):
        for s in self:
            paid_charges = self.env['op.request.charge'].search([('state', '=', 'done')])
            pension = self.env['account.account'].search([('code', '=', '21512')])
            material = self.env['account.account'].search([('code', '=', '21513')])
            if paid_charges:
                move_lines_p = []
                move_lines_m = []
                for p in paid_charges:
                    move = p.invoice_id.move_id
                    if move:
                        lines = move.line_ids
                        if lines:
                            for l in lines:
                                if l.account_id == pension:
                                    move_lines_p.append((0, 0, {
                                        'partner_id': l.partner_id.id,
                                        'name': 'Pensiones Kinder Gestion Anterior',
                                        'debit': l.credit,
                                        'credit': 0,
                                        'account_id': l.account_id.id,
                                    }))
                                    move_lines_p.append((0, 0, {
                                        'partner_id': l.partner_id.id,
                                        'name': 'Pensiones Kinder Gestion Anterior',
                                        'debit': 0,
                                        'credit': l.credit,
                                        'account_id': s.account_kinder_pension_id.id,
                                    }))
                                elif l.account_id == material:
                                    move_lines_m.append((0, 0, {
                                        'partner_id': l.partner_id.id,
                                        'name': 'Materiales Kinder Gestion Anterior',
                                        'debit': l.credit,
                                        'credit': 0,
                                        'account_id': l.account_id.id,
                                    }))
                                    move_lines_m.append((0, 0, {
                                        'partner_id': l.partner_id.id,
                                        'name': 'Materiales Kinder Gestion Anterior',
                                        'debit': 0,
                                        'credit': l.credit,
                                        'account_id': s.account_kinder_material_id.id,
                                    }))
                move1 = self.env['account.move'].create({
                    'ref': 'Pensiones Kinder Gestion Anterior',
                    'journal_id': s.journal_id.id,
                    'date': fields.datetime.now(),
                    'line_ids': move_lines_p,
                })
                move1.post()
                move2 = self.env['account.move'].create({
                    'ref': 'Materiales Kinder Gestion Anterior',
                    'journal_id': s.journal_id.id,
                    'date': fields.datetime.now(),
                    'line_ids': move_lines_m,
                })
                move2.post()
        return {
            'name': _('Finalizar Asistente de Apertura'),
            # 'domain': [('id', '=', new_period_id.id)],
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'op.period.open',
            'target': 'new',
            'view_id': self.env.ref('poi_x_aleman.op_period_open_wiz3_view_form').ids,
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def _get_default_journal(self):
        if self.env.context.get('default_journal_type'):
            return self.env['account.journal'].search([('company_id', '=', self.env.user.company_id.id),
                                                       ('type', '=', self.env.context['default_journal_type'])],
                                                      limit=1).id
