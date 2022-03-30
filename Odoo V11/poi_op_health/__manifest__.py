# -*- coding: utf-8 -*-
{
    'name': 'Poi Educat Health',
    'version': '11.0.1.0.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage TimeTables',
    'complexity': "easy",
    'author': 'Alvaro Renato Paredes Flores',
    'website': 'http://www.poiesisconsulting.org',
    'depends': ['poi_x_aleman'],
    'data': [
        # Menu
        'views/menu.xml',
        # Wizard
        'wizard/op_report_sedes_wiz.xml',
        'wizard/menu_wiz.xml',

        'views/hr_employee_view.xml',
        'views/op_allergy_list_view.xml',
        'views/op_blood_group_view.xml',
        'views/op_consultation_reason_view.xml',
        'views/op_exit_authorization_view.xml',
        'views/op_clinical_record_view.xml',
        'views/op_measure_taken_view.xml',
        'views/op_medical_file_view.xml',
        'views/op_sport_view.xml',
        'views/op_vaccines_list_view.xml',
        'views/op_diseases_list_view.xml',
        'views/op_medicines_frequency_view.xml',
        'views/op_student_view.xml',
        'views/op_report_parameters_view.xml',
        'views/op_value_report_parameters_view.xml',
        'views/op_teacher_view.xml',

        'report/op_report_sedes.xml',
        'report/op_medical_file_report.xml',
        'report/op_exit_authorization_report.xml',

        'data/sequence_data.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
