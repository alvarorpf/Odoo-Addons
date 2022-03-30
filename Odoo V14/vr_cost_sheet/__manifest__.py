# -*- coding: utf-8 -*-
{
    'name': 'Reporte de Hoja de Costos',
    'version': '14.0.0.0',
    'author': 'Alvaro Renato Paredes Flores',
    'summary': '',
    'description': """Reporte Pivote de Hoja de Costos""",
    'category': 'Base',
    'website': 'http://www.versatil.com.bo',
    'license': 'AGPL-3',
    'depends': ['purchase', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_cost_sheet_view.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
