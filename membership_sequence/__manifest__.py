# -*- coding: utf-8 -*-
{
    'name': "membership_sequence",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Odoo-ps",
    'website': "http://www.odoo.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'sale_subscription'],
    'data': [
        'data/sequence.xml',
        'views/views.xml',
    ],
}
