# -*- coding: utf-8 -*-
{
    'name': "Actualizar Fecha de Ventas",
    'summary': """
       Inventario 
    """,
    'description': """
        Aplicacion para actualizacion de fechas para igualar valores tanto de facturas como de movimientos de inventario
    """,
    'author': "Alvaro Renato Paredes Flores",
    'website': "https://www.versatil.com.bo",
    'category': 'Inventory',
    'version': '0.1',
    'depends': ['sale', 'stock', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/update_dates_wizard.xml',
    ],
}
