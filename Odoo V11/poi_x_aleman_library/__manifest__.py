# -*- coding: utf-8 -*-
{
    'name': 'Poi Educat Library',
    'version': '11.0.1.0.0',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Manage TimeTables',
    'complexity': "easy",
    'author': 'Alvaro Renato Paredes Flores',
    'website': 'http://www.poiesisconsulting.org',
    'depends': ['poi_x_aleman', 'openeducat_library'],
    'data': [
        'data/data_sequence.xml',
        'data/data_cron_overdue.xml',
        'views/menu.xml',
        'views/op_media_view.xml',
        'views/op_cdu_code_view.xml',
        'views/op_media_unit_view.xml',
        'views/op_publisher_place_view.xml',
        'views/op_media_type_view.xml',
        'views/op_loan_term_view.xml',
        'views/op_book_loan_view.xml',
        'views/op_book_state_view.xml',
        'views/op_media_unit_state_view.xml',
        'views/op_media_unit_history_view.xml',
        'views/op_publisher_view.xml',
        'views/op_author_view.xml',
        'views/op_student_view.xml',
        'views/op_teacher_view.xml',
        'views/op_subtype.xml',
        'wizard/create_unit_view.xml',
        'wizard/return_book_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
