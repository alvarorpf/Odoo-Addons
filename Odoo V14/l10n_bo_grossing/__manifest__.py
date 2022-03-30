# -*- coding: utf-8 -*-
{
    'name': "Cálculo de Grossing Up",
    'summary': """
        Agrega la funcionalidad de cálculo de grossing up en facturas de proveedor""",
    'description': """
        Cálculo de grossing up en facturas proveedor
    """,
    'author': "Alvaro Renato Paredes Flores",
    'website': "https://versatil.com.bo",
    'category': 'Account',
    'version': '14.0',
    'depends': ['base', 'account', 'l10n_bo_invoice'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'wizard/tax_inverse_wizard.xml',
    ],
}
