# -*- coding: utf-8 -*-
{
    'name': "Survey Export Result in Excel",

    'summary': """
        This modules allows you to export of survey result into excel file.
    """,
    'version': '15.0.1.0.0',
    'description': """
        This modules allows you to export of survey result into excel file.
    """,
    'author': "Ansitek",
    'website': "info.ansitek@gmail.com",
    'category': 'Surveys',

    # any module necessary for this one to work correctly
    'depends': ['survey'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/export_survey_result_wizard_view.xml',
        'wizard/file_download_wizard_view.xml',
        'views/survey_survey_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    "external_dependencies": {
        "python": ["xlsxwriter"]
    },
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'price': 30.00,
    'currency': 'USD',
    'live_test_url': '',
    'installable': True,
    'auto_install': False,
    'application': False,
}
