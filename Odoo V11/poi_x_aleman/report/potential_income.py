from odoo import api, models

class ReportPotentialIncome(models.AbstractModel):
    _name = 'report.poi_x_aleman.potential_income_report_template'

    @api.model
    def get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('poi_x_aleman.potential_income_report_template')
        act_reg = self.env.ref('poi_x_aleman.student_case_active_4').id
        act_com = self.env.ref('poi_x_aleman.student_case_active_6').id
        beca_loc = self.env.ref('poi_x_aleman.scholarship_1').id
        beca_ext = self.env.ref('poi_x_aleman.scholarship_2').id
        period_id = self.env['op.school.period'].search([('state', '=', 'active')])
        levels = {}
        for s in period_id[0].nivel_ids:
            levels[s.level_id.name] = s
        kinder = {}
        regular = {}
        comerce = {}
        beca_local = {}
        becas = {}
        familys = self.env['op.family'].search([])
        com = self.env['op.course.level'].search([('name', '=', 'COMERCIO')])
        ini = self.env['op.course.level'].search([('name', '=', 'INICIAL')])

        students = self.env['op.student'].search([('case_id', '=', act_reg)], order='son_level_id desc')
        comerce_students = self.env['op.student'].search([('course_id.level_id', '=', com.id), ('case_id', '=', act_com)])

        kinder_students = students.filtered(lambda x: x.course_id.level_id.id == ini.id)
        regular_students = students.filtered(lambda x: x.course_id.level_id.id != ini.id and x.course_id.level_id.id != com.id)

        total_students = len(students) + len(comerce_students)
        total_comerce = total_students - len(comerce_students)
        total_familys = len(familys)

        for ks in kinder_students:
            if ks.son_level_id.name not in kinder:
                if ks.scholarship_id:
                    if ks.scholarship_id.id == beca_ext:
                        amount = levels[ks.son_level_id.name].amount_first_fee
                        kinder.update({
                            ks.son_level_id.name: {
                                'level': ks.son_level_id.name,
                                'local': 0,
                                'ext': 1,
                                'amount': amount,
                            }
                        })
                    else:
                        amount = levels[ks.son_level_id.name].amount_first_fee
                        kinder.update({
                            ks.son_level_id.name: {
                                'level': ks.son_level_id.name,
                                'local': 1,
                                'ext': 0,
                                'amount': amount,
                            }
                        })
                else:
                    amount = levels[ks.son_level_id.name].amount_first_fee
                    kinder.update({
                        ks.son_level_id.name: {
                            'level': ks.son_level_id.name,
                            'local': 1,
                            'ext': 0,
                            'amount': amount,
                        }
                    })
            else:
                if ks.scholarship_id:
                    if ks.scholarship_id.id == beca_ext:
                        kinder[ks.son_level_id.name]['ext'] = kinder[ks.son_level_id.name]['ext'] + 1
                    else:
                        kinder[ks.son_level_id.name]['local'] = kinder[ks.son_level_id.name]['local'] + 1
                else:
                    kinder[ks.son_level_id.name]['local'] = kinder[ks.son_level_id.name]['local'] + 1

        for rs in regular_students:
            if rs.son_level_id.name not in regular:
                if rs.scholarship_id:
                    if rs.scholarship_id.id == beca_ext:
                        amount = levels[rs.son_level_id.name].amount_first_fee
                        regular.update({
                            rs.son_level_id.name: {
                                'level': rs.son_level_id.name,
                                'local': 0,
                                'ext': 1,
                                'amount': amount,
                            }
                        })
                    else:
                        amount = levels[rs.son_level_id.name].amount_first_fee
                        regular.update({
                            rs.son_level_id.name: {
                                'level': rs.son_level_id.name,
                                'local': 1,
                                'ext': 0,
                                'amount': amount,
                            }
                        })
                else:
                    amount = levels[rs.son_level_id.name].amount_first_fee
                    regular.update({
                        rs.son_level_id.name: {
                            'level': rs.son_level_id.name,
                            'local': 1,
                            'ext': 0,
                            'amount': amount,
                        }
                    })
            else:
                if rs.scholarship_id:
                    if rs.scholarship_id.id == beca_ext:
                        regular[rs.son_level_id.name]['ext'] = regular[rs.son_level_id.name]['ext'] + 1
                    else:
                        regular[rs.son_level_id.name]['local'] = regular[rs.son_level_id.name]['local'] + 1
                else:
                    regular[rs.son_level_id.name]['local'] = regular[rs.son_level_id.name]['local'] + 1

        for cs in comerce_students:
            if cs.scholarship_id:
                name = cs.course_id.name + ' ' + cs.scholarship_id.name
                if name not in comerce:
                    comerce.update({
                        name: {
                            'name': cs.course_id.name,
                            'students': 1,
                            'amount': cs.regular_pension,
                        }
                    })
                else:
                    comerce[name]['students'] = comerce[name]['students'] + 1
            else:
                if cs.class_id.name not in comerce:
                    comerce.update({
                        cs.course_id.name: {
                            'name': cs.course_id.name,
                            'students': 1,
                            'amount': cs.regular_pension,
                        }
                    })
                else:
                    comerce[cs.course_id.name]['students'] = comerce[cs.course_id.name]['students'] + 1

        local_col = students.filtered(lambda x: x.scholarship_id.id == beca_loc)
        b_local = self.env['op.scholarship'].search([('id', '=', beca_loc)])
        for bl in local_col:
            if bl.son_level_id.name not in beca_local:
                amount = levels[bl.son_level_id.name].amount_first_fee
                beca_local.update({
                    bl.son_level_id.name: {
                        'level': bl.son_level_id.name,
                        'count': 1,
                        'amount': (amount * b_local.discount) / 100,
                    }
                })
            else:
                beca_local[bl.son_level_id.name]['count'] = beca_local[bl.son_level_id.name]['count'] + 1

        scholarships = self.env['op.scholarship'].search([('discount', '>', 0), ('id', '!=', beca_loc), ('id', '!=', beca_ext)], order='discount asc')
        amount = levels['1'].amount_first_fee
        for s in scholarships:
            students_s = students.filtered(lambda x: x.scholarship_id.id == s.id)
            if len(students_s) > 0:
                if s.discount not in becas:
                    discount = (amount * s.discount)/100
                    becas.update({
                        s.discount: {
                            'alumnos': len(students_s),
                            'name': s.name,
                            'amount': amount,
                            'porcentaje': s.discount,
                            'discount': discount,
                            'total': amount-discount,
                        }
                    })
        docs = 0
        prec = self.env['decimal.precision'].precision_get('Product Price')
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
            'data': data,
            'familys': total_familys,
            'comerce': total_comerce,
            'students': total_students,
            'kinder': kinder,
            'regular': regular,
            'comerce_students': comerce,
            'n_beca_local': b_local,
            'beca_local': beca_local,
            'becas': becas,
            'pension': amount,
            'prec': prec,
        }
