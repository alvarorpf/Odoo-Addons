{
    'name': 'Galeria Karlovy Vary Portal Web',
    'summary': 'Portal Web',
    'description': """
* Campos Adicionales
    """,
    'version': '1.0',
    'author': "Alvaro Renato Paredes Flores",
    'category': 'Extra Tools',
    'website': "http://www.poiesisconsulting.com/",
    'depends': ['website', 'website_sale', 'website_sale_delivery', 'delivery', 'payment_libelula'],
    'data': [
        'data/email_template.xml',
        'views/event_templates.xml',
        'views/web_template.xml',
        'views/portal_view.xml',
        'views/res_config_setting_view.xml',
        'views/delivery_carrier_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'images': []
}