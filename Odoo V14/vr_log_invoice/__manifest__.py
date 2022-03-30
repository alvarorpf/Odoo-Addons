# -*- coding: utf-8 -*-
{
    'name': "Log de impresion de facturas",

    'summary': """
        Facturación""",

    'description': """
        Log para de impresiones de facturas originales, adicino de boton para impresion de facturas en formato de copia
    """,

    'author': "Alvaro Renato Paredes Flores",
    'website': "https://www.versatil.com.bo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Invoice',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'l10n_bo_invoice',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_log_view.xml',
        'views/account_move_view.xml',
        #'views/invoice_report.xml',
    ],
    # only loaded in demonstration mode
}
