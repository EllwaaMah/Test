{
    "name": "Record Creation Survey",
    "summary": """
        Record Creation Survey scaffold module
        """,
    "category": "",
    "version": "14.0.1.0.2",
    "author": "Odoo PS",
    "website": "http://www.odoo.com",
    "license": "OEEL-1",
    "depends": [
        'crm', 'survey', 'membership_sequence', 'mail'
    ],
    "data": [
        "views/crm_lead_views.xml",
        "views/res_config_settings.xml",
        "views/survey_survey_views.xml",
        "views/res_partner_views.xml",
    ],
    'assets': {
        'survey.survey_assets': [
            'record_creation_survey/static/src/scss/survey_form.scss',
        ],
    },
    # Only used to link to the analysis / Ps-tech store
    "task_id": [2649479],
}
