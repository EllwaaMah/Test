# -*- coding: utf-8 -*-
{
    'name': 'iSky Notification',
    'summary': 'iSky Notification',
    'description': """
        This module add generic notification form.
         """,
    'depends': ['base','mail'],
    'author': "iSky Development Team",
    'website': "http://www.iskydev.com",
    'data': [
        'data/notification_cron.xml',
        'security/ir.model.access.csv',
        'views/notification_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
