# © 2022 Bitsera Solutions (<http://bitsera-solutions.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'KODE HR Recruitment Requisition',
    'summary': 'KODE HR Recruitment Requisition',
    'description': """KODE HR Recruitment Requisition""",
    'category': 'base',
    'version': '15.0.1.0.0',
    'author': "Bitsera Solutions",
    'website': "http://www.bitsera-solutions.com",
    'depends': ['hr', 'hr_contract', 'hr_recruitment', 'kode_employee'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/recruitment_requisition_seqs.xml',
        'views/recruitment_requisition_views.xml',
        'views/hr_job_views.xml',
    ],
}
