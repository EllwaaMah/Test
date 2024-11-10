# © 2022 Bitsera Solutions (<http://bitsera-solutions.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'KODE HR Referrals',
    'summary': 'KODE HR Referrals',
    'description': """KODE HR Referrals""",
    'category': 'base',
    'version': '15.0.1.0.0',
    'author': "Bitsera Solutions",
    'website': "http://www.bitsera-solutions.com",
    'depends': ['hr', 'hr_contract', 'hr_recruitment'],
    'data': [
        'security/ir.model.access.csv',
        'data/employee_reward_sequence.xml',
        'data/ir_cron.xml',
        'views/referral_reward_views.xml',
        'views/hr_applicant_views.xml',
        'views/employee_referral_reward_views.xml',
        'views/menuitems.xml',
    ],
}
