# © 2022 Bitsera Solutions (<http://bitsera-solutions.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'KODE Contacts',
    'summary': 'KODE Contacts',
    'description': """KODE Contacts""",
    'category': 'base',
    'version': '14.0.1.0.0',
    'author': "Bitsera Solutions",
    'website': "http://www.bitsera-solutions.com",
    'depends': ['contacts', 'base_address_city', 'sms', 'crm'],
    'data': [
        'data/data.xml',
        'views/res_partner.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1,
}
