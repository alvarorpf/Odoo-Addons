{
    'name': "Modulo de Reportes BISA SEGUROS Y REASEGUROS S.A. (Documentos)",

    'summary': """
       Reportes.
    """,

    'author': "Alvaro Renato Paredes Flores",
    'website': "https://www.poiesisconsulting.com",

    'category': 'reports',
    'version': '12.0.1.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'poi_x_bisaseg_doc',
        'muk_quality_docs',
    ],
    'data': [
        # Vistas
        'reports/analysis_requirements.xml',
        'reports/analysis_documents.xml',
        'reports/reader_comparison_view.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
    ],

    'demo': [
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}
