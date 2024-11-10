# © 2022 Bitsera Solutions (<http://bitsera-solutions.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'KODE HR Employee',
    'summary': 'KODE HR Employee',
    'description': """KODE HR Employee""",
    'category': 'base',
    'version': '15.0.1.0.0',
    'author': "Bitsera Solutions",
    'website': "http://www.bitsera-solutions.com",
    'depends': ['hr', 'hr_contract', 'survey', 'hr_recruitment', 'documents'],

    'data': [
        'security/ir.model.access.csv',
        'data/employee_sequence.xml',
        'wizard/send_survey_view.xml',
        'views/disciplinary_cases_history_view.xml',
        'views/position_grade_view.xml',
        'views/career_progression_views.xml',
        'views/servey_inherit_view.xml',
        'views/hr_employee_view_inherit.xml',
        'views/employee_actions.xml',
        'views/menuitems.xml',
    ],
}
