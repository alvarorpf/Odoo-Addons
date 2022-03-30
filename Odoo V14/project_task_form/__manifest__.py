# -*- coding: utf-8 -*-
{
    'name': "Formularios por Tareas",

    'summary': """
        * Encuestas por Tareas 
        """,

    'description': """
        Formularios por Tareas
    """,

    'author': "Alvaro Renato Paredes Flores",
    'website': "http://www.giraffos.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'project',
    ],
    # always loaded
    'data': [
        'data/data_task_form.xml',
        'security/ir.model.access.csv',
        'security/security_data.xml',
        'views/forms_menu_view.xml',
        'views/project_task_view.xml',
        'views/initial_investigation_view.xml',
        'views/investigation_report_view.xml',
        'views/visit_form_view.xml',
        'views/security_inspection_view.xml',
        'views/election_form_view.xml',
        'views/observation_form_view.xml',
        'report/initial_investigation_report.xml',
        'report/investigation_report.xml',
        'report/visit_form_report.xml',
        'report/security_inspection_report.xml',
        'report/election_form_report.xml',
        'report/observation_form_report.xml',
        'report/task_form_report.xml',
        'wizard/add_forms_view.xml',
    ],
}