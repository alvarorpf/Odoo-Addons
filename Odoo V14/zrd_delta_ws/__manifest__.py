# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Modulo de Servicios Web DELTAX',
    'version': '14.0',
    'summary': 'Modulo DELTAX',
    'author': 'Alvaro Renato Paredes Flores',
    'website': "",
    'description': """
        Modulo de servicios web para DELTAX
        1. Servicio web para registro de operaciones 
        2. Servicio web para registro de ventas
        3. Sedrvicio web para registro de compras 
    """,
    'category': '',
    'version': '14.0',
    'depends': ['zrd_delta'],
    'data': [
        'views/operation_transaction_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}