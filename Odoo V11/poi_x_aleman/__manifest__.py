# -*- coding: utf-8 -*-
{
    'name': 'Poi Education',
    'version': '11.0.1.0.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Adecuaciones Colegio Aleman',
    'complexity': "easy",
    'author': 'Alvaro renato Paredes Flores',
    'website': 'http://www.poiesisconsulting.com',
    'depends': ['openeducat_core', 'account', 'account_asset', 'poi_bol_asset',
                'openeducat_library',
                'openeducat_support',
                'web_openeducat',
                'website', 'product', 'poi_bol_base',
                'stock',
                'poi_bol_cc',
                'qweb_usertime',
                ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/web_template.xml',
        'views/account_view.xml',
        'views/account_charge.xml',
        'views/account_asset_view.xml',
        'views/op_school_period.xml',
        'views/op_scholarship.xml',
        'views/account_op_charge_level.xml',
        'views/request_charge.xml',
        'views/op_request_import.xml',
        'views/menu.xml',

        'views/op_class_view.xml',
        'views/op_course_view.xml',
        'views/op_family_view.xml',
        'views/op_family_tag_view.xml',
        'views/op_matter_view.xml',
        'views/op_matter_type_view.xml',
        'views/op_parent_view.xml',
        'views/op_profession_view.xml',
        'views/op_relationship_view.xml',
        'views/op_religion_view.xml',
        'views/op_student_view.xml',
        'views/op_student_case_view.xml',
        'views/op_teacher_classification_view.xml',
        'views/op_teacher_view.xml',
        'views/op_type_view.xml',
        'views/op_course_level_view.xml',
        'views/op_grade_view.xml',
        'views/op_parallel_view.xml',
        'views/op_priority_view.xml',
        'views/op_year_view.xml',
        'views/op_month_view.xml',
        'views/op_course_history_view.xml',
        'views/product.xml',
        'views/account_payment.xml',
        'views/res_partner.xml',
        'report/report_mora_2.xml',
        # Vistas Web
        # 'views/op_web_family_view.xml',

        # wizard
        'wizard/account_charge_generator.xml',
        'wizard/account_charge_payment.xml',
        'wizard/op_period_open.xml',
        'wizard/op_activate_period.xml',
        'wizard/op_student_change_status.xml',
        'wizard/op_force_level.xml',
        'wizard/menu_wiz.xml',
        'wizard/op_scholarship_discount.xml',
        'wizard/op_potential_income.xml',
        'wizard/report_mora_wiz.xml',
        'wizard/report_account_wiz.xml',
        #'wizard/closing_account.xml',
        'wizard/report_export.xml',
        'wizard/op_cancel_charge.xml',
        'wizard/general_ledger_aleman.xml',
        'wizard/statement_income_aleman.xml',
        # data
        'data/data_utility.xml',
        # 'data/data_course_level.xml',
        'data/data_batch_grades.xml',
        'data/data_batch_parallels.xml',
        # 'data/data_batch.xml',
        'data/data_student.xml',
        'data/data_charges.xml',
        'data/data_account_op_charge_level.xml',
        'data/ir_sequence_data.xml',
        # 'data/data_cron_edades.xml',
        'data/data_scholarship.xml',
        'data/data_comercio.xml',
        'data/data_sequence.xml',
        'data/data_charges_comercio.xml',
        # 'data/data_cron_prepaid.xml',

        # report
        'report/account_move.xml',
        'report/invoice_base.xml',
        'report/basic_invoice.xml',
        'report/potential_income_report.xml',
        'report/report_mora.xml',
        'report/report_account.xml',
        'report/report_account_2.xml',
        'report/class_list.xml',

        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}