# -*- coding: utf-8 -*-
{
    'name': 'Cotizador2',
    'version': '1',
    'summary': 'Cotizador2',
    'sequence': -101,
    'description': """Curso Python-Odoo 2022_v2""",
    'author': 'Alejandro Sartorio',
    'maintainer': 'Alejandro Sartorio_2',
    'website': 'https://www.odoomates.tech',
    'license': 'AGPL-3',
    'depends': ['base', 'website', 'sale'],
    'data': [

        'views/costos_almacenamiento.xml',
        'views/analitico.xml',
        'views/cotizador.xml',
        'views/configuracion.xml'


            ],
    'demo': [],
    'qweb': [],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
