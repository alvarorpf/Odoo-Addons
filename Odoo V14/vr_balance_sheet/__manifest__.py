# -*- coding: utf-8 -*-
{
    'name': "Hoja de balance",

    'summary': """
        Periodos contables y cierre contable""",

    'description': """
        Realizar el registro de un periodo contable para el manejo contable mensual, realizar el registro de dos asientos contables
        el primero por el cierre y traspaso de cuentas de la gestion actual,el segundo por la apertura de gestion siguiente
    """,

    'author': "Alvaro Renato Paredes Flores",
    'website': "http://www.versatil.com.bo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'account_accountant', 'l10n_bo_invoice', 'activos_fijos'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_view.xml',
        'views/account_move.xml',
        'views/account_asset.xml',
        'views/account_period.xml',
        'wizard/account_closing_wizard_view.xml',
    ],
    # only loaded in demonstration mode
}
