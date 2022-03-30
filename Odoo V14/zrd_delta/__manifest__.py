# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Modulo de Adecuaciones DELTAX',
    'version': '14.0',
    'summary': 'Modulo DELTAX',
    'author': 'Alvaro Renato Paredes Flores',
    'website': "",
    'description': """
        Modulo de adecuaciones para DELTAX
        1. Formato de factura DeltaX
        2. Transacciones de Flete 
    """,
    'category': 'Account',
    'version': '14.0',
    'depends': ['sale', 'contacts', 'account'],
    'data': [
        'data/data_delta.xml',
        'security/ir.model.access.csv',
        'security/data_security.xml',
        'views/menus.xml',
        'views/operation_transaction_view.xml',
        'views/account_move_view.xml',
        'views/product_category_view.xml',
        'views/res_company_view.xml',
        'views/res_config_view.xml',
        'wizard/edit_description_wizard.xml'
    ],
    'installable': True,
    'auto_install': False,
}