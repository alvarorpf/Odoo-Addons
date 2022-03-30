# -*- coding: utf-8 -*-
{
    'name': "Comision Bancaria",
    'summary': """
        Módulo de comision bancaria""",
    'description': """
        Comision bancaria de transacciones
    """,
    'author': "Alvaro Renato Paredes Flores",
    'website': "https://versatil.odoo.com/",
    'category': 'Localization',
    'version': '14.1',
    'depends': ['l10n_bo_invoice', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_establishment_view.xml',
        'views/pos_config_view.xml',
        'wizard/calculate_bank_commission_view.xml',
    ],
}
