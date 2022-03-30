# -*- coding: utf-8 -*-
{
    'name': "Eventos Bonabel",

    'summary': """
        Funciones esclusivas eventos""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Alvaro Renato Paredes Flores",
    'website': "http://www.poiesisconsulting.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock', 'account', 'purchase'],

    # always loaded
    'data': [
        # 'views/purchase_template_view.xml',
        'wizard/invoice_wizard_view.xml',
        'wizard/transfer_wizard_view.xml',
        'wizard/advance_wizard_view.xml',
        'views/event_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'test': [],
    'installable': True,
    'images': []
}
#ToDo:
#aumentar secuencia al evento
#Arreglar widget de imagen de evento. No guarda!
#Cambiar de nombre módulo. No depender de x_bonabel
#Agregar messaging y chat al Evento
#Aumentar boton de Facturar en cada línea del evento para ir al mismo wizard pero con ese regalo seleccionado
