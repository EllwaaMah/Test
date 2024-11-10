# -*- coding: utf-8 -*-
{
    'name': 'iSky Notification',
    'summary': 'iSky Notification',
    'description': """
        This module add generic notification form.
         """,
    'depends': ['base','mail'],
    'version': '0.1',
    'author': "iSky Development Team",
    'website': "http://www.iskydev.com",
    'data': [
        #-----------data----------
        'data/notification_cron.xml',
        #---------security---------
        'security/ir.model.access.csv',
        #-----------views-----------
        'views/isky_notification_view.xml',
    ],

    'installable': True,
    'auto_install': False,
}
