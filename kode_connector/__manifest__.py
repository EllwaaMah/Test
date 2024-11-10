# -*- coding: utf-8 -*-
# © 2021 DGTera systems (<http://www.dgtera.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Kode 34ml Connector',
    'category': 'base',
    'summary': 'Kode Connector',
    'version': '15.0.1.0.0',
    'author': "Bitsera Solutions",
    'website': "http://www.bitsera-solutions.com",
    'depends': ['contacts'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/kode_connector_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}