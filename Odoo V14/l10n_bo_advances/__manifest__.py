# -*- coding: utf-8 -*-
{
    'name': "Adelantos Bolivia",

    'summary': """
        1. Asignación de adelantos a empleados
        2. Asignación de fondos
        3. Transferencias entre diarios contables""",

    'description': """
    """,

    'author': "Alvaro Renato Paredes Flores",
    'website': "https://versatil.com.bo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Expenses',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_expense', 'l10n_bo_expenses'],

    # always loaded
    'data': [
        'data/data_sequences.xml',
        'security/ir.model.access.csv',
        'views/account_payment_view.xml',
        'views/hr_expense_view.xml',
        'views/internal_transfer.xml',
        'views/internal_transfer_type.xml',
        'views/res_partner_view.xml',
        'wizard/wizard_cancel_process.xml',
        'wizard/wizard_generate_payment.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
